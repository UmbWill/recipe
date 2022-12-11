import datetime
import uuid
import json
import requests
import time
from multiprocessing import Process
from flask import Flask, request, jsonify, make_response
from common.extensions import cache
import factory_solver as fs
import validations

app = Flask(__name__)
app.config.from_object('config.BaseConfig')
cache.init_app(app)

TIMEOUT_HEARTBEAT_SOLVER = 100

@app.route('/post_instance', methods=['POST'])
def post_instance():
    '''public: post instance
    
    Request Args POST:
        -json:
        {"type": string,
         "instance_data": json
        }

    Returns:
        -Success/200:
            {"instance_key":string}

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

@app.route('/solver_request', methods=['GET', 'POST'])
def solver_request():
    '''public: solver request
    
    Request Args POST:
        -json:
        {
            "instance_key": json,
            "solver": string,
            "parameters": json
        }

    Request Args GET:
        -result_key: string

    Returns:
        -POST Success/200:
            {"result_key":string}

        -GET Success/200:
            -SUCCESS:
                {
                    "status":string,
                    "result":object
                }
            -FAILED:
                {
                    "status":string,
                    "message":string
                }
            -PENDING:
                {
                    "status":string
                }

        -Not valid post data:
            Error 400.
        
        -Not valid get data:
            Error 400.
        
        -Not valid method:
            Error 405
    '''
    if request.method == 'POST':
        json_solver_request = request.json
        if not _validation(json_solver_request):
            return make_response(jsonify({
                "status": "400",
                "message": "Not a valid solver request."}), 400)
        return _create_post_sr_response(json_solver_request)
    elif request.method == 'GET':
        return _create_get_sr_response()
    else:
        return make_response(jsonify({
               "status": "405",
               "message": "Error 405 Method Not Allowed"}), 405)

@app.route('/mock_pending', methods=['POST'])
def mock_pending():
    '''public: mock endopint for switch the status of a solver request to PENDING.'''

    if request.method == 'POST':
        result_key = request.json.get("result_key")
        cached_data = cache.get(str(result_key)) 
        cached_data["status"] = "PENDING"
        cache.set(str(result_key), cached_data)
        return make_response(jsonify({
                "status": "200",
                "message": "Set status to pending."}), 200)
    else:
        return make_response(jsonify({
               "status": "405",
               "message": "Error 405 Method Not Allowed"}), 405)

def _validation(json_solver_request):
    '''private: validation solver request.'''

    if json_solver_request["instance_key"] == None or \
       json_solver_request["solver"] == None or \
       json_solver_request["parameters"] == None or \
       not validations._validation_solver(json_solver_request["solver"]):
        return False
    return True

def _create_post_sr_response(json_solver_request):
    '''private: create solver request for a POST request.'''

    fact_solver = fs.FactorySolver()
    result_key = uuid.uuid3(uuid.NAMESPACE_X500, json.dumps(json_solver_request))
    cached_data = cache.get(str(result_key))
    fact_solver.set_parameters(result_key, cached_data)
    if cached_data == None:
        #call solver
        fact_solver.set_parameters(result_key, json_solver_request)
        fact_solver.solver()
    elif cached_data["status"] == "FAILED":
        #call solver
        fact_solver.solver()
    elif cached_data["status"] == "PENDING":
        cur_time = int(datetime.datetime.now().timestamp())
        if cur_time - cached_data["heartbeat"] > TIMEOUT_HEARTBEAT_SOLVER:
            fact_solver.solver()
    return make_response(jsonify({"result_key":str(result_key)}), 200)

def _create_get_sr_response():
    '''private: create solver request for a GET request.'''
    
    result_key = request.args.get("result_key")
    cached_data = cache.get(str(result_key)) 
    if cached_data == None:
        return make_response(jsonify({
            "status": "400",
            "message": "Not a valid result key."}), 400)
    status = cached_data["status"]
    if status == "PENDING":
        return make_response(jsonify({
                "status": status}), 200)
    elif status == "FAILED":
        return make_response(jsonify({
                "status": status,
                "message": cached_data["message"]}), 200)
    elif status == "SUCCESS":
        return make_response(jsonify({
                "status": status,
                "result": cached_data["result"]}), 200)
    else:
        return make_response(jsonify({
                "status": "400",
                "message": "Bad Request."}), 400)

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
