#mine_ai_dialog.py

import remotechineseclient



response = remotechineseclient.access_remote_client_get("llmentries/last_24_hours")
print(str(response))