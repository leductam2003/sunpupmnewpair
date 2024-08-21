import json
with open('dev.json', 'r') as f:
    dev = json.loads(f.read())

data = {}



testOwner = 'TWLw9QVSUxGFnDw8Zz4uC4DFnkJjWFx4UV'

for item in dev:
    if item['owner'] == testOwner:
        data['recentToken'] = item['recentToken']
        print(1)
        break
    
