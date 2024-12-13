import mysql.connector
from datetime import datetime

class StockManager:
    def __init__(self, host, user, password, database):
        """
        Initialize the StockManager with database connection details.
        """
        self.connection = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            database=database
        )
        self.cursor = self.connection.cursor()

    def get_latest_stock_prices(self):
        """
        Get a list of the latest stock prices.
        Returns:
            A list of tuples containing (stock_code, price, rating, update_datetime).
        """
        query = """
        SELECT stock_code, position, price, rating, update_datetime
        FROM stock_data
        ORDER BY update_datetime DESC;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def add_price_to_stock(self, stock_code, position,price, rating):
        """
        Add a new price and rating to a stock.
        Args:
            stock_code (str): The stock code (e.g., 'AAPL').
            price (float): The price of the stock.
            rating (str): The rating of the stock ('Buy', 'Hold', 'Sell').
        """
        query = """
        INSERT INTO stock_data (stock_code, position,price, rating)
        VALUES (%s, %s, %s);
        """
        self.cursor.execute(query, (stock_code, position,price, rating))
        self.connection.commit()

    def get_stocks_with_rating_change(self):
        """
        Get a list of stocks whose rating has changed between the last update.
        Returns:
            A list of tuples containing (stock_code, old_rating, new_rating, update_datetime).
        """
        query = """
        SELECT 
            a.stock_code, 
            a.rating AS old_rating, 
            b.rating AS new_rating, 
            b.update_datetime
        FROM 
            stock_data a
        JOIN 
            stock_data b
        ON 
            a.stock_code = b.stock_code
            AND a.update_datetime < b.update_datetime
        WHERE 
            a.rating != b.rating
        ORDER BY 
            b.update_datetime DESC;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()


    def get_stocks_with_position_change(self):
        """
        Get a list of stocks whose rating has changed between the last update.
        Returns:
            A list of tuples containing (stock_code, old_rating, new_rating, update_datetime).
        """
        query = """
        SELECT 
            a.stock_code, 
            a.position AS old_position, 
            b.position AS new_position, 
            b.update_datetime
        FROM 
            stock_data a
        JOIN 
            stock_data b
        ON 
            a.stock_code = b.stock_code
            AND a.update_datetime < b.update_datetime
        WHERE 
            a.position != b.position
        ORDER BY 
            b.update_datetime DESC;
        """
        self.cursor.execute(query)
        return self.cursor.fetchall()

    def close(self):
        """
        Close the database connection.
        """
        self.cursor.close()
        self.connection.close()

    
    
import os
# Example Usage
if __name__ == "__main__":
    # Database connection details
    host = "localhost"
    user = "erik"
    password = os.getenv( "DBPASSWORD" )
    database = "language"

    # Create an instance of StockManager
    stock_manager = StockManager(host, user, password, database)

    # Example 1: Get the latest stock prices
    latest_prices = stock_manager.get_latest_stock_prices()
    print("Latest Stock Prices:")
    for stock in latest_prices:
        print(stock)

    # Example 2: Add a new price to a stock
    stock_manager.add_price_to_stock("GOOGL", 2800.50, "Buy")
    print("Added new price for GOOGL.")

    # Example 3: Get stocks with rating changes
    rating_changes = stock_manager.get_stocks_with_rating_change()
    print("Stocks with Rating Changes:")
    for stock in rating_changes:
        print(stock)

   # Example 4: Get stocks with position changes
    rating_changes = stock_manager.get_stocks_with_rating_change()
    print("Stocks with Rating Changes:")
    for stock in rating_changes:
        print(stock)


    # Close the connection
    stock_manager.close()
