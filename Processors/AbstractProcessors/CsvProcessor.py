import csv
from .Processor import Processor


class CsvProcessor(Processor):
    def __init__(self, file, pro_type=0):
        super(CsvProcessor, self).__init__(file, pro_type)
        self._name = "csv"

    def read_data(self):
        with open(self.file, 'r') as f:
            reader = csv.reader(f)
            for row in reader:
                self._src_data.extend([item for item in row])
