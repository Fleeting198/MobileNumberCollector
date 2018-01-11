class ProcessorImpl:
    """
    处理器实现基类，其他处理器实现应继承此类
    子类需要覆盖实现_process_data方法，实现具体的数据提取策略，本父类中调用子类的实现和其他公共处理方法
    是桥接模式的实现类
    """

    def __init__(self, remove_repeat=True, strip_pure_result=False):
        """
        :param remove_repeat: 是否执行remove_repeat方法去重
        :param strip_pure_result: 是否执行strip_pure_result方法提取目标
        """
        self._results = []  # 保存数据处理结果
        self._name = "Default ProcessorImpl"  # 仅用于log，子类应覆盖

        self.__remove_repeat = remove_repeat
        self.__strip_pure_result = strip_pure_result

    @property
    def results(self):
        return self._results

    @property
    def name(self):
        return self._name

    def process_data(self, src_data):
        self._process_data(src_data)

        if self.__remove_repeat: self.remove_repeat()
        if self.__strip_pure_result: self.strip_pure_result()

        self.check_result()

    def _process_data(self, src_data):
        """子类在这里覆盖实现对文件数据的提取策略"""
        raise NotImplementedError("Default ProcessorImpl, process_data not implemented.")

    def remove_repeat(self):
        """用set去重"""
        a = set()
        for line in self._results:
            a.add(line)
        self._results = list(a)

    def strip_pure_result(self):
        """只留下严格符合目标要求的信息，子类应覆盖"""
        raise NotImplementedError("Default ProcessorImpl, strip_pure_result not implemented.")

    def check_result(self):
        if len(self._results) == 0:
            raise Exception("Found no {}.".format(self._name))
