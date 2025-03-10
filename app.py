from flask import Flask, request, make_response, redirect
import url_shortener
from urllib import parse 
import os 

app = Flask(__name__)

# default to localhost 
localhost = "127.0.0.1"
global url_library
url_library = url_shortener.URLShortener(localhost)

RESPONSE_SUCCESS, RESPONSE_ERROR, RESPONSE_WARNING = "success", "error", "warning"
# Hardcoding custom constants here because Flask doesn't seem to provide these in a convenient way
HTTP_OK, HTTP_REDIRECT, HTTP_CLIENT_ISSUE, HTTP_NOT_FOUND, HTTP_SERVER_ERROR = 200, 302, 400, 404, 500 

@app.route('/')
def home():
    # set the domain the server ended up being served at:  
    url_library.set_default_domain(request.host_url)
    return f"<b> Welcome to Sharon's URL shortener service! </b> <br> <br> The following routes are available: <br> <br> <b> GET /shorten?url=url </b> Please pass full URLs in the query parameter. This will produce a new short URL at <b> {request.host_url} </b> <br> <b> GET /getOriginal?url=url </b>. Pass a full shortened URL to get back the original. <br> Any other GET /route request will be interpreted as a query for a short URL and redirected if available with its click count.  ", HTTP_OK

@app.route("/shorten", methods = ["GET"])
def shorten():
    # if we didn't visit the base route after starting the server, let's set it here so the URLs get shortened correctly
    if url_library.get_default_domain != request.host_url: 
        url_library.set_default_domain(request.host_url)

    long_url = request.args.get('url')
    if not long_url:
        return make_response("long URL parameter is required for shortening", HTTP_CLIENT_ISSUE)

    decoded_long_url = parse.unquote(long_url)

    try:
        newly_shortened, short_url = url_library.shorten_url(decoded_long_url)
        if newly_shortened:
            return make_response(f"Long URL <b> {long_url} </b> is now accessible from the short URL <b> {short_url} </b>", HTTP_OK)
        else:
            return make_response(f"Long URL <b> {long_url} </b> has already been shortened to short URL <b> {short_url} </b>", HTTP_OK)
    except Exception as e:
        return make_response(f"URL shortening failed because: <br> <br> <b> {e} </b>")

@app.route("/getOriginal", methods = ["GET"])
def get_original_url():
    short_url = request.args.get('url')
    if not short_url:
        return make_response("short URL parameter is required to obtain the original long URL", HTTP_CLIENT_ISSUE)

    decoded_short_url = parse.unquote(short_url)

    try:
        url_info = url_library.get_url(decoded_short_url) 
        return make_response(f"The original URL is <b> {url_info[0]} </b>", HTTP_OK)
    except KeyError as key_error:
        return make_response(f"No such short URL exists.", HTTP_CLIENT_ISSUE)

@app.route('/<path:path>', methods = ["GET"])
def handle_url_request(path):
    # request is routing to a long URL
    # the resulting content in response will only be seen if the long URL is hosted on this server 
    if request.base_url in url_library.long_url_mapping:
        click_count = request.args.get("click-count")
        return make_response(f"<b> URL {request.base_url} </b> has been clicked <b> {click_count} </b> times via its short URL", HTTP_OK)
    
    # request is routing to a short URL
    elif request.base_url in url_library.short_url_mapping:
        try:
            url_info = url_library.get_url(request.base_url, True) 
            return redirect(url_info[0] + f"?click-count={url_info[1]}", code=HTTP_REDIRECT)
        except KeyError as key_error:
            return make_response(f"No such short URL exists.", HTTP_CLIENT_ISSUE)
    
    else:
        return make_response(f"Unknown URL. If you intended to shorten this long URL, send to {request.host_url}shorten?url=<url> instead", HTTP_NOT_FOUND)

if __name__ == "__main__":
    port = os.getenv("PORT", "8080")
    app.run(debug=True, port=port)