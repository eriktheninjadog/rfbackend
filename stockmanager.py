import mysql.connector
from datetime import datetime


"""CREATE TABLE stock_data (     stock_id INT AUTO_INCREMENT PRIMARY KEY,
   stock_code VARCHAR(20) NOT NULL,price DECIMAL(15, 2) NOT NULL,
               rating ENUM('STRONG BUY','BUY', 'HOLD', 'SELL','STRONG SELL') NOT NULL, position int,update_datetime DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP  );
"""


def extract_blocks(text):
    """
    Extracts blocks of text starting with ###START### and ending with ###END### from a long string.

    Args:
        text (str): The input string containing the blocks.

    Returns:
        list: A list of extracted blocks (strings).
    """
    # Define the regex pattern to match blocks
    pattern = r'###START###(.*?)###END###'
    
    # Use re.findall to extract all matching blocks
    blocks = re.findall(pattern, text, re.DOTALL)
    
    # Return the list of blocks
    return blocks
    
def parse_stock_block(stock_block):
    ret = []    
    blocks =extract_blocks(stock_block)
    for block in blocks:
        lines = block.strip().split('\n')
        if len(lines) >= 4:
            position = lines[0].strip()
            stock_code = lines[2].strip()
            rating = lines[6].strip().replace('RATING:','').strip()
            price = lines[4].strip()
            ret.append({"code":stock_code, "name":"doesntmatter", "position":position, "rating":rating, "price":00.0})    
    return ret

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
        WITH RankedStockData AS (
            SELECT 
                stock_code, 
                price, 
                rating, 
                update_datetime,
                ROW_NUMBER() OVER (PARTITION BY stock_code ORDER BY update_datetime DESC) AS rn
            FROM 
                stock_data
            )
            SELECT 
                stock_code, 
                price, 
                rating, 
                update_datetime
            FROM 
                RankedStockData
            WHERE 
            rn = 1;
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
        VALUES (%s, %s,%s, %s);
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
    
    def parse_block(self,block):
        print("parsing block")
        print(block)
        stocks = parse_stock_block(block)
        for s in stocks:
            print(str(s))
            self.add_price_to_stock(s['code'],int(s['position']),float(s['price']),s['rating'])
        return None
        

    def close(self):
        """
        Close the database connection.
        """
        self.cursor.close()
        self.connection.close()
    
import re
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
    #stock_manager.parse_block(stockblock)
    # Example 1: Get the latest stock prices
    latest_prices = stock_manager.get_latest_stock_prices()
    # Close the connection
    stock_manager.close()
