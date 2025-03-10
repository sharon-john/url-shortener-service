# url-shortener-service

Hello Actuate Team!

This repository implements a prototype of a URL shortener HTTP server as per the provided spec. It implements this in Python using the Flask microframework. All dependencies are encapsulated in a self-contained Python virtual environment. `flask` is the only non-standard library used in this project. 

## running the server 

To start the server, simply run `./start.sh` which takes one optional argument for the PORT the server will be exposed at. You might need to make this shell script executable on your machine. 

## making requests 

As detailed in the home page, this service supports 3 specially defined routes: 

1) GET / 

The home page detailing the available routes to the user. 

2) GET /shorten?url:url

The shorten route takes a full URL as its query parameter. This route will take a full URL from the user and generate a short URL and return this in its response. 

3) GET /getOriginal?url:url

The getOriginal route takes a full short URL (already shortened by the /shorten route) and returns the original long URL which was shortened in its response.

Finally,

4) GET /:anyotherroute

All other GET requests to the server are interpreted as potential short URLs which might need to be redirected to their underlying long URL origins. If the path is identified as a short URL on the server, the server will perform an HTTP 302 redirect to its corresponding origin and append the `click-count` as a query parameter to meet the extra credit requirement in the spec. **Note**: Clicks are only counted when the short URL is requested on the server. getOriginal requests and direct visits to the underlying request do not count. 

If the origin long URL is on the server, it will serve some text content, otherwise it will simply redirect with the query parameter. 

## Unit Testing 

Unit tests have been provided for the `url_shortener.py` library and can be run as follows: `python3 url_shortener_test.py`. They make use of Python's standard unittest library. 

## Assumptions and simplifications 

1) A "long" URL is simply any URL sent to the server in a GET /shorten request which could be hosted at any domain including the server domain itself. 

2) A "short" URL was interpreted as a URL hosted on the server with a 6-character path after the domain. This 6-character code is randomly generated from the base62 character set and bears no correlation with the original URL. Base62 was chosen because the more common base64 encoding contains characters that are invalid in URLs.

3) "Unique" URLs are interpreted along the lines of the HTTP RFC: with the scheme and domains being considered case-insensitive, i.e "hTTPs://WWw.exaMPle.com" and "https://www.example.com" are treated as the same URL. In addition, I also chose to treat identical query parameeters sent in any order as unique. So as long as the same domain and path are provided, a variation in the ordering of params will not affect the uniqueness of the URL. Fragments are maintained so changing the fragment at the end of a URL will result in the URL being treated as different. Schemes other than HTTP/HTTPS and domains larger than 255 characters are rejected. 

3) No persistent storage was implemented for simplicity. The short URL, long URLs, and click counts are maintained as 2 Python in-memory dictionary data structures (hash maps). This provides fast lookups to a particular long URL by its short URL and vice versa. Since this is in-memory, a reboot of the server will lose all data. An extension of this project for production would persist these data structures to disk either periodically or with write-through semantics. A key-value database such as Memcached or Redis would be ideal for this. 

Thanks for your time!



















