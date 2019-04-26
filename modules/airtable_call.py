# requires
# pip install airtable
# pip install airtable-python-wrapper

import json
import airtable
from airtable import Airtable

BASE_ID = "app38cZA2uPDxdTL8" # found in url of API documentation for base
SERVICES_TABLE = "Services"
ICONS_TABLE = "Icons"

def create_services_object():
    return Airtable(BASE_ID, SERVICES_TABLE)

def create_icons_object():
    return Airtable(BASE_ID, ICONS_TABLE)

def airtable_call():
    services_object = Airtable(BASE_ID, SERVICES_TABLE)
    records = services_object.get_all(sort="ID")

    service_list = []
    for record in records:
        od = { # Original Dictionary
            "id" : record['fields']['ID'],
            "name" : record['fields']['Name'],
            "desc" : record['fields']['Desc'],
            "icons" : []
        }
        for record_id in record['fields']['Icons']:
            icon_record = services_object.get(record_id)
            od["icons"].append({
                "text" : icon_record['fields']['text'],
                "icon" : icon_record['fields']['icon']
            })

        service_list.append(od)

    with open("output.json", "w") as f:
        json.dump(service_list, f, indent=2)

    return service_list


"""
        # The above is much more elegant, but this handles empty fields
        # without breaking...
        try:
            od['id'] = record['fields']['ID']
        except KeyError:
            continue # every record needs an ID, skip if there is not one
        try:
            od['name'] = record['fields']['Name']
        except KeyError:
            pass
        try:
            od['desc'] = record['fields']['Desc']
        except KeyError:
            pass
        try:
            for index, record_id in enumerate(record['fields']['Icons']):
                record = airtable_object.get(record_id)
                od['icons'].append({
                    "text" : "",
                    "icon" : ""
                })
                try:
                    od['icons'][index]['text'] = record['fields']['text']
                except KeyError:
                    pass
                try:
                    od['icons'][index]['icon'] = record['fields']['icon']
                except KeyError:
                    pass
        except KeyError:
            pass
        if od['icons'] == []:
            del od['icons']
"""
