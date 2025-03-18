import base64 
import hashlib 
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

class URLShortener:
    # salt to make it so that short URLs cannot be guessed from their long URLs even with knowledge of the hashing scheme 
    # using a hardcoded string not dependent on random properties for deterministic generation of URLs
    salt = "randomstring"

    def __init__(self, default_domain=""):
        self.long_url_mapping = dict()
        self.short_url_mapping = dict()
        self.default_domain = default_domain 
    
    def set_default_domain(self, domain):
        self.default_domain = domain 
    
    def get_default_domain(self):
        return self.default_domain

    """
    Generates a 6 character-length base64 encoded short code that represents the path in a URL
    """
    def _generate_short_code(self, url:str) -> str:
        # md5 hash the URL and salt 
        string_to_hash = url + URLShortener.salt 
        hash = hashlib.md5(string_to_hash.encode("utf-8")).digest()
        # encode the hash to url safe base64 
        bytes = base64.urlsafe_b64encode(hash)
        # finally truncate the result and choose the first 6 characters
        return bytes.decode("utf-8")[0:6]
    
    """
    Generates a new short URL using md5 and base64 if this is a newly encountered long URL
    """
    def _get_short_url(self, original_long_url:str) -> str:
      # only attempt to generate a short URL if the long URL isn't in our mapping
      if original_long_url not in self.long_url_mapping:
        short_url, long_url = "", original_long_url
        attempts = 0
        while ((short_url == "") or (short_url in self.short_url_mapping)):
            # if we encountered a collision, add a counter to the end of the long URL and retry 
            if attempts > 0:
                long_url = original_long_url + str(attempts)
            
            short_code = self._generate_short_code(long_url)
            short_url = self.default_domain.rstrip("/") + "/" + short_code
            attempts += 1 

        return short_url

    """
    Parses URL, converts case-insensitive portions to lowercase and ensures RFC constraints are followed 

    Raises Exception if URL isn't valid 
    """
    def _parse_long_url(self, long_url:str) -> tuple[urlparse, str, str]: 
        # default scheme to http and allow fragments incase user wants to link two parts of a p
        parsed_long_url = urlparse(long_url, scheme="http", allow_fragments=True)

        # scheme and domain should be case-insensitive as per DNS 
        scheme = parsed_long_url.scheme.lower() 
        domain = parsed_long_url.netloc.lower() 

        # only supporting standard HTTP URLs 
        if scheme not in ["http", "https"]:
            raise Exception("Scheme not supported by URL shortener service")
        if len(domain) < 1 or len(domain) > 255:
            raise Exception("Domain is longer than RFC permits")

        return parsed_long_url, scheme, domain 
    
    """
    Generates a new short URL if it's a new long url or fetches an existing short URL

    Raises Exception if URL isn't properly valid 
    """
    def shorten_url(self, long_url: str) -> tuple[bool, str]:
        parsed_long_url, scheme, domain = self._parse_long_url(long_url)
                            
        # query parameters should be sorted to preserve uniqueness across differently ordered but identical query parameters 
        sorted_query_params = urlencode(sorted(parse_qsl(parsed_long_url.query))) if parsed_long_url.query else ""

        # rebuild URL from components after parsing 
        long_url = urlunparse(
            (
                scheme,
                domain,
                parsed_long_url.path, 
                parsed_long_url.params,
                sorted_query_params,
                parsed_long_url.fragment
            )
        )

        # look up processed URL to see if we already have it 
        if long_url in self.long_url_mapping:
            return False, self.long_url_mapping[long_url]

        short_url = self._get_short_url(long_url)

        self.long_url_mapping[long_url] = short_url 
        # store the short url to its underlying long URL
        self.short_url_mapping[short_url] = [long_url, 0]
        return True, short_url  
    
    """
    Retrieves the long URL by short URL and increments the click count if it exists. Throws a KeyError if short URL doesn't exist.  

    Raises KeyError if passed short_url doesn't exist in map 
    """
    def get_url(self, short_url:str, increment_click_count:bool = False) -> tuple[str,int]:
        url_and_click_count = self.short_url_mapping.get(short_url, -1)
        if url_and_click_count == -1:
            raise KeyError
        
        if increment_click_count:
            self.short_url_mapping[short_url][1] += 1 

        return self.short_url_mapping[short_url]






