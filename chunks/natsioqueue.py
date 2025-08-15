import asyncio
import os
from nats.aio.client import Client as NATS

from nats.aio.client import Client as NATS
from nats.aio.errors import ErrConnectionClosed, ErrTimeout
import threading


async def run_nats_listener():
    # Configuration (use environment variables in production)
    config = {
        "servers": ["nats://chinese.eriktamm.com:4222"],  # Your server URLs
        "user": os.getenv("NATS_USER", None),     # Optional username
        "password": os.getenv("NATS_PASSWORD", None),  # Optional password
        "subject": "example.subject",             # Subject to subscribe to
        "queue": "my-worker-group"                # Queue group (optional)
    }

    nc = NATS()
    
    async def disconnected_cb():
        print("Connection to NATS lost!")

    async def reconnected_cb():
        print("Reconnected to NATS")

    # Message handler (process incoming messages)
    async def message_handler(msg):
        subject = msg.subject
        data = msg.data.decode()
        print(f"Received message [{subject}]: {data}")
        # Process message here - may respond with msg.respond()
        # Example: await msg.respond(b"Ack")

    try:
        # Connect to NATS with authentication
        await nc.connect(
            servers=config["servers"],
            user=config["user"],
            password=config["password"],
        )
        print(f"Connected to NATS at {nc.connected_url.netloc}")

        # Subscribe to subject with optional queue group
        sub = await nc.subscribe(
            subject=config["subject"],
            cb=message_handler,
            queue=config["queue"]
        )
        print(f"Listening on [{config['subject']}] in queue '{config['queue']}'...")

        # Handle graceful shutdown (Ctrl+C)
        while True:
            await asyncio.sleep(1)

    except (ErrConnectionClosed, ErrTimeout) as e:
        print(f"Connection error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        # Gracefully close connection
        await nc.drain()
        print("Connection closed")



async def publish_message():
    # Create a NATS client instance
    nc = NATS()

    try:
        user = os.getenv("NATS_USER")
        password = os.getenv("NATS_PASSWORD")
    
        # Connect to a remote NATS server (replace with your server address)
        await nc.connect(servers=["nats://chinese.eriktamm.com:4222"],
                         user=user,
            password=password)

        # Define the subject (queue) and message
        subject = "example.subject"
        message = b"Hello from Python!"

        # Publish the message
        await nc.publish(subject, message)
        print(f"Published message to '{subject}': {message.decode()}")

    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        # Gracefully close the connection
        await nc.close()
        
def start_nats_listener_thread():
    """
    Start a new thread that runs the NATS listener.
    Returns the thread object which can be used to manage the thread.
    """
    thread = threading.Thread(
        target=lambda: asyncio.run(run_nats_listener()),
        daemon=True  # Make the thread exit when the main program exits
    )
    thread.start()
    return thread


import time
# Run the asynchronous function
if __name__ == "__main__":
    
    start_nats_listener_thread()    
    time.sleep(5)  # Give the listener some time to start
    for i in range(5):
        asyncio.run(publish_message())
        time.sleep(10)  # Wait before sending the next message