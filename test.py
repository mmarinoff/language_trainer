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
            with open('C:/Users/LPMSI00085/PycharmProjects/language_trainer/Test/HTML_Files/Case_1/'
                      '100 Most Common French Verbs - Linguasorb.html', 'rb') as file:
                self._content = file.read()

    return LocalRequest()


class TestStringMethods(unittest.TestCase):

    @patch('requests.get', local_get)  # scrape data from html files in local folder
    def test_handle_remote_file(self):
        data_scrape()


if __name__ == '__main__':
    unittest.main()