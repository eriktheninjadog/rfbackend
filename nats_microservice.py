# nats_microservice.py

import os
import json
import threading
import logging
import asyncio
import socket
import platform
from typing import Any, Dict, Callable, Optional, List, Union
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import functools
import time
from concurrent.futures import ThreadPoolExecutor
import uuid

import nats
from nats.errors import ConnectionClosedError, TimeoutError as NatsTimeoutError

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceStatus(Enum):
    """Enumeration for service status"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    STARTING = "starting"
    STOPPING = "stopping"


class ResultStrategy(Enum):
    """Enumeration for result handling strategies"""
    NO_RESPONSE = "no_response"  # Fire and forget
    DIRECT_REPLY = "direct_reply"  # Reply directly to sender
    PUBLISH_RESULT = "publish_result"  # Publish result to a specific topic
    CALLBACK = "callback"  # Use a callback function


@dataclass
class ServiceInfo:
    """Data class for service information"""
    service_id: str
    service_name: str
    hostname: str
    platform: str
    status: ServiceStatus
    timestamp: str
    metadata: Dict[str, Any] = None


@dataclass
class TaskResult:
    """Data class for task results"""
    task_id: str
    service_id: str
    success: bool
    result: Any = None
    error: str = None
    timestamp: str = None


class NatsMicroservice:
    """
    A comprehensive NATS-based microservice framework
    """
    
    def __init__(
        self,
        service_name: str,
        service_id: Optional[str] = None,
        nats_url: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        max_reconnect_attempts: int = 5,
        reconnect_time_wait: int = 2
    ):
        """
        Initialize the NATS microservice
        
        Args:
            service_name: Name of the microservice
            service_id: Unique identifier for this service instance
            nats_url: NATS server URL (can be overridden by env var)
            username: NATS username (can be overridden by env var)
            password: NATS password (can be overridden by env var)
            max_reconnect_attempts: Maximum reconnection attempts
            reconnect_time_wait: Wait time between reconnection attempts
        """
        self.service_name = service_name
        self.service_id = service_id or f"{service_name}_{uuid.uuid4().hex[:8]}"
        
        # Get connection parameters from environment or arguments
        self.nats_url = nats_url or os.getenv('NATS_URL', '')
        self.username = username or os.getenv('NATS_USER', '')
        self.password = password or os.getenv('NATS_PASSWORD', '')
        
        # Connection settings
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_time_wait = reconnect_time_wait
        
        # State management
        self.nc = None
        self.loop = None
        self.subscriptions = {}
        self.handlers = {}
        self.status = ServiceStatus.STARTING
        self.running = False
        self.executor = ThreadPoolExecutor(max_workers=10)
        
        # Service info
        self.hostname = socket.gethostname()
        self.platform_info = platform.platform()
        
        # Callback storage for async operations
        self.pending_callbacks = {}
        
        logger.info(f"Initialized service: {self.service_name} ({self.service_id})")
    
    async def _connect(self):
        """Establish connection to NATS server"""
        try:
            options = {
                "servers": [self.nats_url],
                "max_reconnect_attempts": self.max_reconnect_attempts,
                "reconnect_time_wait": self.reconnect_time_wait,
                "disconnected_cb": self._disconnected_cb,
                "reconnected_cb": self._reconnected_cb,
                "error_cb": self._error_cb,
                "closed_cb": self._closed_cb,
            }
            
            # Add authentication if provided
            if self.username and self.password:
                options["user"] = self.username
                options["password"] = self.password
            
            self.nc = await nats.connect(**options)
            logger.info(f"Connected to NATS server at {self.nats_url}")
            self.status = ServiceStatus.HEALTHY
            
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            self.status = ServiceStatus.UNHEALTHY
            raise
    
    async def _disconnected_cb(self):
        """Callback for disconnection events"""
        logger.warning("Disconnected from NATS server")
        self.status = ServiceStatus.DEGRADED
    
    async def _reconnected_cb(self):
        """Callback for reconnection events"""
        logger.info("Reconnected to NATS server")
        self.status = ServiceStatus.HEALTHY
    
    async def _error_cb(self, e):
        """Callback for error events"""
        logger.error(f"NATS error: {e}")
    
    async def _closed_cb(self):
        """Callback for connection closed events"""
        logger.info("NATS connection closed")
        self.status = ServiceStatus.UNHEALTHY
    
    def start(self):
        """Start the microservice in a separate thread"""
        if self.running:
            logger.warning("Service is already running")
            return
        
        self.running = True
        thread = threading.Thread(target=self._run_event_loop, daemon=True)
        thread.start()
        
        # Wait for connection to be established
        time.sleep(1)
        
        # Register for service discovery
        self._register_service_discovery()
    
    def _run_event_loop(self):
        """Run the async event loop in a thread"""
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        
        try:
            self.loop.run_until_complete(self._connect())
            self.loop.run_until_complete(self._run())
        except Exception as e:
            logger.error(f"Event loop error: {e}")
        finally:
            self.loop.close()
    
    async def _run(self):
        """Main run loop"""
        while self.running:
            await asyncio.sleep(0.1)
    
    def stop(self):
        """Stop the microservice"""
        logger.info(f"Stopping service {self.service_name}")
        self.status = ServiceStatus.STOPPING
        self.running = False
        
        if self.nc and not self.nc.is_closed:
            asyncio.run_coroutine_threadsafe(self.nc.close(), self.loop)
        
        self.executor.shutdown(wait=True)
        self.status = ServiceStatus.UNHEALTHY
    
    def _register_service_discovery(self):
        """Register handlers for service discovery"""
        self.subscribe(
            "service.discovery.ping",
            self._handle_discovery_ping,
            result_strategy=ResultStrategy.DIRECT_REPLY
        )
    
    async def _handle_discovery_ping(self, message: Dict[str, Any]) -> ServiceInfo:
        """Handle service discovery ping requests"""
        return ServiceInfo(
            service_id=self.service_id,
            service_name=self.service_name,
            hostname=self.hostname,
            platform=self.platform_info,
            status=self.status,
            timestamp=datetime.utcnow().isoformat(),
            metadata=message.get("metadata", {})
        )
    
    def publish(
        self,
        subject: str,
        data: Any,
        reply_subject: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> Optional[Any]:
        """
        Publish a message to a subject
        
        Args:
            subject: NATS subject to publish to
            data: Python object to send (will be JSON serialized)
            reply_subject: Optional reply subject for request-reply pattern
            timeout: Optional timeout for request-reply pattern
            
        Returns:
            Response data if reply_subject is provided, None otherwise
        """
        if not self.nc or self.nc.is_closed:
            logger.error("Not connected to NATS server")
            return None
        
        try:
            # Serialize data to JSON
            if isinstance(data, (ServiceInfo, TaskResult)):
                json_data = json.dumps(asdict(data)).encode()
            else:
                json_data = json.dumps(data).encode()
            
            # If reply subject is provided, use request-reply pattern
            if reply_subject or timeout:
                future = asyncio.run_coroutine_threadsafe(
                    self.nc.request(subject, json_data, timeout=timeout or 5.0),
                    self.loop
                )
                response = future.result(timeout=(timeout or 5.0) + 1)
                return json.loads(response.data.decode())
            else:
                # Fire and forget
                future = asyncio.run_coroutine_threadsafe(
                    self.nc.publish(subject, json_data),
                    self.loop
                )
                future.result(timeout=5.0)
                return None
                
        except Exception as e:
            logger.error(f"Failed to publish message: {e}")
            return None
    
    def subscribe(
        self,
        subject: str,
        handler: Callable,
        queue: Optional[str] = None,
        result_strategy: ResultStrategy = ResultStrategy.NO_RESPONSE,
        result_subject: Optional[str] = None
    ):
        """
        Subscribe to a subject with a handler
        
        Args:
            subject: NATS subject to subscribe to
            handler: Function to handle received messages
            queue: Optional queue group for load balancing
            result_strategy: How to handle results from the handler
            result_subject: Subject to publish results to (if using PUBLISH_RESULT strategy)
        """
        if not self.nc or self.nc.is_closed:
            logger.error("Not connected to NATS server")
            return
        
        async def message_handler(msg):
            """Internal message handler wrapper"""
            try:
                # Deserialize JSON data
                data = json.loads(msg.data.decode())
                
                # Generate task ID for tracking
                task_id = str(uuid.uuid4())
                
                # Execute handler
                try:
                    # Check if handler is async
                    if asyncio.iscoroutinefunction(handler):
                        result = await handler(data)
                    else:
                        # Run sync handler in executor
                        result = await self.loop.run_in_executor(
                            self.executor,
                            handler,
                            data
                        )
                    
                    # Handle result based on strategy
                    await self._handle_result(
                        msg,
                        task_id,
                        True,
                        result,
                        None,
                        result_strategy,
                        result_subject
                    )
                    
                except Exception as e:
                    logger.error(f"Handler error for {subject}: {e}")
                    await self._handle_result(
                        msg,
                        task_id,
                        False,
                        None,
                        str(e),
                        result_strategy,
                        result_subject
                    )
                    
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON: {e}")
            except Exception as e:
                logger.error(f"Unexpected error in message handler: {e}")
        
        # Subscribe to the subject
        future = asyncio.run_coroutine_threadsafe(
            self.nc.subscribe(subject, queue=queue, cb=message_handler),
            self.loop
        )
        
        sub = future.result(timeout=5.0)
        self.subscriptions[subject] = sub
        self.handlers[subject] = handler
        
        logger.info(f"Subscribed to {subject}" + (f" with queue {queue}" if queue else ""))
    
    async def _handle_result(
        self,
        msg,
        task_id: str,
        success: bool,
        result: Any,
        error: Optional[str],
        strategy: ResultStrategy,
        result_subject: Optional[str]
    ):
        """Handle task results based on the specified strategy"""
        
        task_result = TaskResult(
            task_id=task_id,
            service_id=self.service_id,
            success=success,
            result=result,
            error=error,
            timestamp=datetime.utcnow().isoformat()
        )
        
        if strategy == ResultStrategy.NO_RESPONSE:
            # Do nothing
            pass
            
        elif strategy == ResultStrategy.DIRECT_REPLY:
            # Reply directly to the sender if reply subject exists
            if msg.reply:
                response_data = json.dumps(asdict(task_result)).encode()
                await self.nc.publish(msg.reply, response_data)
                
        elif strategy == ResultStrategy.PUBLISH_RESULT:
            # Publish result to a specific subject
            if result_subject:
                response_data = json.dumps(asdict(task_result)).encode()
                await self.nc.publish(result_subject, response_data)
                
        elif strategy == ResultStrategy.CALLBACK:
            # Execute callback if registered
            if task_id in self.pending_callbacks:
                callback = self.pending_callbacks.pop(task_id)
                await self.loop.run_in_executor(
                    self.executor,
                    callback,
                    task_result
                )
    
    def unsubscribe(self, subject: str):
        """Unsubscribe from a subject"""
        if subject in self.subscriptions:
            sub = self.subscriptions[subject]
            future = asyncio.run_coroutine_threadsafe(
                sub.unsubscribe(),
                self.loop
            )
            future.result(timeout=5.0)
            del self.subscriptions[subject]
            del self.handlers[subject]
            logger.info(f"Unsubscribed from {subject}")
    
    def discover_services(self, timeout: float = 2.0) -> List[ServiceInfo]:
        """
        Discover all available services
        
        Args:
            timeout: Timeout for discovery requests
            
        Returns:
            List of ServiceInfo objects for discovered services
        """
        services = []
        
        # Create a temporary inbox for responses
        inbox = f"_INBOX.{uuid.uuid4().hex}"
        
        # Subscribe to the inbox
        responses = []
        
        async def collect_responses(msg):
            try:
                data = json.loads(msg.data.decode())
                responses.append(ServiceInfo(**data))
            except Exception as e:
                logger.error(f"Error collecting discovery response: {e}")
        
        # Subscribe and publish discovery ping
        try:
            future = asyncio.run_coroutine_threadsafe(
                self.nc.subscribe(inbox, cb=collect_responses),
                self.loop
            )
            sub = future.result(timeout=1.0)
            
            # Publish discovery ping
            self.publish(
                "service.discovery.ping",
                {"metadata": {"requester": self.service_id}},
                reply_subject=inbox
            )
            
            # Wait for responses
            time.sleep(timeout)
            
            # Unsubscribe from inbox
            asyncio.run_coroutine_threadsafe(
                sub.unsubscribe(),
                self.loop
            ).result(timeout=1.0)
            
            services = responses
            
        except Exception as e:
            logger.error(f"Error during service discovery: {e}")
        
        return services
    
    def request_reply(
        self,
        subject: str,
        data: Any,
        timeout: float = 5.0
    ) -> Optional[Any]:
        """
        Send a request and wait for a reply
        
        Args:
            subject: NATS subject to send request to
            data: Request data
            timeout: Timeout for waiting for reply
            
        Returns:
            Reply data or None if timeout
        """
        return self.publish(subject, data, reply_subject=True, timeout=timeout)
    
    def publish_task(
        self,
        subject: str,
        data: Any,
        callback: Optional[Callable[[TaskResult], None]] = None,
        result_subject: Optional[str] = None,
        timeout: Optional[float] = None
    ) -> str:
        """
        Publish a task and optionally register a callback for the result
        
        Args:
            subject: NATS subject to publish task to
            data: Task data
            callback: Optional callback function for handling results
            result_subject: Optional subject to listen for results
            timeout: Optional timeout for the task
            
        Returns:
            Task ID for tracking
        """
        task_id = str(uuid.uuid4())
        
        # Add task ID to the data
        task_data = {
            "task_id": task_id,
            "data": data,
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Register callback if provided
        if callback:
            self.pending_callbacks[task_id] = callback
            
            # If result subject is provided, subscribe to it
            if result_subject:
                async def result_handler(msg):
                    try:
                        result_data = json.loads(msg.data.decode())
                        task_result = TaskResult(**result_data)
                        
                        if task_result.task_id == task_id:
                            if task_id in self.pending_callbacks:
                                cb = self.pending_callbacks.pop(task_id)
                                await self.loop.run_in_executor(
                                    self.executor,
                                    cb,
                                    task_result
                                )
                    except Exception as e:
                        logger.error(f"Error handling task result: {e}")
                
                # Subscribe to result subject
                asyncio.run_coroutine_threadsafe(
                    self.nc.subscribe(result_subject, cb=result_handler),
                    self.loop
                ).result(timeout=1.0)
        
        # Publish the task
        self.publish(subject, task_data)
        
        return task_id
    
    def get_status(self) -> ServiceInfo:
        """Get current service status information"""
        return ServiceInfo(
            service_id=self.service_id,
            service_name=self.service_name,
            hostname=self.hostname,
            platform=self.platform_info,
            status=self.status,
            timestamp=datetime.utcnow().isoformat(),
            metadata={
                "subscriptions": list(self.subscriptions.keys()),
                "pending_callbacks": len(self.pending_callbacks)
            }
        )


class MicroserviceWorker:
    """
    A helper class to easily create microservice workers
    """
    
    def __init__(
        self,
        service_name: str,
        task_handlers: Dict[str, Callable],
        result_strategy: ResultStrategy = ResultStrategy.DIRECT_REPLY,
        **kwargs
    ):
        """
        Initialize a microservice worker
        
        Args:
            service_name: Name of the service
            task_handlers: Dictionary mapping subjects to handler functions
            result_strategy: Default result handling strategy
            **kwargs: Additional arguments for NatsMicroservice
        """
        self.service = NatsMicroservice(service_name, **kwargs)
        self.task_handlers = task_handlers
        self.result_strategy = result_strategy
        
    def start(self):
        """Start the worker and register all handlers"""
        self.service.start()
        
        # Register all task handlers
        for subject, handler in self.task_handlers.items():
            self.service.subscribe(
                subject,
                handler,
                queue=self.service.service_name,  # Use service name as queue group
                result_strategy=self.result_strategy
            )
        
        logger.info(f"Worker {self.service.service_name} started with {len(self.task_handlers)} handlers")
    
    def stop(self):
        """Stop the worker"""
        self.service.stop()
    
    def run_forever(self):
        """Run the worker until interrupted"""
        self.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down worker...")
            self.stop()


# Example usage decorator for creating microservice handlers
def microservice_handler(subject: str, result_strategy: ResultStrategy = ResultStrategy.DIRECT_REPLY):
    """
    Decorator for marking functions as microservice handlers
    
    Args:
        subject: NATS subject to listen on
        result_strategy: How to handle the result
    """
    def decorator(func):
        func._microservice_subject = subject
        func._result_strategy = result_strategy
        return func
    return decorator


class MicroserviceApp:
    """
    A decorator-based microservice application framework
    """
    
    def __init__(self, service_name: str, **kwargs):
        """
        Initialize a microservice application
        
        Args:
            service_name: Name of the service
            **kwargs: Additional arguments for NatsMicroservice
        """
        self.service_name = service_name
        self.service = NatsMicroservice(service_name, **kwargs)
        self.handlers = {}
        
    def task(self, subject: str, result_strategy: ResultStrategy = ResultStrategy.DIRECT_REPLY):
        """
        Decorator for registering task handlers
        
        Args:
            subject: NATS subject to listen on
            result_strategy: How to handle the result
        """
        def decorator(func):
            self.handlers[subject] = (func, result_strategy)
            return func
        return decorator
    
    def startup(self, func):
        """Decorator for startup hook"""
        self._startup_hook = func
        return func
    
    def shutdown(self, func):
        """Decorator for shutdown hook"""
        self._shutdown_hook = func
        return func
    
    def run(self):
        """Run the microservice application"""
        # Start the service
        self.service.start()
        
        # Run startup hook if defined
        if hasattr(self, '_startup_hook'):
            self._startup_hook()
        
        # Register all handlers
        for subject, (handler, strategy) in self.handlers.items():
            self.service.subscribe(
                subject,
                handler,
                queue=self.service_name,
                result_strategy=strategy
            )
        
        logger.info(f"Microservice {self.service_name} started with {len(self.handlers)} handlers")
        
        try:
            # Run forever
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Shutting down microservice...")
            
            # Run shutdown hook if defined
            if hasattr(self, '_shutdown_hook'):
                self._shutdown_hook()
            
            self.service.stop()


# Convenience functions for quick setup
def create_publisher(service_name: str = "publisher", **kwargs) -> NatsMicroservice:
    """Create a simple publisher service"""
    service = NatsMicroservice(service_name, **kwargs)
    service.start()
    return service


def create_subscriber(
    service_name: str,
    subject: str,
    handler: Callable,
    **kwargs
) -> NatsMicroservice:
    """Create a simple subscriber service"""
    service = NatsMicroservice(service_name, **kwargs)
    service.start()
    service.subscribe(subject, handler, queue=service_name)
    return service
