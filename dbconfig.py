
def get_db_password():
    try:
        with open('/var/www/html/api/rfbackend/dbpassword.txt', 'r') as f:
            return f.readline().strip()
    except FileNotFoundError:
            raise Exception("API key file not found")
