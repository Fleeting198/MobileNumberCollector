from Utils import *
from .Processor import Processor


class TxtProcessor(Processor):
    def __init__(self, file, process_impl):
        super(TxtProcessor, self).__init__(file, process_impl)
        self._name = "text processor"

    def items(self, f):
        """多种编码尝试解码，区分文本段"""
        for line in f:
            line = try_decode(line).strip()
            for e in line.split():
                for e1 in e.split(','):
                    yield e1

    def read_data(self):
        with open(self._file, 'rb') as f:
            self._src_data.extend(self.items(f))
