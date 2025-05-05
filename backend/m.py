import json

with open("token.json") as f:
    token = json.load(f)
    print(json.dumps(token))
