from .Processor import Processor
from html.parser import HTMLParser


class HtmlProcessor(Processor):
    class _MyHtmlParser(HTMLParser):
        def __init__(self):
            super(HtmlProcessor._MyHtmlParser, self).__init__()
            self.data = []

        def handle_data(self, data):
            self.data.append(data)

        def handle_starttag(self, tag, attrs):
            for k, v in attrs:
                self.data.append(v)

    def __init__(self, file, process_impl):
        super(HtmlProcessor, self).__init__(file, process_impl)
        self._name = "html processor"
        self.parser = self._MyHtmlParser()

    def read_data(self):
        with open(self.file, 'r') as f:
            self.parser.feed(f.read())
            self._src_data = self.parser.data
