import random 
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

class URLShortener:
    # shortened URL paths will only contain characters from the following sets: (a-z),(A-Z), (0-9)
    # other base64 characters are not URL compatible 
    lowercase_min_range = ord('a')
    lowercase_max_range = ord('z')

    uppercase_min_range = ord('A')
    uppercase_max_range = ord('Z')

    numeric_min_range, numeric_max_range = 1, 9

    def __init__(self, default_domain=""):
        self.long_url_mapping = dict()
        self.short_url_mapping = dict()
        self.default_domain = default_domain

        # build up the short url character set
        URLShortener.short_url_character_set = []
        
        # build up the character set (essentially base62) from 3 different constituent character sets 
        URLShortener.short_url_character_set.extend([chr(i) for i in range(URLShortener.lowercase_min_range, URLShortener.lowercase_max_range+1)])
        URLShortener.short_url_character_set.extend([chr(i) for i in range(URLShortener.uppercase_min_range, URLShortener.uppercase_max_range+1)])
        URLShortener.short_url_character_set.extend([str(i) for i in range(URLShortener.numeric_min_range, URLShortener.numeric_max_range+1)])
        
        # shuffle the character set for more randomization 
        random.shuffle(URLShortener.short_url_character_set)
    
    def set_default_domain(self, domain):
        self.default_domain = domain 
    
    def get_default_domain(self):
        return self.default_domain

    """
    Generates a 6 character-length base62 short code that represents the path in a URL
    """
    def _generate_short_code(self, url):
        if url not in self.long_url_mapping:
            short_code = ""
            while (len(short_code) < 6):
                short_code += random.choice(URLShortener.short_url_character_set)
        
        return short_code
    
    """
    Generates a new short URL if it's a new long url or fetches an existing short URL
    """
    def shorten_url(self, long_url):
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
                            
        # query parameters should be sorted to preserve uniqueness across differently ordered but identical query parameters 
        sorted_query_params = urlencode(sorted(parse_qsl(parsed_long_url.query))) if parsed_long_url.query else ""

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

        if long_url in self.long_url_mapping:
            return False, self.long_url_mapping[long_url]

        short_code = ""
        while (len(short_code) < 6 or short_code in self.short_url_mapping):
            short_code = self._generate_short_code(long_url)

        short_url = self.default_domain.rstrip("/") + "/" + short_code

        self.long_url_mapping[long_url] = short_url 
        # store the short url to its underlying long URL
        self.short_url_mapping[short_url] = [long_url, 0]
        return True, short_url  
    
    """
    Retrieves the long URL by short URL and increments the click count if it exists. Throws a KeyError if short URL doesn't exist.  
    """
    def get_url(self, short_url, increment_click_count = False):
        url_and_click_count = self.short_url_mapping.get(short_url, -1)
        if url_and_click_count == -1:
            raise KeyError
        
        if increment_click_count:
            self.short_url_mapping[short_url][1] += 1 

        return self.short_url_mapping[short_url]






