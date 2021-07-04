from time import time
from requests import get
from constants import CACHE_TIMEOUT, CSV_API_URL, DATA_FIELDS
from exceptions import ParseError, RequestError

CACHE = None
LAST_CACHED = 0

def parser():
    """
    Returns API data
    """
    global CACHE
    global LAST_CACHED

    if time() - LAST_CACHED < CACHE_TIMEOUT:
        return CACHE

    try:
        # Downloading the data from VPNGate CSV API
        request = get(CSV_API_URL)
    except Exception as err:
        raise RequestError("An error occured while retrieving the data from VPNGate (error: {err})".format(err=str(err)))
    if request.status_code >= 400:
        raise RequestError("VPNGate returned a {code} HTTP Status Code".format(code=str(request.status_code)))

    try:
        # Prepare the data
        vpngate_data = request.text.split('\n')[2:] # does not contain the header
        
        # Variable declaration and initialization
        results = [] # stores a list of server object
        current_server = {} # stores the current server object data
        for server in vpngate_data:
            server_data = server.split(',') # CSV Data Splitting
            if len(server_data) == 15:
                # Iterate through all of the elements in the CSV Data
                for index, element in enumerate(server_data):
                    current_server[DATA_FIELDS[index]] = element
                results.append(current_server) # Append the resulting server object to the list of results
                current_server = {}

        CACHE = results
        LAST_CACHED = time()
        return results
    except Exception as err:
        raise ParseError("An error occured while parsing VPNGate's data (error: {err})".format(err=str(err)))