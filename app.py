#!flask/bin/python
from flask import (
    Flask,
    jsonify,
    abort,
    make_response,
    request,
    url_for
)
from modules.api_validation import (
    auth,
    get_password,
    unauthorized
)
from modules.airtable_call import (
    airtable_call,
    create_services_object,
    create_icons_object
)


app = Flask(__name__)


services_object = create_services_object()
icons_object = create_icons_object()
services = airtable_call()


# GET for all records
@app.route('/cards/api/services/', methods=['GET'])
@auth.login_required
def get_services():
    return jsonify({'services': [make_public_service(s) for s in services]})

# GET for single record
@app.route('/cards/api/services/<int:service_id>', methods=['GET'])
@auth.login_required
def get_service(service_id):
    service = [s for s in services if s['id'] == service_id]
    if len(service) == 0:
        abort(404)
    return jsonify({'service': make_public_service(service[0])})

# POST
@app.route('/cards/api/services/', methods=['POST'])
@auth.login_required
def create_service():
    if not request.json or not 'name' in request.json:
        abort(400)
    icon_ids = []
    for icon in request.json["icons"]:
        new_icon = {
            "icon" : icon["icon"],
            "text" : icon["text"]
        }
        new_icon_record = icons_object.insert(new_icon)
        icon_ids.append(new_icon_record["id"])
    refreshed_icons_object = create_icons_object() # get the new ones
    service = {
        # id is handled by airtable automatically
        "Name": request.json["name"],
        "Desc": request.json.get("desc", ""),
        "Icons": [refreshed_icons_object.get(id) for id in icon_ids]
    }
    services_object.insert(service)
    return jsonify({'service': make_public_service(service)}), 201

# DELETE
@app.route('/cards/api/services/<int:service_id>', methods=['DELETE'])
@auth.login_required
def delete_service(service_id):
    service = services_object.match('ID', str(service_id))
    if not service:
        abort(404)
    services_object.delete(service['id'])
    return jsonify({'result': True})

# PUT
@app.route('/cards/api/services/<int:service_id>', methods=['PUT'])
@auth.login_required
def update_service(service_id):
    service = services_object.match('ID', str(service_id))
    if not service:
        abort(404)
    if not request.json:
        abort(400)
    """
    if 'name' in request.json and type(request.json['name']) != type(unicode):
        abort(400)
    if 'desc' in request.json and type(request.json['desc']) is not type(unicode):
        abort(400)
    # TODO make this work
    if 'icons' in request.json and type(request.json['icons']) is not type(list):
        abort(400)
    """
    update_fields = {
        "Name" : request.json["name"] if "name" in request.json else "",
        "Desc" : request.json["desc"] if "desc" in request.json else "",
        "Icons" : [] # TODO make icons work
    }
    update_fields = {
        key: value for key, value in update_fields.items() if value is not None
    }
    print(update_fields)
    wait = input("waiting...\n\n\n")
    services_object.replace(service['id'], jsonify(update_fields))
    wait = input("waiting...\n\n\n")
    return jsonify({'service': make_public_service(service)})

# ERRORS returned as JSON
@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Not found'}), 404)

# replaces id field with link to uri field for user ease
def make_public_service(service):
    new_service = {}
    for field in service:
        if field == "id":
            new_service["uri"] = url_for(
                "get_service",
                service_id=service['id'],
                _external=True
            )
        else:
            new_service[field] = service[field]
    return new_service

if __name__ == '__main__':
    app.run(debug=True)
