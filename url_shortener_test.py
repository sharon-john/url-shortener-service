import unittest
from urllib.parse import urlparse
import url_shortener 

class URLShortenerTest(unittest.TestCase):
    domain = "actuate.ai"
    short_url_path_size = 6

    def setUp(self):
        self.url_shortener = url_shortener.URLShortener(URLShortenerTest.domain)

    """Test if the shortened URL's domain matches the expected domain"""
    def test_domain_equals(self):
        actual_url = "https://actuate.ai/somelongpath"  # Dummy URL for testing
        parsed_url = urlparse(actual_url)
        expected = URLShortenerTest.domain  # Expected domain
        self.assertEqual(expected, parsed_url.netloc)

    """Test the URL shortening functionality"""
    def test_shorten_url(self):
        long_url = "https://www.example.com/hello/ok/longurl/here"

        # Generate a short URL
        shortened_now, short_url = self.url_shortener.shorten_url(long_url)
        self.assertTrue(shortened_now)

        parsed_url = urlparse(short_url)
        domain_and_path =  parsed_url.path.split("/")
        # The domain in the shortened URL should match
        self.assertEqual(URLShortenerTest.domain, domain_and_path[0])

        # The path should be URLShortener.short_url_path_size characters long
        self.assertEqual(URLShortenerTest.short_url_path_size, len(domain_and_path[1]))

        # Shortening the same URL should return the same short URL
        shortened_now2, short_url2 = self.url_shortener.shorten_url(long_url)
        self.assertFalse(shortened_now2)
        self.assertEqual(short_url, short_url2)

        # Shortening the same URL with scheme or domain in different cases should still work 
        long_url_different_case = "HTtPs://WWw.eXAmPle.com/hello/ok/longurl/here"
        shortened_now3, short_url3 = self.url_shortener.shorten_url(long_url_different_case)
        self.assertFalse(shortened_now3)
        self.assertEqual(short_url, short_url3)
    
    """Test that reordered but identical query parameters are considered the same"""
    def test_shorten_url_query_params(self):
        # query params with different orders 
        long_url_with_query_params = "https://www.example.com/hello/ok/longurl/here?query1=ok&query2=3&query3=hi"
        shortened_now, short_url = self.url_shortener.shorten_url(long_url_with_query_params)
        self.assertTrue(shortened_now)

        parsed_url = urlparse(short_url)
        domain_and_path =  parsed_url.path.split("/")
        # The domain in the shortened URL should match
        self.assertEqual(URLShortenerTest.domain, domain_and_path[0])

        # The path should be 6 characters long
        self.assertEqual(URLShortenerTest.short_url_path_size, len(domain_and_path[1]))

        long_url_with_query_params_v2 = "hTTps://wwW.example.com/hello/ok/longurl/here?query2=3&query1=ok&query3=hi"
        shortened_now2, short_url2 = self.url_shortener.shorten_url(long_url_with_query_params_v2)
        self.assertFalse(shortened_now2)
        self.assertEqual(short_url, short_url2)
    
    """ Test that the shortening works on the same domain itself"""
    def test_shorten_url_same_domain(self):
        long_url_same_domain = "https://actuate.ai/long/path/on/same/domain"
        shortened_now, short_url = self.url_shortener.shorten_url(long_url_same_domain)
        self.assertTrue(shortened_now)

        parsed_url = urlparse(short_url)
        domain_and_path =  parsed_url.path.split("/")
        # The domain in the shortened URL should match
        self.assertEqual(URLShortenerTest.domain, domain_and_path[0])

        # The path should be URLShortener.short_url_path_size characters long
        self.assertEqual(URLShortenerTest.short_url_path_size, len(domain_and_path[1]))
    
    """ The same long URL should always produce the same short URL deterministically """
    def test_shorten_url_same_url_across_instances(self):
        long_url_same_domain = "https://actuate.ai/long/path/on/same/domain"
        shortened_now, short_url = self.url_shortener.shorten_url(long_url_same_domain)
        self.assertTrue(shortened_now)

        # new instance 
        url_shortener2 = url_shortener.URLShortener(URLShortenerTest.domain)
        shortened_now2, short_url2 = url_shortener2.shorten_url(long_url_same_domain)

        self.assertTrue(shortened_now2)
        # The same long URL should produce the same shortened URL always 
        self.assertEqual(short_url, short_url2)
    
    """Test that in the unlikely event of a collision (short code already exists), we are able to produce a new valid short code"""
    def test_shorten_url_collisions(self):
        long_url_same_domain = "https://actuate.ai/long/path/on/same/domain"
        short_url_for_this = "actuate.ai/fJZlUx"

        # simulating a hash collision
        self.url_shortener.short_url_mapping[short_url_for_this] = ["https://example.com/ok", 0]
        
        # since we have a collision, we expect url shortener to append a count to it and produce a new URL
        shortened_now, short_url = self.url_shortener.shorten_url(long_url_same_domain)
        self.assertTrue(shortened_now)
        self.assertNotEqual(short_url_for_this, short_url)

        parsed_url = urlparse(short_url)
        domain_and_path =  parsed_url.path.split("/")
        self.assertEqual(URLShortenerTest.short_url_path_size, len(domain_and_path[1]))

        # now claim this short code as well and see if increment to 2 works
        del self.url_shortener.short_url_mapping[short_url]
        del self.url_shortener.long_url_mapping[long_url_same_domain]

        # jerry rig the second short code
        short_url_attempt2 = "actuate.ai/" + domain_and_path[1]
        self.url_shortener.short_url_mapping[short_url_attempt2] = ["https://example.com/ok2", 0]

        # now we will have 2 collisions when we attempt to generate this short code, we will ultimately produce the short URL for https://actuate.ai/long/path/on/same/domain2
        shortened_now2, short_url2 = self.url_shortener.shorten_url(long_url_same_domain)
        self.assertTrue(shortened_now2)
        self.assertNotEqual(short_url_for_this, short_url2)

        parsed_url = urlparse(short_url2)
        domain_and_path =  parsed_url.path.split("/")
        self.assertEqual(URLShortenerTest.short_url_path_size, len(domain_and_path[1]))

        self.assertNotEqual(short_url, short_url2)

        print(short_url, short_url2)
        
if __name__ == '__main__':
    unittest.main()
