# middleware.py
def simple_middleware(get_response):
    def middleware(request):
        response = get_response(request)
        response["Access-Control-Allow-Origin"] = "https://ft-transcendance-1.onrender.com"
        response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, Pragma" 
        response["Access-Control-Allow-Credentials"] = "true"
        return response
    return middleware