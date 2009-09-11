from twill import get_browser
import unittest

sites = {
    'my_dev' : 'http://pinaxdev.the-hub.net:1999/',
    'dev' : 'http://pinaxdev.the-hub.net:1955/',
    'plus_demo' : 'http://plusdemo.the-hub.net/',
    'psn_demo' : 'http://demo.psychosocialnetwork.net/'
    }


class TestSites(unittest.TestCase) :

    def test_up(self) :
        b = get_browser()
        for site, url in sites.iteritems() :
            print site, url
            b.go(url)
            self.assertEquals(b.get_code(),200)
            b.showforms()


if __name__ == '__main__' :
    unittest.main()
