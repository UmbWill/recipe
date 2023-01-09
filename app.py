import io
import base64
import datetime
import uuid
import json
import requests
import sqlite3
import time
from multiprocessing import Process
from flask import Flask, request, jsonify, make_response, g, send_file
from flask_cors import CORS
from common.extensions import cache
import factory_solver as fs
import validations

app = Flask(__name__)
CORS(app)
app.config.from_object('config.BaseConfig')
cache.init_app(app)

TIMEOUT_HEARTBEAT_SOLVER = 100
DATABASE = './recipes_db.db'

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route('/recipe', methods=['POST'])
def recipe():
    '''public: post recipe
    
    Request Args POST:
        -json:
        {"name" : string,
         "description": string,
         "time_cook": string,
         "time_preparation": string,
         "howto_prepare": string
        }

    Returns:
        -Success/200:

        -Not valid post data:
            Error 400.
        
        -Not valid method:
            Error 405
    '''
    if request.method == 'POST':
        instance_type = request.json.get("type")
        instance_data = request.json.get("instance_data")
        if instance_type == None or instance_data == None:
            return make_response(jsonify({
               "status": "FAILED",
               "message": "Not a valid instance."}), 400)
        json_instance = request.json
        instance_key = uuid.uuid3(uuid.NAMESPACE_X500, json.dumps(json_instance))
        cached_data = cache.get(str(instance_key))
        
        if cached_data == None:
            cache.set(str(instance_key), json_instance)
        cached_data = cache.get(str(instance_key))
        return make_response(jsonify({"instance_key":str(instance_key)}), 200)
    else:
        return make_response(jsonify({
               "status": "405",
               "message": "Error 405 Method Not Allowed"}), 405)

@app.route('/recipe_image', methods=['GET'])
def recipe_image():
    '''public: recipe_image
    
    Request Args GET:
        -id: recipe id

    Returns:
        -GET Success/200:
            - return recipe image if something found

        -Not valid post data:
            Error 400.
        
        -Not valid get data:
            Error 400.
        
        -Not valid method:
            Error 405
    '''
    print(request.method, flush=True)
    if request.method == 'GET':
        json_recipe_id_request = request.args
        print(json_recipe_id_request, flush=True)
        redis_image_key = uuid.uuid3(uuid.NAMESPACE_X500, json.dumps(json_recipe_id_request))
        cached_data = cache.get(str(redis_image_key))
        if cached_data != None:
            print("Found cache", flush=True)
            return send_file(
            io.BytesIO(cached_data),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='%s.jpg' % json_recipe_id_request["recipe_id"])    
        
        sql, args = createSqlQueryImage(json_recipe_id_request)
        print(sql, flush=True)
        print(args, flush=True)
        query_result = query_db(sql, args)
        if query_result == None:
            return make_response(jsonify({
                "status": "400",
                "message": "Not a valid solver request."}), 400)
        print("query result : ", flush=True)
        print(query_result[0].keys(), flush=True)
        keys = query_result[0].keys()
        # send_file download image 
        cache.set(str(redis_image_key), query_result[0]['image'])
        return send_file(
            io.BytesIO(query_result[0]['image']),
            mimetype='image/jpeg',
            as_attachment=True,
            download_name='%s.jpg' % json_recipe_id_request["recipe_id"])
        img_byte_arr = io.BytesIO(query_result[0]['image'])
        encoded_image = base64.encodebytes(img_byte_arr.getvalue()).decode('ascii')
        return make_response(jsonify({
                "status": "200",
                "ImageBytes": encoded_image}), 200)
    else:
        return make_response(jsonify({
               "status": "405",
               "message": "Error 405 Method Not Allowed"}), 405)

@app.route('/recipes_list', methods=['GET'])
def recipes_list():
    '''public: recipes_list
    
    Request Args GET:
        -ingredients: query string

    Returns:
        -GET Success/200:
            - return recipes if something found

        -Not valid post data:
            Error 400.
        
        -Not valid get data:
            Error 400.
        
        -Not valid method:
            Error 405
    '''
    print(request.method, flush=True)
    if request.method == 'GET':
        json_recipe_list_request = request.args
        print(json_recipe_list_request, flush=True)
        redis_recipe_list_key = uuid.uuid3(uuid.NAMESPACE_X500, json.dumps(json_recipe_list_request))
        cached_data = cache.get(str(redis_recipe_list_key))
        
        if cached_data != None:
            print("Find cache", flush=True)
            return make_response(jsonify({
                "status": "200",
                "message": cached_data}), 200)
        
        sql, args = createSqlQuery(json_recipe_list_request)
        print(sql, flush=True)
        print(args, flush=True)
        query_result = query_db(sql, args)
        if query_result == None:
            return make_response(jsonify({
                "status": "400",
                "message": "Not a valid solver request."}), 400)
        print("type query result : ", flush=True)
        print(query_result, flush=True)
        cache.set(str(redis_recipe_list_key), query_result)
        return make_response(jsonify({
                "status": "200",
                "message": query_result}), 200)
    else:
        return make_response(jsonify({
               "status": "405",
               "message": "Error 405 Method Not Allowed"}), 405)

def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    #rv = cur.fetchall()
    rv = [dict((cur.description[i][0], value) \
               for i, value in enumerate(row)) for row in cur.fetchall()]
    cur.close()
    return (rv[0] if rv else None) if one else rv

def createSqlQueryImage(recipe_id):
    args = []
    sql = "select image from recipe_image where recipe_id = ?;"
    args.append(recipe_id["recipe_id"])
    return (sql, args)

def createSqlQuery(json_data):
    cnt_courses = 0
    cnt_ingredients = 0
    args = []
    sql_courses = ""
    sql_ingredients = ""
    sql = "select * from recipe where"
    print("json_Data", flush=True)
    print(json_data, flush=True)
    for key in json_data:
        print((key, json_data[key]), flush=True)
        if key == 'course':
            courses = json_data[key].split(',')
            sql_courses += ' course = ? '
            cnt_courses = len(courses)
            sql_courses += " OR course = ? " * (cnt_courses-1)
            args.extend(courses)
        else:
            if json_data[key] == "true":
                if cnt_ingredients > 0:
                    sql_ingredients += " AND "
                cnt_ingredients+=1
                sql_ingredients += ' ingredient_name = ? '
                args.append(key)
    if cnt_courses > 0:
        sql += sql_courses
    if cnt_ingredients > 0:
        if cnt_courses > 0:
            sql += " AND "
        sql += "id in\
        (SELECT recipe_id from ingredients_recipes WHERE "
        sql += sql_ingredients 
        sql += ');'
    return (sql, args)



if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
