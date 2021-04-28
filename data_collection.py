import requests
from errors import LineIndexError
import re


class GetRequest:
    """
    Semi-process html data from get request

    Attributes
        content: array containing /n delimited get request text content
        head_text: Tag Subclass containing header line and char indices
        body_text: Tag Subclass containing body line and char indices

    Methods
        tag_search: return first block bounded by specified tag. If nested tags found, will recurse and return entire
        tree as list.
        tag_scan: exhaustive calling of tag_search. Will return Tag Subclass objects for all
        tag_split: split line by seconds bounded by <> angle brakets and return nth item.
    """
    # semi processes requests for ease of processing later
    def __init__(self, content: requests.models.Response):
        # sort content into body and head
        self.content = content.text.splitlines()  # newline delimited html page
        self.head = self.tag_search('head')[0]  # page head
        self.body = self.tag_search('body', start_index=self.head.line_indices[1])[0]  # page body

    def __str__(self, line_indices=None, tag_indices=None):

        if line_indices:  # if self.Tag subclass
            subcontent = self.content[line_indices[0]:line_indices[1]+1]  # slice to tag lines
            # start line 0 with open tag, end line -1 with close tag
            if len(subcontent) == 1:
                subcontent = ["".join(re.split('(<[^>]*>)', subcontent[0])[tag_indices[0]*2+1:tag_indices[1]*2+2])]

            else:
                subcontent[0] = "".join(re.split('(<[^>]*>)', subcontent[0])[tag_indices[0]*2+1:])
                subcontent[-1] = "".join(re.split('(<[^>]*>)', subcontent[-1])[:tag_indices[1]*2+1])
        else:
            subcontent = self.content

        return '\n'.join(subcontent)

    def tag_search(self, tag: str, start_index=0, tag_index=0):
        """
        returns first html block delimited by specified tag. In the case of nested html blocks of specified tag,
        order of return will be outside to inside, top to bottom.

        :param tag: tag being searched for (head, div, script, etc)
        :param start_index: index of starting line for html tag search
        :param tag_index: index of initial tag on starting line
        :return: list of GetRequest.Tag instances
        """

        tags = ['<' + tag + '[ ,>]', '</' + tag + '>']  # open tag regex, close tag

        state = 0  # open tag not detected yet
        subtags = []
        line_index = start_index
        while line_index < len(self.content):
            line = self.content[line_index]

            # check for desired open/close tags in current line
            tag_detect = [bool(re.search(tag, line)) for tag in tags]
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
                    if re.search(tags[0], subline):

                        if state == 0:  # first open tag detected, store index
                            start_line_index = line_index
                            start_tag_index = ls
                            state = 1  # in case of nested tags

                        else:  # second open tag detected prior to closing tag, recursively call self
                            subtags = subtags + self.tag_search(tag, line_index, ls)

                            line_index = subtags[-1].line_indices[1]
                            ls = subtags[-1].tag_indices[1]
                            # continue search for closing tag after subtag

                    # close tag detected in line
                    elif tag_detect[1] and state == 1:  # create Tag class object to store information
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

    def tag_scan(self, tag: str, start_index=0, tag_index=0):
        """
        Scan entire newline delimited html text given in content, and return list of every html block wrapped in the
        specified tag, (head, script, body, div etc.) including nested blocks. Order of return will be first to last,
        root to leaf.


        :param tag: tag being searched for (head, div, script, etc)
        :param start_index: index of starting line for html tag search
        :param tag_index: index of initial tag on starting line
        :return: list of GetRequest.Tag instances
        """

        line_index = start_index
        tagslist = []
        tags = True  # do at least one cycle
        while tags:
            tags = self.tag_search(tag, line_index, tag_index)

            if tags:  # tags returns non empty list
                tagslist += tags
                tag_index = tags[0].tag_indices[1]+1  # continue scan from last line of root tag (
                line_index = tags[0].line_indices[1]  # continue from last tag of root tag

        return tagslist

    def table_search(self, start_index=0, tag_index=0):
        # head = self.tag_search('thead', start_index=start_index, tag_index=tag_index)[0]
        # body = self.tag_search('tbody', start_index=head.line_indices[1], tag_index=head.tag_indices[0])[0]
        headers = self.tag_scan('th', start_index=284)
        for header in headers:
            print(header)


    @staticmethod
    def tag_split(line: str, tag_index: int):
        """
        return nth item in line enclosed in <> braces, where nth item is specified by tag_index
        :param line: html text string
        :param tag_index: index of desired tag block
        :return: str containing nth tag found in line
        """
        return re.split('(<[^>]*>)', line)[1::2][tag_index:]

    class Tag:
        """
        Html request text data is only stored in parent class GetRequest.context. Tag subclass defines the line and
        tag indices for html page sub-elements, such as head and body. Upon call, Tag subclass will slice relevant
        data from GetRequest.content
        """
        def __init__(self, parent: super, line_indices: tuple, tag_indices: tuple):
            """
            defines the slice limits for the relevant html block

            :param parent: instance of parent class, referenced to collect html text data
            :param line_indices: start and ending line indices for element block
            :param tag_indices: indices of first element on first line, and last element on last line of relevant block.
            """
            self.parent = parent
            self.line_indices = line_indices
            self.tag_indices = tag_indices

        def __str__(self):
            return self.parent.__str__(self.line_indices, self.tag_indices)


def data_scrape():
    # import list of most common verbs
    r = requests.get('https://www.linguasorb.com/french/verbs/most-common-verbs/')
    gr = GetRequest(r)
    print(len(gr.tag_scan('div')))
    input('stop')
    gr.table_search()


if __name__ == '__main__':
    data_scrape()




