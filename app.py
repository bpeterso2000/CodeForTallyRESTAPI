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
    services_call,
    icons_call,
    create_services_object,
    create_icons_object
)


app = Flask(__name__)


services_object = create_services_object()
icons_object = create_icons_object()
services = services_call()
icons = icons_call()


# GET for all services
@app.route('/cards/api/services/', methods=['GET'])
@auth.login_required
def get_services():
    return jsonify({'services': [make_public_service(s) for s in services]})

# GET for single service
@app.route('/cards/api/services/<int:service_id>', methods=['GET'])
@auth.login_required
def get_service(service_id):
    service = [s for s in services if s['id'] == service_id]
    if len(service) == 0:
        abort(404)
    return jsonify({'service': make_public_service(service[0])})

# POST service
@app.route('/cards/api/services/', methods=['POST'])
@auth.login_required
def create_service():
    if not request.json or not 'name' in request.json:
        abort(400)
    new_icons = []
    for icon in request.json["icons"]:
        new_icon = create_icon()
        new_icons.append(new_icon)
    service = {
        # id is handled by airtable automatically
        "Name": request.json["name"],
        "Desc": request.json.get("desc", ""),
        "Icons": new_icons
    }
    services_object.insert(service)
    return jsonify({'service': make_public_service(service)}), 201

# DELETE service
@app.route('/cards/api/services/<int:service_id>', methods=['DELETE'])
@auth.login_required
def delete_service(service_id):
    service = services_object.match('ID', str(service_id))
    if not service:
        abort(404)
    services_object.delete(service['id'])
    return jsonify({'result': True})

# PUT for service
@app.route('/cards/api/services/<int:service_id>', methods=['PUT'])
@auth.login_required
def update_service(service_id):
    service = services_object.match('ID', str(service_id))
    if not service:
        abort(404)
    if not request.json:
        abort(400)
    # TODO add tests to make sure data is formatted properly
    update_fields = {
        k.title(): v for k, v in request.json.items() if v is not None
    }
    print(update_fields)
    print(service['id'])
    services_object.replace(service['id'], update_fields)
    return jsonify({'service': make_public_service(service)})

# GET for all icons
@app.route('/cards/api/icons/', methods=['GET'])
@auth.login_required
def get_icons():
    return jsonify({'icons': [i for i in icons]})

# GET for single icon
@app.route('/cards/api/icons/<int:icon_id>', methods=['GET'])
@auth.login_required
def get_icon(icon_id):
    icon = [i for i in icons if i['id'] == icon_id]
    if len(icon) == 0:
        abort(404)
    return jsonify({'icon': icon[0]})

# POST for icons
@app.route('/cards/api/icons/', methods=['POST'])
@auth.login_required
def create_icon():
    if not request.json or not 'icon' in request.json or not 'text' in request.json:
        abort(400)
    icon = {
        # id will be handled by airtable
        "icon" : request.json["icon"],
        "text" : request.json["text"],
        "Services" : []
    }
    new_icon_record = icons_object.insert(icon)
    return jsonify({'icon': icon}), 201

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
