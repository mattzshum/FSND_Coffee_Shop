import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

from jose import jwt
from urllib.request import urlopen

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
@app.route('/drinks', methods=['GET'])
def get_drinks():
    try:
        # print('trying to retrieve drinks')
        drinks = [drink.short() for drink in Drink.query.all()]
        # print('success')
        return jsonify({
            'success':True,
            'drinks':drinks
        })
    except:
        #NOT FOUND ERROR
        print('aborting')
        abort(404)
    # SERVER ERROR
    # # # abort(500)
    return jsonify({"success": True})


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_drinks_details():
    '''
    Read drink details.
    '''
    try:
        drinks = [drink.long() for drink in Drink.query.all()]
        return jsonify({
            'success':True,
            'drinks':drinks
        })
    except:
        #NOT FOUND ERROR
        abort(404)
    # SERER ERROR
    # # abort(500)
    return jsonify({"success": True})
    


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
def add_drinks():
    '''
    Adds drinks to the database.
    '''
    try:
        drink = Drink(title=request.json['title'], recipe=json.dumps(request.json['recipe']))
        drink.insert()
        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        })
    except:
        # UNPROCESSABLE ERROR
        abort(422)
    # SERVER ERROR
    # # abort(500)
    return jsonify({"success": True})


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
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth('patch:drinks')
def modify_drink(drink_id):
    try:
        drink = Drink.query.get(drink_id)
        drink.title = request.json['title'] if 'title' in request.json else drink.title
        drink.recipe = json.dumps(request.json['recipe']) if 'recipe' in request.json else drink.recipe
        drink.update()
        return jsonify({
            'success':True,
            'drinks':[drink.long()]
        })
    except:
        abort(404)
    # # abort(500)
    return jsonify({"success": True})


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
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth('delete:drinks')
def delete_drink(drink_id):
    try:
        drink = Drink.query.get(drink_id)
        drink.delete()
        return jsonify({
            'success':True,
            'delete':drink_id
        })
    except:
        abort(404)
    # # # abort(500)
    return jsonify({"success": True})

## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
        "success": False, 
        "error": 422,
        "message": "unprocessable"
    }), 422

'''
# @TODO implement error handlers using the @app.errorhandler(error) decorator
#     each error handler should return (with approprate messages):
#              jsonify({
#                     "success": False, 
#                     "error": 404,
#                     "message": "resource not found"
#                     }), 404

# '''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def notfound(error):
    return jsonify({
        'success':False,
        'error':404,
        'message':'resource not found'
    }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(Exception)
def handle_error(error):
    return jsonify({
        'success':False,
        'error':500,
        'message':'server error'
    }), 500

@app.errorhandler(AuthError)
def auth_error_handler(error):
    response = jsonify(error.error)
    response.status_code = error.status_code
    return response