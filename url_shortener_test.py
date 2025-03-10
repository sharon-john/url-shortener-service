import unittest
from urllib.parse import urlparse
import url_shortener 

class URLShortenerTest(unittest.TestCase):
    def setUp(self):
        self.domain = "actuate.ai"
        self.url_shortener = url_shortener.URLShortener(self.domain)

    """Test if the shortened URL's domain matches the expected domain"""
    def test_domain_equals(self):
        actual_url = "https://actuate.ai/somelongpath"  # Dummy URL for testing
        parsed_url = urlparse(actual_url)
        expected = self.domain  # Expected domain
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
        self.assertEqual(self.domain, domain_and_path[0])

        # The path should be 6 characters long
        self.assertEqual(6, len(domain_and_path[1]))

        # Shortening the same URL should return the same short URL
        shortened_now2, short_url2 = self.url_shortener.shorten_url(long_url)
        self.assertFalse(shortened_now2)
        self.assertEqual(short_url, short_url2)

        # Shortening the same URL with scheme or domain in different cases should still work 
        long_url_different_case = "HTtPs://WWw.eXAmPle.com/hello/ok/longurl/here"
        shortened_now3, short_url3 = self.url_shortener.shorten_url(long_url_different_case)
        self.assertFalse(shortened_now3)
        self.assertEqual(short_url, short_url3)
    
    def test_shorten_url_query_params(self):
        # query params with different orders 
        long_url_with_query_params = "https://www.example.com/hello/ok/longurl/here?query1=ok&query2=3&query3=hi"
        shortened_now, short_url = self.url_shortener.shorten_url(long_url_with_query_params)
        self.assertTrue(shortened_now)

        parsed_url = urlparse(short_url)
        domain_and_path =  parsed_url.path.split("/")
        # The domain in the shortened URL should match
        self.assertEqual(self.domain, domain_and_path[0])

        # The path should be 6 characters long
        self.assertEqual(6, len(domain_and_path[1]))

        long_url_with_query_params_v2 = "hTTps://wwW.example.com/hello/ok/longurl/here?query2=3&query1=ok&query3=hi"
        shortened_now2, short_url2 = self.url_shortener.shorten_url(long_url_with_query_params_v2)
        self.assertFalse(shortened_now2)
        self.assertEqual(short_url, short_url2)
    
    def test_shorten_url_same_domain(self):
        long_url_same_domain = "https://actuate.ai/long/path/on/same/domain"
        shortened_now, short_url = self.url_shortener.shorten_url(long_url_same_domain)
        self.assertTrue(shortened_now)

        parsed_url = urlparse(short_url)
        domain_and_path =  parsed_url.path.split("/")
        # The domain in the shortened URL should match
        self.assertEqual(self.domain, domain_and_path[0])

        # The path should be 6 characters long
        self.assertEqual(6, len(domain_and_path[1]))

        
if __name__ == '__main__':
    unittest.main()
