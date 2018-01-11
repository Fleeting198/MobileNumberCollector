from Utils import *

from .ProcessorImpl import ProcessorImpl


class ProcessorID(ProcessorImpl):
    def __init__(self):
        super(ProcessorID, self).__init__()
        self._name = "id"

    def _process_data(self, src_data):
        for line in src_data:
            line = line.strip()
            if has_person_id(line):
                self._results.append(line)

    def strip_pure_result(self):
        """ 用正则表达式强行提取处理结果中严格符合身份证的数据，若有包含身份证格式的非身份证数据，则可能提取出伪身份证"""
        buf = []
        for line in self._results:
            buf.extend(person_id_compiler.findall(line))
        self._results = buf
