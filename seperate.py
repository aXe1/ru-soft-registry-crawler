#!/usr/bin/env python3
import json

with open('1.json', 'rb') as input_file:
    objects = json.load(input_file)

orgs = []
org_ids = []
soft = []
soft_ids = []
for obj in objects:
    if 'org_id' in obj and not obj['_id'] in soft_ids:
        soft.append(obj)
        soft_ids.append(obj['_id'])
    elif not obj['_id'] in org_ids:
        orgs.append(obj)
        org_ids.append(obj['_id'])

with open('orgs.json', 'w') as orgs_file:
    json.dump(orgs, orgs_file)
with open('soft.json', 'w') as soft_file:
    json.dump(soft, soft_file)
