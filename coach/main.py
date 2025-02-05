from teaching_agent import TeachingAgent



def _read_bearer_key() -> str:
    try:
        with open('/var/www/html/api/rfbackend/routerkey.txt', 'r') as f:
            return f.readline().strip()
    except FileNotFoundError:
        raise Exception("API key file not found")


# main.py
if __name__ == "__main__":
    api_key = _read_bearer_key()
    agent = TeachingAgent(api_key)
    agent.start_session()
