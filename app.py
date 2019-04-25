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



app = Flask(__name__)

services = [
    {
        'id': 1,
        'name': u'Crowdsource Rescue',
        'desc': u'Get help when 911 is overwhelmed: citizen first responders, wellness checks, and debris removal.',
        'icons': [
            {
                "text" : "18,500+ recuers & volunteers",
                "icon" : "fas fa-first-aid fa-lg"
            },
            {
                "text" : "46,000+ survivors helped",
                "icon" : "fas fa-ambulance fa-lg"
            }
        ]
    },
    {
        'id': 2,
        'name': u'Harmany',
        'desc': u'Emergency and evacuation home sharing; connects people to willing hosts.',
        'icons': [
            {
                "text" : "Need a place",
                "icon" : "fas fa-house-damage fa-lg"
            },
            {
                "text" : "Have a place",
                "icon" : "fas fa-home fa-lg"
            }
        ]
    },
    {
        'id': 3,
        'name': u'Airbnb',
        'desc': u'Free, temporary housing to people who have needed to leave their home due to conflict, disasters, or medical care.',
        'icons': [
            {
                "text" : "11,000+ temporary homes provided.",
                "icon" : "fas fa-warehouse fa-lg"
            }
        ]
    }

]


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
    service = {
        "id": services[-1]["id"] + 1, # guarantees unique id
        "name": request.json["name"],
        "desc": request.json.get("desc", ""),
        "icons": [
            {
                "text" : request.json.get("text", ""), # TODO make this work
                "icon" : request.json.get("icon", "") # TODO same
            }
        ]
    }
    services.append(service)
    return jsonify({'service': make_public_service(service)}), 201

# DELETE
@app.route('/cards/api/services/<int:service_id>/', methods=['DELETE'])
@auth.login_required
def delete_service(service_id):
    service = [s for s in services if s['id'] == service_id]
    if len(service) == 0:
        abort(404)
    services.remove(service[0])
    return jsonify({'result': True})

# PUT
@app.route('/cards/api/services/<int:service_id>', methods=['PUT'])
@auth.login_required
def update_task(service_id):
    service = [s for s in services if s['id'] == service_id]
    if len(service) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'name' in request.json and type(request.json['name']) != unicode:
        abort(400)
    if 'desc' in request.json and type(request.json['desc']) is not unicode:
        abort(400)
    # TODO make this work
    if 'icons' in request.json and type(request.json['icons']) is not type(list):
        abort(400)
    service[0]['name'] = request.json.get('name', service[0]['name'])
    service[0]['desc'] = request.json.get('desc', service[0]['desc'])
    # TODO make this work
    service[0]['icons'] = request.json.get('icons', service[0]['icons'])
    return jsonify({'service': make_public_service(service[0])})

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
