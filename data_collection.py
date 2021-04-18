import requests
from errors import InputError


# import list of most common verbs
r = requests.get('https://www.linguasorb.com/french/verbs/most-common-verbs/')
content = r.content.splitlines()  # content body


class GetRequest:
    """
    Semi-process html data from get request

    Attributes
        head_text: array containing /n delimited header content
        body_text: array containing /n delimited body content
    """
    # semi processes requests for ease of processing later
    def __init__(self, content: requests.models.Response):
        # sort content into body and head
        html_lines = content.text.splitlines()  # newline delimited html page

        self.head_text, text_index = self.tag_scrape('head', html_lines)  # head
        self.body_text, text_index = self.tag_scrape('body', html_lines[text_index:])  # body

    def tag_scrape(self, tag: str or list, content: list, self_closing=False):

        tags = ['<' + tag, '</' + tag + '>']  # open tag, close tag

        text = []  # return text
        state = 0  # data collect false
        j = 0  # index of tags search term
        for i, line in enumerate(content):  # loop through content, collect data between tags
            # state change
            if tags[j] in line:  # tag detected
                if j == 0:  # switch data collect on
                    state = 1
                    j += 1
                else:  # switch data collect to last
                    state += 1

            if state == 1 or state == 2:
                text.append(line)
                if state == 2:
                    return text, i+1

        raise InputError('content', str('Tag ' + tags[j] + ' Not found in selection'))



gr = GetRequest(r)
for line in gr.head_text:
    print(line)
