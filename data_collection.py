import requests
from errors import TagNotFoundError
import re


class GetRequest:
    """
    Semi-process html data from get request

    Attributes
        content: array containing /n delimited get request text content
        head_text: Tag Subclass containing header block indices
        body_text: Tag Subclass containing body block indices

    Methods
        tag_search: return first block bounded by specified tag. If nested tags found, will recurse and return entire
        tree as list.
        tag_scan: exhaustive calling of tag_search. Will return Tag Subclass objects for all
        tag_split: split line by seconds bounded by <> angle brakets and return nth item.
        table_extract: will extract data from first table in selection and export to pandas Dataframe
    """
    # semi processes requests for ease of processing later
    def __init__(self, content: requests.models.Response):
        # sort content into body and head
        self.content = content.text
        self.head = self.tag_search('head')[0]  # page head
        self.body = self.tag_search('body', start=self.head.indices[1])[0]  # page body

    def __str__(self, indices=(0, None)):

        return self.content[indices[0]:indices[1]]

    def tag_search(self, tag_text: str, start=0, stop=None):
        """
        returns first html block delimited by specified tag. In the case of nested html blocks of specified tag,
        order of return will be outside to inside, top to bottom.

        :param tag_text: tag being searched for (head, div, script, etc)
        :param start: starting index
        :param stop: ending index
        :return: list of GetRequest.Tag instances
        """

        # setup
        tags = ['<' + tag_text + '[ ,>]', '</' + tag_text + '>']  # open tag regex, close tag

        state = 0  # 0 - open tag not found yet /1 - open tag found
        subtags = []  # list of tags to be returned if recursive

        if not stop:
            stop = len(self.content)

        index = start  # starting search index
        while index < stop:
            content = self.content[index:stop]

            search_open = re.search(tags[0], content)  # next open tag
            search_close = re.search(tags[1], content)  # next close tag
            if search_open and search_open.start() < search_close.start():

                # first open tag encountered
                if state == 0:
                    t_start = index + search_open.span()[0]  # save open tag positon
                    index += search_open.span()[1]  # continue search after tag
                    state = 1

                # nested open tag discovered, recurse
                else:
                    subtags += self.tag_search(tag_text, start=index)
                    index = subtags[-1].indices[1]  # continue search from end of nested call

            elif search_close:
                if state == 1:
                    t_end = index + re.search(tags[1], content).span()[1]
                    tag_instance = self.Tag(self, (t_start, t_end))

                    return [tag_instance] + subtags
                else:
                    index = index + search_close.span()[1]

            else:
                if state == 0:
                    return []
                else:
                    expression = "tag= '" + tag_text + "'"
                    message = 'At least one closing tag is missing in the current selection'
                    raise TagNotFoundError(expression, message)

    def tag_scan(self, tag_text: str, start=0, stop: int = None):
        """
        Scan entire section of html text given in content, and return list of every html block wrapped in the
        specified tag, (head, script, body, div etc.) including nested blocks. Order of return will be first to last,
        root to leaf.

        :param tag_text: tag being searched for ('head', 'div', 'script', etc)
        :param start: starting index
        :param stop: ending index
        :return: list of GetRequest.Tag instances
        """

        tagslist = []  # list of Tag subclass to return
        index = start  # starting search index
        if not stop:
            stop = len(self.content)

        while index < stop:
            ntags = self.tag_search(tag_text, index, stop)
            if ntags:
                tagslist += ntags
                index = tagslist[-1].indices[1]
            else:

                if tagslist:
                    return tagslist

                else:
                    expression = "tag= '" + tag_text + "'"
                    message = 'No instances of tag found in selection'
                    raise TagNotFoundError(expression, message)

    def table_extract(self, start_index=0, tag_index=0):
        headers = self.tag_scan('th', start_index=start_index)

        table_headers = []
        for header in headers:
            table_headers.append(self.tag_split(header.content)[2])

        table_body = []
        body = self.tag_scan('tr', start_index=header.line_indices[1], tag_index=tag_index)
        for row_block in body:
            table_row = []
            row = self.tag_scan('td', start_index=row_block.line_indices[0], tag_index=row_block.tag_indices[0])

            for cell in row:
                selection = "".join(cell.content.splitlines())
                table_row.append(re.search('>[^<>]+<', selection).group(0)[1:-1])

            table_body.append(table_row)

        print(table_body)
        input('stop')

    @staticmethod
    def tag_split(line: str, tag_index=0):
        """
        return nth item in line enclosed in <> braces, where nth item is specified by tag_index
        :param line: html text string
        :param tag_index: index of desired tag block
        :return: str containing nth tag found in line
        """
        return re.split('(<[^>]*>)', line)

    class Tag:
        """
        Html request text data is only stored in parent class GetRequest.context. Tag subclass defines the line and
        tag indices for html page sub-elements, such as head and body. Upon call, Tag subclass will slice relevant
        data from GetRequest.content
        """
        def __init__(self, parent, indices: tuple):
            """
            defines the slice limits for the relevant html block

            :param parent: instance of parent class, referenced to collect html text data
            :param indices: start and ending line indices for element block
            """
            self.__parent__ = parent
            self.indices = indices

        def __str__(self):
            return self.__parent__.__str__(self.indices)

        @property
        def content(self):
            return self.__parent__.__str__(self.indices)


def data_scrape():
    # import list of most common verbs
    r = requests.get('https://www.linguasorb.com/french/verbs/most-common-verbs/')
    gr = GetRequest(r)
    div = gr.tag_scan('div')

    # gr.table_extract(start_index=284)


if __name__ == '__main__':
    data_scrape()




