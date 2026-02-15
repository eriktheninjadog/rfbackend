# Database Connection Refactoring

## Overview

This document describes the database connection refactoring that centralizes all database connection handling into a single class.

## Problem Statement

Previously, database connections were scattered throughout the codebase:

1. **database.py**: Had hardcoded connection details (`get_connection()` function)
2. **audioimport.py**: Had its own `get_db_connection()` with hardcoded credentials
3. **stockmanager.py**: Took connection parameters and created its own connections
4. **Multiple files**: Used `database.get_connection()` which created new connections each time

### Issues with Previous Approach

- **Hardcoded credentials** in multiple locations
- **No connection pooling** - connections were created and destroyed repeatedly
- **Mixed patterns** - Some files used raw MySQL connector, others used SQLAlchemy
- **Difficult to configure** - Changing database settings required editing multiple files
- **Resource inefficient** - Opening/closing connections is expensive

## Solution: DatabaseConnection Class

A new `db_connection.py` module provides a singleton `DatabaseConnection` class that:

1. **Centralizes configuration** - One place to manage database settings
2. **Implements connection pooling** - Reuses connections for better performance
3. **Supports both MySQL and SQLAlchemy** - Provides methods for both use cases
4. **Maintains backward compatibility** - Existing code continues to work
5. **Thread-safe** - Uses locking for thread safety

## Architecture

### New File: `db_connection.py`

```python
from db_connection import get_db_connection, get_connection

# Get the singleton instance
db = get_db_connection()

# Get a pooled MySQL connection
conn = db.get_connection()

# Or use the convenience function
conn = get_connection()

# Get SQLAlchemy components
engine = db.get_engine()
session = db.get_session()
base = db.get_base()
metadata = db.get_metadata()
```

### Key Features

#### 1. Connection Pooling

The class maintains a connection pool (default size: 5) for MySQL connections:

```python
pool = mysql.connector.pooling.MySQLConnectionPool(
    pool_name="main_pool",
    pool_size=5,
    pool_reset_session=True,
    ...
)
```

#### 2. Singleton Pattern

Only one instance of `DatabaseConnection` exists, ensuring consistent configuration:

```python
_db = DatabaseConnection()  # Global singleton

def get_db_connection():
    return _db
```

#### 3. SQLAlchemy Support

Provides SQLAlchemy engine, sessions, and reflected metadata:

```python
engine = db.get_engine()
session = db.get_session()
Base = db.get_base()  # Automap base with reflected tables
metadata = db.get_metadata()  # Reflected schema
```

#### 4. Configuration

Can be configured programmatically:

```python
db = get_db_connection()
db.configure(
    host="localhost",
    user="erik",
    password="ninjadogs",
    database="language"
)
```

## Changes to Existing Files

### database.py

**Before:**
```python
import mysql.connector

engine = create_engine('mysql://erik:ninjadogs@localhost/language')
connection = engine.connect()
session = Session(engine)

Base = automap_base()
Base.prepare(autoload_with=engine)

def get_connection():
    mydb = mysql.connector.connect(
        host="localhost",
        user="erik",
        password="ninjadogs",
        database='language'
    )
    return mydb
```

**After:**
```python
from db_connection import get_db_connection

_db = get_db_connection()
engine = _db.get_engine()
connection = engine.connect()
session = Session(engine)

Base = _db.get_base()
metadata_obj = _db.get_metadata()

def get_connection():
    """Get a database connection from the centralized connection pool."""
    return _db.get_connection()
```

### audioimport.py

**Before:**
```python
def get_db_connection():
    db = mysql.connector.connect(
        host="localhost",
        user="erik",
        password="ninjadogs",
        database='language'
    )
    cursor = db.cursor()
    return db, cursor
```

**After:**
```python
from db_connection import get_db_connection as get_db

_db = get_db()

def get_db_connection():
    """Get a database connection from the centralized connection pool."""
    db = _db.get_connection()
    cursor = db.cursor()
    return db, cursor
```

### stockmanager.py

**Before:**
```python
class StockManager:
    def __init__(self, host, user, password, database):
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
```

**After:**
```python
from db_connection import get_db_connection

_db = get_db_connection()

class StockManager:
    def __init__(self, host=None, user=None, password=None, database=None, use_pool=True):
        if use_pool:
            # Use centralized connection pool
            self.connection = _db.get_connection()
        else:
            # Use provided connection details for backward compatibility
            self.connection = mysql.connector.connect(...)
```

### activity_time_tracker.py

**No changes needed** - This file already uses `database.get_connection()`, which now uses the connection pool.

## Benefits

1. **Performance**: Connection pooling reduces overhead of creating/destroying connections
2. **Maintainability**: Single place to manage database configuration
3. **Resource Management**: Better control over database connections
4. **Thread Safety**: Proper locking ensures safe concurrent access
5. **Flexibility**: Easy to switch between MySQL connector and SQLAlchemy
6. **Backward Compatibility**: Existing code continues to work without changes

## Migration Guide

### For New Code

Use the centralized connection:

```python
from db_connection import get_connection

# Get a connection
conn = get_connection()
cursor = conn.cursor()

# Use the connection
cursor.execute("SELECT * FROM table")
results = cursor.fetchall()

# Close when done
cursor.close()
conn.close()
```

### For SQLAlchemy Usage

```python
from db_connection import get_db_connection

db = get_db_connection()

# Get a session
session = db.get_session()

# Use the session
results = session.query(Model).all()

# Close when done
session.close()
```

### For StockManager

```python
# Use connection pool (recommended)
manager = StockManager()

# Or provide custom credentials
manager = StockManager(
    host="custom_host",
    user="custom_user",
    password="custom_pass",
    database="custom_db",
    use_pool=False
)
```

## Testing

To verify the refactoring:

1. **Syntax Check**: All Python files should compile without errors
2. **Import Test**: `import db_connection` should succeed
3. **Integration Test**: Run the application and verify database operations work
4. **Connection Pool**: Monitor that connections are being reused

## Future Improvements

1. **Environment Variables**: Read credentials from environment variables
2. **Configuration File**: Support external configuration files
3. **Multiple Databases**: Support connections to multiple databases
4. **Connection Monitoring**: Add metrics for connection pool usage
5. **Retry Logic**: Add automatic retry for transient connection failures
6. **Health Checks**: Implement connection health checking

## Security Considerations

- Database credentials should be moved to environment variables or secure configuration
- The `dbconfig.py` file should be used to centralize credential management
- Consider using secrets management systems for production deployments

## Rollback Plan

If issues arise, the changes can be reverted by:

1. Removing `db_connection.py`
2. Restoring the previous versions of modified files
3. The `use_pool=False` parameter in `StockManager` provides a fallback mechanism
