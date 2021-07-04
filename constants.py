from flask import request, Response
from json import dumps

CACHE_TIMEOUT = 600 # in sec
CSV_API_URL = "http://www.vpngate.net/api/iphone/"
CSV_FIELDS = ["ServerName", "IP", "Score", "Ping", "Speed", "CountryLong", "CountryShort", "NumberOfVPNSessions", "Uptime", "TotalUsers", "TotalTraffic", "LogType", "Operator", "Message", "OpenVPN_ConfigData_Base64"]
DATA_FIELDS = ["name", "ip", "score", "ping", "speed", "countryLong", "countryShort", "numberOfSessions", "uptime", "totalUsers", "totalTraffic", "logType", "operator", "message", "base64Config"]
INT_DATA = {"score", "ping", "speed", "numberOfSessions", "uptime", "totalUsers", "totalTraffic"}

def makeResponse(data=None, error=None, code=200, cache_hit=False):
    """
    Shapes the response
    """
    responseBody = {"success": error is None, "error": error, "data": data}

    if "minify" in request.values:
        response = Response(dumps(responseBody, ensure_ascii=False, separators=(",", ":")))
    else:
        response = Response(dumps(responseBody, ensure_ascii=False, indent=4))
    
    response.headers["Server"] = "Anise"
    response.headers["Content-Type"] = "application/json"
    if cache_hit:
        response.headers["X-ANISE-CACHE"] = "HIT"
    else:
        response.headers["X-ANISE-CACHE"] = "MISS"
    response.status_code = int(code)
    return response
