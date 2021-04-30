import unittest
from unittest.mock import patch
import requests
from data_collection import *


def local_get(url):
    """
    Requests library does not support local paths, for testing purposes the LccalRequest simulates requests.get and
    returns binary content from html file in the test folder.

     to pass back to GetRequest __init__ method.
    :param url: url of site request, not used
    :return: LocalRequest instance, a requests.models.Response skeleton containing html text from local file
    """

    class LocalRequest(requests.models.Response):
        def __init__(self):
            super().__init__()
            if url == 'test_case1':
                with open('C:/Users/LPMSI00085/PycharmProjects/language_trainer/Test/HTML_Files/Case_1/'
                          'test_homepage.html', 'rb') as file:
                    self._content = file.read()
            elif url == 'test_case2':
                with open('C:/Users/LPMSI00085/PycharmProjects/language_trainer/Test/HTML_Files/Case_2/'
                          'testcase2.html', 'rb') as file:
                    self._content = file.read()

    return LocalRequest()


@patch('requests.get', local_get)  # scrape data from html files in local folder
class TestStringMethods(unittest.TestCase):

    def test_handle_remote_file(self):
        r = requests.get('test_case1')
        gr = GetRequest(r)
        self.assertEqual(len(gr.tag_scan('div')), 44, 'should be 44 instances of div blocks in test case')
        self.assertEqual(gr.head.content[:6], '<head>', 'block should begin with referenced opening tag')
        self.assertEqual(gr.body.content[-7:], '</body>', 'block should terminate with referenced closing tag')

    def test_nested_divs(self):
        r = requests.get('test_case2')
        gr = GetRequest(r)
        for i, div in enumerate(gr.tag_scan('div')):
            self.assertEqual(div.content[:15], '<div class="{}">'.format(i), 'instance number should match occurrence')


if __name__ == '__main__':
    unittest.main()