# middleware.py
def simple_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        response["Access-Control-Allow-Origin"] = "https://ft-transcendance-1.onrender.com"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, PATCH, HEAD, CONNECT, TRACE, COPY, LOCK, MKCOL, MOVE, PROPFIND, PROPPATCH, SEARCH, UNLOCK"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Pragma, Cache-Control, If-Modified-Since, If-None-Match, X-Requested-With, X-CSRFToken, X-Frame-Options, X-Access-Token, X-Refresh-Token, X-Username, X-Password, Expires"
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    return middleware