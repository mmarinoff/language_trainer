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
        #self.head = self.tag_scrape(self.content, 'head')  # head
        #self.body = self.tag_scrape(self.content, 'body', line_index=self.head.line_indices[0])  # body
        self.div = self.tag_scrape(self.content, 'div')
        print(self.div)

    def __str__(self, line_indices=None, tag_indices=None):

        if line_indices:  # if self.Tag subclass
            subcontent = self.content[line_indices[0]:line_indices[1]+1]  # slice to tag lines
            # start line 0 with open tag, end line -1 with close tag
            subcontent[0] = "".join(re.split('(<[^>]*>)', subcontent[0])[1::2][tag_indices[0]:])
            subcontent[-1] = "".join(re.split('(<[^>]*>)', subcontent[-1])[1::2][:tag_indices[1]+1])
        else:
            subcontent = self.content

        return '\n'.join(subcontent)

    def tag_scrape(self, content: list, tag: str, line_index=0, tag_index=0):

        tags = ['<' + tag, '</' + tag + '>']  # open tag, close tag

        # shift content to starting search index
        subcontent = content[line_index:]  # starting line index
        if tag_index:
            subcontent[0] = "".join(re.split('(<[^>]*>)', content[0])[1::2][tag_index:])  # starting tag index

        state = 0  # open tag not detected yet
        subtags = None
        for i, line in enumerate(subcontent):  # read through html block line by line

            # check for desired open/close tags in current line
            tag_detect = [tag in line for tag in tags]
            if any(tag_detect):  # desired tag detected
                line_split = re.split('(<[^>]*>)', line)[1::2]  # break line into tags

                if i == 0:  # absolute index stored, if first line apply shift to account for slicing above
                    abs_tag = tag_index
                else:  # not first line in selection
                    abs_line, abs_tag = 0, 0

                for j, ls in enumerate(line_split):

                    # open tag detected in line
                    if tags[0] in ls:
                        if state == 0:  # first open tag detected, store index
                            start_line_index = line_index + i
                            start_tag_index = abs_tag + j

                            state = 1  # in case of nested tags
                        else:  # second open tag detected prior to closing tag, recursively call self
                            subtags = self.tag_scrape(content, tag, start_line_index, start_tag_index + 1)
                            # continue search for closing tag after subtag


                    # close tag detected in line
                    if tag_detect[1] and state == 1:  # create Tag class object to store information
                        end_line_index = line_index + i
                        end_tag_index = abs_tag + j
                        tag_instance = self.Tag(self, line_indices=[start_line_index, end_line_index],
                                                tag_indices=[start_tag_index, end_tag_index])


                        if subtags:  # return recurred tags as list
                            if type(subtags) == self.Tag:
                                subtags = [subtags]
                            subtags.append(tag_instance)
                            return subtags
                        else:  # return single tag
                            return tag_instance

        raise LineIndexError('content', str('Tag ' + tags[state] + ' Not found in selection'))

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
for tag in gr.div:
    print(tag)
