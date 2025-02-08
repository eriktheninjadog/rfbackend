#activity_time_tracker

import mysql.connector
from mysql.connector import Error


import database

def add_time_to_activity(activity_name: str, milliseconds_to_add: int) -> bool:
    """
    Adds milliseconds to an activity's accumulated time. Creates new activity if it doesn't exist.
    
    Args:
        activity_name (str): Name of the activity to update
        milliseconds_to_add (int): Number of milliseconds to add to the activity's accumulated time
    
    Returns:
        bool: True if operation was successful, False otherwise
    """
    # Database connection configuration
    try:
        # Validate input
        if not activity_name or not isinstance(activity_name, str):
            raise ValueError("Activity name must be a non-empty string")
        
        if not isinstance(milliseconds_to_add, int) or milliseconds_to_add < 0:
            raise ValueError("Milliseconds must be a positive integer")

        # Establish database connection
        conn = database.get_connection()
        cursor= conn.cursor()

        # First, try to update existing activity
        update_query = """
            UPDATE ActivityTimes 
            SET AccumulatedTime = AccumulatedTime + %s 
            WHERE ActivityName = %s
        """
        cursor.execute(update_query, (milliseconds_to_add, activity_name))

        # If no rows were updated (activity doesn't exist), create new activity
        if cursor.rowcount == 0:
            insert_query = """
                INSERT INTO ActivityTimes (ActivityName, AccumulatedTime) 
                VALUES (%s, %s)
            """
            cursor.execute(insert_query, (activity_name, milliseconds_to_add))

        # Commit the transaction
        conn.commit()
        return True

    except Error as e:
        print(f"Database error: {e}")
        return False
    except ValueError as e:
        print(f"Validation error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

def get_accumulated_time(activity_name: str) -> int:
    """
    Retrieves the accumulated time in milliseconds for a specific activity.
    
    Args:
        activity_name (str): Name of the activity to retrieve
    
    Returns:
        int: Accumulated time in milliseconds, or 0 if activity not found
    """
    # Database connection configuration
    db_config = {
        'host': 'localhost',
        'user': 'your_username',
        'password': 'your_password',
        'database': 'your_database'
    }

    try:
        # Validate input
        if not activity_name or not isinstance(activity_name, str):
            raise ValueError("Activity name must be a non-empty string")
        
        # Establish database connection
        conn = database.get_connection()
        cursor = conn.cursor()

        # Query to get the accumulated time
        select_query = """
            SELECT AccumulatedTime FROM ActivityTimes 
            WHERE ActivityName = %s
        """
        cursor.execute(select_query, (activity_name,))
        result = cursor.fetchone()

        # Return the accumulated time or 0 if not found
        return result[0] if result else 0

    except Error as e:
        print(f"Database error: {e}")
        return 0
    except ValueError as e:
        print(f"Validation error: {e}")
        return 0
    except Exception as e:
        print(f"Unexpected error: {e}")
        return 0
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

