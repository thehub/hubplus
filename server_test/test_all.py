from twill import get_browser
import unittest
import re

sites = {
    'my_dev' : 'http://pinaxdev.the-hub.net:1999/',
    'dev' : 'http://pinaxdev.the-hub.net:1955/',
    'plus_demo' : 'http://plusdemo.the-hub.net/',
    'psn_demo' : 'http://demo.psychosocialnetwork.net/',
    'psn_demo2' : 'http://pinaxdev.the-hub.net:1888/',
    }

reg = re.compile("DEBUG_STATUS=OK")
browser = get_browser()

areas = ['explore','members','groups','hubs','regions']

class TestSites(unittest.TestCase) :
    pass

def add_test(cls,site,url) :
    def test_it(self) :
        print
        print site, url
        browser.go(url)
        self.assertEquals(browser.get_code(),200)
        print "testing debug_status"
        self.assertTrue(reg.search(browser.get_html()))
        for area in areas :
            browser.go('%s%s/' % (url,area))
            self.assertTrue(reg.search(browser.get_html()))


    setattr(cls,'test_%s'%site,test_it)

for site,url in sites.iteritems() :
    add_test(TestSites,site,url)
    reg = re.compile("DEBUG_STATUS=OK")

if __name__ == '__main__' :
    unittest.main()
