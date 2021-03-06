# Imports

## Flask Management
from flask import Flask, request, send_file
from flask_compress import Compress
from flask_cors import CORS

## Initialization
app = Flask(__name__) # Flask
Compress(app) # Compressing the responses
CORS(app) # Enabling CORS globally

## Other Imports
from time import time
from io import BytesIO
from base64 import b64decode

from traceback import print_exc
from constants import makeResponse
from parse import parser
from utils import str_to_bool
from exceptions import RequestError, ParseError

## Variable Initialization
LOCAL_CACHE = {} # store variable
CACHE_DURATION = 3600 # in sec.

# Route Defining
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    try:
        ## if the name of the file is in the following schema: [parameter].py
        server_ip = path[path.rfind("/") + 1:]

        # Cache Management

        ## Cache Key Defining
        _values_dict = request.values.to_dict()
        _values_dict.pop("_invalidate_cache", None)
        cache_key = str(_values_dict) + str(request.method) + server_ip

        ## Cache Invalidation Management
        if "_invalidate_cache" in request.values:
            LOCAL_CACHE.pop(cache_key, None)
            return "Ok"
        
        ## Cache Lookup
        try:
            if cache_key in LOCAL_CACHE:
                cache_duration = time() - LOCAL_CACHE[cache_key]["timestamp"]
                if cache_duration > CACHE_DURATION:
                    LOCAL_CACHE.pop(cache_key, None)
                else:
                    return send_file(BytesIO(LOCAL_CACHE[cache_key]["data"]), as_attachment=True, attachment_filename="{country} Server ({ip}).ovpn".format(country=LOCAL_CACHE[cache_key]["countryShort"], ip=LOCAL_CACHE[cache_key]["ip"]))
        except:
            print_exc()
            print("[CACHE] An error occured while sending back the cached data")
            print("[FAILURE_RECOVERING] Processing the request as if nothing was cached")


        # Processing and Computation
        result = None # the result should in this variable

        try:
            results = parser()
        except RequestError as err:
            return makeResponse({"message": str(err)}, error="REQUEST_ERROR", code=500)
        except ParseError as err:
            return makeResponse({"message": str(err)}, error="PARSER_ERROR", code=500)

        results = [server for server in results if server["ip"] == server_ip]

        if len(results) == 0:
            return makeResponse({"message": "We couldn't find this server"}, error="NOT_FOUND", code=404)
        
        server = results[0]

        result = b64decode(server["base64Config"])
            
        # Caching and Response
        LOCAL_CACHE[cache_key] = {"timestamp": time(), "data": result, "countryShort": server["countryShort"], "ip": server["ip"]}
        return send_file(BytesIO(result), as_attachment=True, attachment_filename="{country} Server ({ip}).ovpn".format(country=server["countryShort"], ip=server["ip"]))
    except:
        print_exc()
        print("[ERROR] An unknown error occured on the server and nothing could handle it. Sending back SERVER_ERROR (Status Code: 500)")
        return makeResponse({"message": "An error occured on the server"}, error="SERVER_ERROR", code=500)
