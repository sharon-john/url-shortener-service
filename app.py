from flask import Flask, request, make_response, jsonify, redirect
import url_shortener
import urllib.parse 
import sqlite3 

app = Flask(__name__)
# default to localhost 
localhost = "127.0.0.1"
global url_library
url_library = url_shortener.URLShortener(localhost)

RESPONSE_SUCCESS, RESPONSE_ERROR, RESPONSE_WARNING = "success", "error", "warning"
# Hardcoding custom constants here because Flask doesn't seem to provide these in a convenient way
HTTP_OK, HTTP_REDIRECT, HTTP_CLIENT_ISSUE, HTTP_NOT_FOUND, HTTP_SERVER_ERROR = 200, 302, 400, 404, 500 

def get_response(response_type, msg, code=HTTP_OK, data=""):
    if response_type == RESPONSE_SUCCESS: 
        json_response = { RESPONSE_SUCCESS : msg }
        # if we need to send json data back in the response 
        if type(data) == dict: 
            json_response["data"] = data 
        res = make_response( jsonify(json_response), HTTP_OK )

    elif response_type == RESPONSE_ERROR:
        json_response = { RESPONSE_ERROR : msg }
        if type(data) == dict:
            json_response["data"] = data 

        res = make_response(jsonify(json_response), code)
    
    return res 

@app.route('/')
def home():
    # set the domain the server ended up being serve at:  
    url_library.set_default_domain(request.base_url)
    return f"Welcome to Sharon's URL shortener service! \n In order to shorten a URL, please pass it as a query parameter (?url) to the /shorten path. This will produce a new, short URL at {request.base_url}", HTTP_OK

@app.route("/shorten", methods = ["GET"])
def shorten():
    long_url = request.args.get('url')
    if not long_url:
        return make_response("long URL parameter is required for shortening", HTTP_CLIENT_ISSUE)

    decoded_long_url = urllib.parse.unquote(long_url)
    print(decoded_long_url)
    already_shortened, short_url = url_library.shorten_url(decoded_long_url)
    print(already_shortened, short_url)
    if already_shortened:
        return make_response(f"URL {long_url} has already been shortened to {short_url}", HTTP_OK)
    else:
        return make_response(f"URL {long_url} is now accessible from the short URL {short_url}", HTTP_OK)

@app.route('/<path:path>', methods = ["GET"])
def handle_url_request(path):
    # long url, short url, brand new url 
    if path in url_library.long_url_mapping:
        click_count = request.args.get("click-count")
        return make_response(f"URL {path} has been clicked {click_count} times via its short URL", HTTP_OK)
    
    elif path in url_library.short_url_mapping: 
        url_info = url_library.short_url_mapping.get(path)
        return redirect(url_info + f"?click-count={url_info[1]}", code=HTTP_REDIRECT)

    else:
        return make_response(f"Unknown URL", HTTP_NOT_FOUND)

if __name__ == "__main__":
    app.run(debug=True, port=8080)