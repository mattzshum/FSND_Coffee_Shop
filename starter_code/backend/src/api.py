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

# db_drop_and_create_all()

## ROUTES
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
    return jsonify({"success": True})

@app.route('/drinks-detail', methods=['GET'])
@requires_auth('get:drinks-detail')
def get_all_drinks_detail():
    """
    Permission "get:drinks-detail" endpoint: "/drinks-detail"
    :return: drinks: List of drinks in long format
    """
    drinks = [drink.long() for drink in Drink.query.all()]
    return jsonify({
        'success': True,
        'drinks': drinks
    })
    
@app.route('/drinks', methods=['POST'])
@requires_auth('post:drinks')
def add_drink():
    """
    Permission "post:drinks" endpoint: "/drinks"
    :json title: string, recipe: dict
    :return: drinks: List containing newly created drink in long format
    """
    try:
        drink = Drink(title=request.json['title'], recipe=json.dumps(request.json['recipe']))
        drink.insert()
        print('SUCCESS')
        return jsonify({
            'success': True,
            'drinks': [drink.long()]
        })
    except Exception as E:
        print(E)
        abort(404)
    return jsonify({"success": True})

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
    return jsonify({"success": True})


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


@app.errorhandler(404)
def notfound(error):
    '''
    not found error
    '''
    return jsonify({
        'success':False,
        'error':404,
        'message':'resource not found'
    }), 404

@app.errorhandler(Exception)
def handle_error(error):
    '''
    Server Error
    ''' 
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