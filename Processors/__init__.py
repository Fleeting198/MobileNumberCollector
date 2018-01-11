import os

from .AbstractProcessors.CsvProcessor import CsvProcessor
from .AbstractProcessors.HtmlProcessor import HtmlProcessor
from .AbstractProcessors.Processor import Processor
from .AbstractProcessors.SheetProcessor import SheetProcessor
from .AbstractProcessors.TxtProcessor import TxtProcessor
from .AbstractProcessors.XmlProcessor import XmlProcessor

try:
    from .AbstractProcessors.DocProcessor import DocProcessor
except:
    docImported = False
else:
    docImported = True

from .ProcessorImpls.ProcessorMobile import ProcessorMobile
from .ProcessorImpls.ProcessorID import ProcessorID

from Utils import *


class ProcessorFactory:
    """单例工厂类"""
    _instance = None

    # ProcessorImpl类型选项，提供给外部传入构造命令时调用，或者外部也可以直接传入整数(可能放在dict里更好?)
    pro_mobile = 0
    pro_id = 1

    def __new__(cls):
        if not cls._instance:
            cls._instance = super(ProcessorFactory, cls).__new__(cls)
        return cls._instance

    def create_processor(self, file, pro_type):
        """
        工厂方法，根据文件后缀名选择实现
        :param file: 要处理的文件路径
        :param pro_type: 实例化的ProcessorImpls类型
        :return: 继承Processor的类实例
        """
        _processor_impl_dict = {0: ProcessorMobile, 1: ProcessorID}
        pro_impl = _processor_impl_dict[pro_type]()

        # .et是WPS的表格文件，可以直接把后缀名直接转成xls，然后让下面的流程处理
        if ext_in(file, ['et']):
            new_file = change_ext_to(file, 'xls')
            dir, file_name = os.path.split(new_file)
            new_file = os.path.join(dir, 'et' + file_name)
            os.renames(file, new_file)
            file = new_file

        if is_sheet_file(file):
            try:
                p = SheetProcessor(file, pro_impl)
            except Exception as e:
                # 遇到了保存为excel文件的xml文件
                if "<?xml" in str(e):
                    try:
                        p = XmlProcessor(file, pro_impl)
                    except Exception as exml:
                        raise exml

                # 遇到了保存为excel文件的html或htm文件
                elif "<html" in str(e) or 'table' in str(e):
                    try:
                        newPath = change_ext_to(file, 'htm')
                        os.renames(file, newPath)
                        p = HtmlProcessor(file, pro_impl)
                    except Exception as ehtml:
                        raise ehtml
                else:
                    raise e
        elif docImported and is_doc_file(file):
            p = DocProcessor(file, pro_impl)
        elif is_txt_file(file):
            p = TxtProcessor(file, pro_impl)
        elif is_csv_file(file):
            p = CsvProcessor(file, pro_impl)
        elif is_html_file(file):
            p = HtmlProcessor(file, pro_impl)
        else:
            # 默认Processor，会抛出没有实现的异常，源文件会被剪切到exception文件夹中
            p = Processor(file, pro_impl)

        return p
