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
        stocks = parse_stock_block(block)
        for s in stocks:
            self.add_price_to_stock(s['code'],int(s['position']),float(s['price']),s['rating'])
        return None
        

    def close(self):
        """
        Close the database connection.
        """
        self.cursor.close()
        self.connection.close()

    
    
    
import re



stockblock = """
content.js:1 Page URL: https://seekingalpha.com/screeners/96793299-Top-Rated-Stocks
content.js:2 storageToken undefined
content.js:2 storageSession undefined
content.js:2 storageExpiresAt 2023-12-05T05:52:20.953Z
init.js:3 Error
c.9738.c3919826.js:1 
###START###
1
	
LX
	
LexinFintech Holdings Ltd.
	
RATING: STRONG BUY
4.99	
RATING: BUY
4.00	
RATING: STRONG BUY
4.75	
981.54M
	
2.31%
	A-	A-	B+	A+	B	
###END###

###START###
2
	
KINS
	
Kingstone Companies, Inc.
	
RATING: STRONG BUY
4.98	
RATING: BUY
4.00	
RATING: STRONG BUY
5.00	
192.15M
	
-
	B+	B+	B+	A+	A-	
###END###

###START###
3
	
PSIX
	
Power Solutions International, Inc.
	
RATING: STRONG BUY
4.98	
RATING: BUY
3.62	
RATING: STRONG BUY
5.00	
620.99M
	
-
	B	A+	A+	A+	A	
###END###

###START###
4
	
CCL
	
Carnival Corporation & plc
	
RATING: STRONG BUY
4.96	
RATING: BUY
4.00	
RATING: BUY
4.20	
34.17B
	
-
	B-	A+	A	A	A+	
###END###

###START###
5
	
UAL
	
United Airlines Holdings, Inc.
	
RATING: STRONG BUY
4.96	
RATING: BUY
4.00	
RATING: STRONG BUY
4.54	
32.55B
	
-
	A	A	A	A+	B+	
###END###

###START###
6
	
QFIN
	
Qifu Technology, Inc.
	
RATING: STRONG BUY
4.96	
RATING: BUY
4.00	
RATING: STRONG BUY
4.81	
5.93B
	
3.09%
	A	A-	B+	A+	A	
###END###

###START###
7
	
EBS
	
Emergent BioSolutions Inc.
	
RATING: STRONG BUY
4.94	
RATING: BUY
4.00	
RATING: BUY
3.50	
464.36M
	
-
	A+	A+	B+	A+	A	
###END###

###START###
8
	
ICAGY
	
International Consolidated Airlines Group S.A.
	
RATING: STRONG BUY
4.93	
RATING: BUY
4.00	
RATING: STRONG BUY
5.00	
17.92B
	
0.89%
	A	A+	A+	A+	A+	
###END###

###START###
9
	
SKYW
	
SkyWest, Inc.
	
RATING: STRONG BUY
4.91	
RATING: BUY
3.80	
RATING: BUY
4.00	
4.42B
	
-
	A+	A+	B+	A+	A+	
###END###

###START###
10
	
AAL
	
American Airlines Group Inc.
	
RATING: STRONG BUY
4.86	
RATING: BUY
4.33	
RATING: BUY
3.56	
11.55B
	
-
	B	A-	B-	A	A-	
###END###

###START###
11
	
GM
	
General Motors Company
	
RATING: STRONG BUY
4.85	
RATING: BUY
4.00	
RATING: BUY
3.78	
57.22B
	
0.92%
	A	B-	A+	B+	B+	
###END###

###START###
12
	
PNC
	
The PNC Financial Services Group, Inc.
	
RATING: STRONG BUY
4.84	
RATING: BUY
4.00	
RATING: BUY
3.78	
80.70B
	
3.10%
	B	B+	A+	B-	B	
###END###

###START###
13
	
MFC
	
Manulife Financial Corporation
	
RATING: STRONG BUY
4.84	
RATING: BUY
3.50	
RATING: BUY
3.78	
55.17B
	
3.71%
	B+	B-	A+	B-	B+	
###END###

###START###
14
	
JD
	
JD.com, Inc.
	
RATING: STRONG BUY
4.83	
RATING: BUY
3.80	
RATING: STRONG BUY
4.60	
55.39B
	
1.99%
	A-	B	A+	A-	B+	
###END###

###START###
15
	
KGC
	
Kinross Gold Corporation
	
RATING: STRONG BUY
4.82	
RATING: BUY
3.50	
RATING: BUY
3.86	
12.97B
	
1.14%
	A-	A-	A	A	A	
###END###

###START###
16
	
FINV
	
FinVolution Group
	
RATING: STRONG BUY
4.81	
RATING: STRONG BUY
4.50	
RATING: STRONG BUY
4.66	
1.77B
	
3.48%
	A	B-	A-	A-	A+	
###END###

###START###
17
	
NLCP
	
NewLake Capital Partners, Inc.
	
RATING: STRONG BUY
4.81	
RATING: BUY
3.88	
RATING: STRONG BUY
5.00	
406.00M
	
8.59%
	A	A	A+	B-	B-	
###END###

###START###
18
	
WLKP
	
Westlake Chemical Partners LP Common Units
	
RATING: STRONG BUY
4.78	
RATING: STRONG BUY
5.00	
RATING: BUY
4.00	
849.25M
	
7.82%
	A+	A	A	B-	A+	
###END###

###START###
19
	
ACIC
	
American Coastal Insurance Corporation
	
RATING: STRONG BUY
4.77	
RATING: BUY
4.00	
RATING: BUY
4.00	
682.10M
	
-
	A-	B+	A	B+	A+	
###END###

###START###
20
	
VLRS
	
Controladora Vuela Compañía de Aviación, S.A.B. de C.V.
	
RATING: STRONG BUY
4.75	
RATING: BUY
4.00	
RATING: STRONG BUY
4.53	
981.33M
	
-
	A+	B-	B+	B	A+	
###END###

###START###
21
	
VCTR
	
Victory Capital Holdings, Inc.
	
RATING: STRONG BUY
4.75	
RATING: STRONG BUY
5.00	
RATING: BUY
3.70	
4.30B
	
2.35%
	B	A	A-	A	B+	
###END###

###START###
22
	
GAP
	
The Gap, Inc.
	
RATING: STRONG BUY
4.74	
RATING: BUY
4.00	
RATING: BUY
3.71	
9.51B
	
2.38%
	A+	A	B+	B-	A+	
###END###

###START###
23
	
MCY
	
Mercury General Corporation
	
RATING: STRONG BUY
4.73	
RATING: BUY
3.50	
RATING: BUY
4.00	
4.04B
	
1.75%
	B+	A-	B	A-	A+	
###END###

###START###
24
	
IMAX
	
IMAX Corporation
	
RATING: STRONG BUY
4.71	
RATING: BUY
4.00	
RATING: BUY
4.36	
1.37B
	
-
	A	A+	B-	A	B+	
###END###

###START###
25
	
BRFS
	
BRF S.A.
	
RATING: STRONG BUY
4.70	
RATING: BUY
3.50	
RATING: BUY
3.50	
7.80B
	
-
	A	A-	B	A	A+	
###END###

###START###
26
	
PRDO
	
Perdoceo Education Corporation
	
RATING: STRONG BUY
4.67	
RATING: BUY
4.00	
RATING: BUY
4.00	
1.82B
	
1.74%
	B	B+	A-	A-	A-	
###END###

###START###
27
	
RNG
	
RingCentral, Inc.
	
RATING: STRONG BUY
4.62	
RATING: BUY
4.00	
RATING: BUY
3.85	
3.78B
	
-
	A+	B	B+	B+	B	
###END###

###START###
28
	
DAL
	
Delta Air Lines, Inc.
	
RATING: STRONG BUY
4.54	
RATING: BUY
4.14	
RATING: STRONG BUY
4.60	
40.70B
	
0.79%
	B	A+	A+	A	B-	
###END###

###START###
29
	
THC
	
Tenet Healthcare Corporation
	
RATING: STRONG BUY
4.50	
RATING: BUY
4.00	
RATING: BUY
4.35	
13.32B
	
-
	A+	B+	A+	A-	B+	
###END###

###START###
30
	
VIRT
	
Virtu Financial, Inc.
	
RATING: BUY
4.47	
RATING: STRONG BUY
5.00	
RATING: BUY
3.77	
5.69B
	
2.61%
	B+	B	B-	A	B-	
###END###

###START###
31
	
UNM
	
Unum Group
	
RATING: BUY
4.44	
RATING: BUY
3.66	
RATING: BUY
4.00	
13.32B
	
2.15%
	B-	B+	B	A	B-	
###END###

###START###
32
	
PBPB
	
Potbelly Corporation
	
RATING: BUY
4.38	
RATING: BUY
3.50	
RATING: STRONG BUY
4.50	
296.08M
	
-
	B+	A	B+	B	A	
###END###

###START###
33
	
SKX
	
Skechers U.S.A., Inc.
	
RATING: BUY
4.36	
RATING: BUY
3.75	
RATING: BUY
4.41	
10.72B
	
-
	B	B+	B-	B-	A-	
###END###

###START###
34
	
SKWD
	
Skyward Specialty Insurance Group, Inc.
	
RATING: BUY
4.26	
RATING: BUY
3.50	
RATING: BUY
4.18	
2.05B
	
-
	B	A	B	A-	B-	
###END###

###START###
35
	
FLUT
	
Flutter Entertainment plc
	
RATING: BUY
4.23	
RATING: STRONG BUY
5.00	
RATING: STRONG BUY
4.54	
49.40B
	
-
	B-	A+	B+	A-	B-	
###END###

###START###
36
	
PFBC
	
Preferred Bank
	
RATING: BUY
4.14	
RATING: STRONG BUY
5.00	
RATING: BUY
3.60	
1.25B
	
2.98%
	B-	B-	B-	B-	B-	
###END###

###START###
37
	
BYDDF
	
BYD Company Limited
	
RATING: BUY
4.08	
RATING: BUY
4.20	
RATING: BUY
4.00	
108.52B
	
1.24%
	B	B-	A+	B+	B-	
###END###

###START###
38
	
BIP
	
Brookfield Infrastructure Partners L.P. Limited Partnership Units
	
RATING: BUY
3.83	
RATING: BUY
4.20	
RATING: BUY
4.41	
15.83B
	
4.79%
	A-	A	A	B+	B-	
###END###

###START###
39
	
TOUR
	
Tuniu Corporation
	
RATING: BUY
3.74	
RATING: BUY
4.00	
RATING: STRONG BUY
5.00	
136.36M
	
-
	A	B+	A+	A-	B-	
###END###

###START###
40
	
KEX
	
Kirby Corporation
	
RATING: BUY
3.73	
RATING: BUY
3.66	
RATING: STRONG BUY
5.00	
6.77B
	
-
	A-	A	B	B-	B-	
###END###

###START###
41
	
PR
	
Permian Resources Corporation
	
RATING: BUY
3.63	
RATING: STRONG BUY
4.66	
RATING: STRONG BUY
4.50	
12.07B
	
4.06%
	B-	A	A-	B-	B-	
###END###

c.9738.c3919826.js:1 Heartbeat stopped
5c.9738.c3919826.js:1 Checking for service worker update...
2content.js:290 chrome.runtime.onMessage.addListener
    
    """
    
    
import os
# Example Usage
if __name__ == "__main__":
    
    parse_stock_block(stockblock)
    
    # Database connection details
    host = "localhost"
    user = "erik"
    password = os.getenv( "DBPASSWORD" )
    database = "language"

    # Create an instance of StockManager
    stock_manager = StockManager(host, user, password, database)
    stock_manager.parse_block(stockblock)
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
