from Utils import split_multi
from uniformLogger import logger


class Processor:
    """
    抽象处理器基类，其他处理器应继承此类
    处理流程在这里统一编写，先调用自己的read_data从文件中读取数据到_src_data，再调用process_impl的process_data处理数据，
    处理结果保存在_results
    子类需要覆盖实现read_data方法
    是桥接模式的抽象类
    """
    sep_chars = ['/', '\\', ',', '；', ';', '、', ' ', '\t', '，', '或']

    def __init__(self, file, process_impl):
        self._src_data = []  # 保存从文件中读取的数据
        self._results = []  # 保存处理提取出的目标数据
        self._file = file  # 此对象负责处理的目标文件
        self._process_impl = process_impl  # 持有的数据处理实现类的对象

        self._name = "default processor"  # 仅用于log，子类应覆盖

    @property
    def file(self):
        return self._file

    @property
    def results(self):
        return self._results

    @property
    def name(self):
        return self._name

    def process_file(self):
        logger.info("开始文件，路径：%s，类型：%s" % (self.file, self.name))

        self.read_data()  # 读取文件数据
        self.split_multi_target()

        # 调用桥接模式实现类实现的提取数据方法
        self._process_impl.process_data(self._src_data)
        self._results = self._process_impl.results  # 取回处理结果

        logger.info("完成文件，路径：%s，结果 %s %d个" % (self.file, self._process_impl.name, len(self.results)))

    def read_data(self):
        """桥接模式中抽象类负责实现的从文件中读取原始数据"""
        raise NotImplementedError("Default Processors, read_data not implemented.")

    def split_multi_target(self, sep_chars=sep_chars):
        buf = []
        for line in self._src_data:
            buf.extend(split_multi(line, sep_chars=sep_chars))
        self._src_data = buf
