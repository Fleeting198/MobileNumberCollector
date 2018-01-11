from Utils import *
from .ProcessorImpl import ProcessorImpl


class ProcessorMobile(ProcessorImpl):
    def __init__(self):
        super(ProcessorMobile, self).__init__()
        self._name = "mobile"

    def _process_data(self, src_data):
        for line in src_data:
            line = mobile_str_pre_process(line)
            if has_mobile_num(line):
                self._results.append(line)

    def strip_pure_result(self):
        """ 用正则表达式强行提取处理结果中严格符合手机号的数据，若有包含手机号格式的非手机号数据，则可能提取出伪手机号"""
        buf = []
        for line in self._results:
            buf.extend(mobile_compiler.findall(line))
        self._results = buf
