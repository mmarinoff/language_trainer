import requests
from errors import LineIndexError
import re


# import list of most common verbs
r = requests.get('https://www.linguasorb.com/french/verbs/most-common-verbs/')


class GetRequest:
    """
    Semi-process html data from get request

    Attributes
        content: array containing /n delimited get request text content
        head_text: Tag Subclass
        body_text: Tag Subclass
    """
    # semi processes requests for ease of processing later
    def __init__(self, content: requests.models.Response):
        # sort content into body and head
        self.content = content.text.splitlines()  # newline delimited html page
        self.head = self.tag_scrape(self.content, 'head')[0]  # head
        self.body = self.tag_scrape(self.content, 'body', start_index=self.head.line_indices[0])[0]  # body
        self.div = self.tag_scrape(self.content, 'div')

    def __str__(self, line_indices=None, tag_indices=None):

        if line_indices:  # if self.Tag subclass
            subcontent = self.content[line_indices[0]:line_indices[1]+1]  # slice to tag lines
            # start line 0 with open tag, end line -1 with close tag
            subcontent[0] = "".join(re.split('(<[^>]*>)', subcontent[0])[1::2][tag_indices[0]:])
            subcontent[-1] = "".join(re.split('(<[^>]*>)', subcontent[-1])[1::2][:tag_indices[1]+1])
        else:
            subcontent = self.content

        return '\n'.join(subcontent)

    def tag_scrape(self, content: list, tag: str, start_index=0, tag_index=0):

        tags = ['<' + tag, '</' + tag + '>']  # open tag, close tag

        state = 0  # open tag not detected yet
        subtags = []
        line_index = start_index
        while line_index < len(content):
            line = content[line_index]

            # check for desired open/close tags in current line
            tag_detect = [tag in line for tag in tags]
            if any(tag_detect):  # desired tag detected
                line_split = re.split('(<[^>]*>)', line)[1::2]  # break line into tags

                # if first line, start at tag index, else start at first element in line
                if line_index == start_index:
                    ls = tag_index
                else:
                    ls = 0

                # loop through line sub-elements between <> braces, search for tag
                while ls < len(line_split):
                    subline = line_split[ls]

                    # open tag detected in subline
                    if tags[0] in subline:
                        # cl = re.search('.*=".*"', subline)

                        if state == 0:  # first open tag detected, store index
                            start_line_index = line_index
                            start_tag_index = ls
                            state = 1  # in case of nested tags

                        else:  # second open tag detected prior to closing tag, recursively call self
                            subtags = subtags + self.tag_scrape(content, tag, line_index, ls)

                            line_index = subtags[-1].line_indices[1]
                            ls = subtags[-1].tag_indices[1]
                            # continue search for closing tag after subtag

                    # close tag detected in line
                    if tag_detect[1] and state == 1:  # create Tag class object to store information
                        end_line_index = line_index
                        end_tag_index = ls
                        tag_instance = self.Tag(self, line_indices=(start_line_index, end_line_index),
                                                tag_indices=(start_tag_index, end_tag_index))

                        if subtags:
                            return [tag_instance] + subtags
                        else:
                            return [tag_instance]

                    ls += 1
            line_index += 1

    def tag_scan(self, content: list, tag: str, start_index=0, tag_index=0):

        line_index = start_index
        tagslist = []
        tags = True  # do at least one cycle
        while tags:
            tags = self.tag_scrape(self.content, tag, line_index, tag_index)

            if tags:
                tagslist = tagslist + tags
                tag_index = tags[0].tag_indices[1]+1
                line_index = tags[0].line_indices[1]

        return tagslist

    @staticmethod
    def tag_split(line, tag_index):
        return re.split('(<[^>]*>)', line)[1::2][tag_index:]

    class Tag:
        def __init__(self, parent: super, line_indices: tuple, tag_indices: tuple):
            self.parent = parent
            self.line_indices = line_indices
            self.tag_indices = tag_indices

        def __str__(self):
            return self.parent.__str__(self.line_indices, self.tag_indices)


gr = GetRequest(r)
abba = gr.tag_scan(gr.content, 'div')



