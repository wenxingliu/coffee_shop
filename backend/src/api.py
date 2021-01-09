import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS
from functools import wraps

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth


class APIException(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
# db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
    drinks = Drink.query.order_by('id').all()

    if len(drinks) == 0:
        raise APIException("Resource Not Found", 404)

    try:
        drink_info = [drink.short() for drink in drinks]
        return jsonify({
            "success": True, 
            "drinks": drink_info
            }), 200
    except:
        raise APIException("Internal Error", 500)


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail')
@requires_auth('get:drinks-detail')
def get_drinks_details(jwt):
    drinks = Drink.query.order_by('id').all()
    
    if len(drinks) == 0:
        raise APIException("Resource Not Found", 404)

    drink_info = [drink.long() for drink in drinks]
    return jsonify({
        "success": True, 
        "drinks": drink_info
        }), 200


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink(jwt):
    try:
        body = request.get_json()
        new_drink = Drink(title=body['title'], recipe=body['recipe'])
        new_drink.insert()

        drinks = Drink.query.order_by('id').all()
        drink_info = [drink.long() for drink in drinks]

        return jsonify({
            "success": True, 
            "drinks": drink_info
            }), 200

    except:
        raise APIException("Unprocessable", 422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def update_drink(id, jwt):
    body = request.get_json()

    selected_coffee = Drink.query.get(id)
    
    if not selected_coffee:
        raise APIException("Resource Not Found", 404)

    try:
        selected_coffee.title = body['title']
        selected_coffee.recipe = body['recipe']
        selected_coffee.update()

        return jsonify({
            "success": True,
            "drinks": [selected_coffee]
            }), 200
    except:
        raise APIException("Unprocessable", 422)


'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<id>', methods=['DELETE'])
@requires_auth('patch:drinks')
def delete_drink(id, jwt):
    body = request.get_json()

    selected_coffee = Drink.query.get(id)

    if not selected_coffee:
        raise APIException("Resource Not Found", 404)
    
    try:
        selected_coffee.delete()

        return jsonify({
            "success": True,
            "delete": id
            }), 200

    except:
        raise APIException("Unprocessable", 422)

## Error Handling
'''
Example error handling for unprocessable entity
'''

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(APIException)
def not_found(e):
    return jsonify({
                    "success": False, 
                    "error": e.status_code,
                    "message": e.error
                    }), e.status_code
