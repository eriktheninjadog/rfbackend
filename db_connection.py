"""
Centralized database connection management.

This module provides a singleton class to manage database connections
across the application, supporting both MySQL connector and SQLAlchemy.
"""

import mysql.connector
from mysql.connector import pooling
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.ext.automap import automap_base
from sqlalchemy import MetaData
import threading


class DatabaseConnection:
    """
    Singleton class to manage database connections with connection pooling.
    
    This class provides centralized management of database connections,
    supporting both raw MySQL connections and SQLAlchemy sessions.
    """
    
    _instance = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(DatabaseConnection, cls).__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize the database connection manager."""
        if self._initialized:
            return
            
        # Default configuration
        self.host = "localhost"
        self.user = "erik"
        self.password = "ninjadogs"
        self.database = "language"
        
        # Connection pool for MySQL connector
        self._connection_pool = None
        
        # SQLAlchemy components
        self._engine = None
        self._session_factory = None
        self._base = None
        self._metadata = None
        
        self._initialized = True
    
    def configure(self, host=None, user=None, password=None, database=None):
        """
        Configure database connection parameters.
        
        Args:
            host (str): Database host
            user (str): Database user
            password (str): Database password
            database (str): Database name
        """
        if host:
            self.host = host
        if user:
            self.user = user
        if password:
            self.password = password
        if database:
            self.database = database
        
        # Reset pools and connections when configuration changes
        self._connection_pool = None
        self._engine = None
        self._session_factory = None
    
    def _get_connection_pool(self):
        """
        Get or create the MySQL connection pool.
        
        Returns:
            mysql.connector.pooling.MySQLConnectionPool: Connection pool
        """
        if self._connection_pool is None:
            self._connection_pool = pooling.MySQLConnectionPool(
                pool_name="main_pool",
                pool_size=5,
                pool_reset_session=True,
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
        return self._connection_pool
    
    def get_connection(self):
        """
        Get a MySQL connection from the pool.
        
        Returns:
            mysql.connector.connection.MySQLConnection: Database connection
            
        Note:
            The caller is responsible for closing the connection when done.
        """
        pool = self._get_connection_pool()
        return pool.get_connection()
    
    def get_engine(self):
        """
        Get or create the SQLAlchemy engine.
        
        Returns:
            sqlalchemy.engine.Engine: SQLAlchemy engine
        """
        if self._engine is None:
            connection_string = f'mysql://{self.user}:{self.password}@{self.host}/{self.database}'
            self._engine = create_engine(
                connection_string,
                pool_recycle=60 * 5,
                pool_pre_ping=True
            )
        return self._engine
    
    def get_session(self):
        """
        Get a new SQLAlchemy session.
        
        Returns:
            sqlalchemy.orm.Session: New database session
            
        Note:
            The caller is responsible for closing the session when done.
        """
        if self._session_factory is None:
            engine = self.get_engine()
            self._session_factory = sessionmaker(bind=engine)
        return self._session_factory()
    
    def get_base(self):
        """
        Get or create the SQLAlchemy automap base.
        
        Returns:
            sqlalchemy.ext.automap.AutomapBase: Automap base with reflected tables
        """
        if self._base is None:
            engine = self.get_engine()
            self._base = automap_base()
            self._base.prepare(autoload_with=engine)
        return self._base
    
    def get_metadata(self):
        """
        Get or create the SQLAlchemy metadata.
        
        Returns:
            sqlalchemy.MetaData: Metadata with reflected schema
        """
        if self._metadata is None:
            engine = self.get_engine()
            self._metadata = MetaData()
            self._metadata.reflect(bind=engine)
        return self._metadata
    
    def close_all(self):
        """
        Close all connections and dispose of resources.
        
        This should be called when shutting down the application.
        """
        if self._engine:
            self._engine.dispose()
            self._engine = None
        
        self._connection_pool = None
        self._session_factory = None
        self._base = None
        self._metadata = None


# Global singleton instance
_db = DatabaseConnection()


def get_db_connection():
    """
    Get the global DatabaseConnection instance.
    
    Returns:
        DatabaseConnection: Singleton database connection manager
    """
    return _db


def get_connection():
    """
    Get a MySQL connection from the pool (backward compatible).
    
    Returns:
        mysql.connector.connection.MySQLConnection: Database connection
    """
    return _db.get_connection()
