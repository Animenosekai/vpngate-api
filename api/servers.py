# Imports

## Flask Management
from flask import Flask, request
from flask_compress import Compress
from flask_cors import CORS

## Initialization
app = Flask(__name__) # Flask
Compress(app) # Compressing the responses
CORS(app) # Enabling CORS globally

## Other Imports
from time import time
from traceback import print_exc
from constants import makeResponse
from parse import parser
from utils import str_to_bool
from exceptions import RequestError, ParseError

## Variable Initialization
LOCAL_CACHE = {} # store variable
CACHE_DURATION = 60 # in sec.

# Route Defining
@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def hello(path):
    try:
        ## if the name of the file is in the following schema: [parameter].py
        # parameter = path[path.rfind("/") + 1:]

        # Cache Management

        ## Cache Key Defining
        _values_dict = request.values.to_dict()
        _values_dict.pop("_invalidate_cache", None)
        cache_key = str(_values_dict) + str(request.method)

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
                    return makeResponse(data=LOCAL_CACHE[cache_key]["data"], cache_hit=True)
        except:
            print_exc()
            print("[CACHE] An error occured while sending back the cached data")
            print("[FAILURE_RECOVERING] Processing the request as if nothing was cached")


        # Processing and Computation
        
        country = request.values.get("country", None)
        academic = str_to_bool(request.values.get("academic", True))
        config = str_to_bool(request.values.get("config", False))

        try:
            results = parser()
        except RequestError as err:
            return makeResponse({"message": str(err)}, error="REQUEST_ERROR", code=500)
        except ParseError as err:
            return makeResponse({"message": str(err)}, error="PARSER_ERROR", code=500)

        if not config:
            for server in results:
                server.pop("base64Config", None)

        if country:
            country = str(country).lower()
            results = [server for server in results if server["countryShort"].lower() == country or server["countryLong"].lower() == country]

        if not academic:
            results = [server for server in results if "academicuseonly" not in server["operator"].replace(" ", "").lower()]

        # Caching and Response
        LOCAL_CACHE[cache_key] = {"timestamp": time(), "data": results}
        return makeResponse(results, cache_hit=False)
    except:
        print_exc()
        print("[ERROR] An unknown error occured on the server and nothing could handle it. Sending back SERVER_ERROR (Status Code: 500)")
        return makeResponse({"message": "An error occured on the server"}, error="SERVER_ERROR", code=500)
