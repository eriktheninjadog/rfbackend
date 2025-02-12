#mine_ai_dialog.py

import openrouter

import remotechineseclient



def extract_text(data):
    if isinstance(data, dict):
        for value in data.values():
            yield from extract_text(value)
    elif isinstance(data, list):
        for item in data:
            yield from extract_text(item)
    elif isinstance(data, str):
        yield data

# Example usage:
# data = {"key1": "value1", "key2": ["value2", {"key3": "value3"}]}
# text_strings = list(extract_text(data))
# print(text_strings)

response = remotechineseclient.access_remote_client_get("llmentries/last_24_hours")
api = openrouter.OpenRouterAPI()
blop = extract_text(response)
result = ""
for b in blop:
    result += b

print(str(blop))
result = api.open_router_claude_3_5_sonnet("You are a language teaching expert, helping teachers to make their tutoring more efficient","From this lesson transcript, write notes what the student needs to practice on:" + result)
result = api.open_router_nova_micro_v1("Extract and organise the chinese from this text mass: " + result)
remotechineseclient.access_remote_client("make_c1_examples", {"pattern": "use vocabulary, syntax, expressions and grammatics from this text:" +result})
 