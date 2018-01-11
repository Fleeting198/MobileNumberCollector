import xml.etree.ElementTree as et
from .Processor import Processor


class XmlProcessor(Processor):
    def __init__(self, file, process_impl):
        super(XmlProcessor, self).__init__(file, process_impl)
        self._name = "xml processor"

    def walkData(self, root_node, result_list):
        temp_list = [root_node.tag, root_node.attrib, root_node.text]
        result_list.append(temp_list)

        # 遍历每个子节点
        children_node = root_node.getchildren()
        if len(children_node) == 0:
            return
        for child in children_node:
            self.walkData(child, result_list)
        return

    def getXmlData(self, file_name):
        result_list = []
        root = et.parse(file_name).getroot()
        self.walkData(root, result_list)

        return result_list

    def read_data(self):
        for nodes in self.getXmlData(self.file):
            for k, v in nodes[1].items():
                self._src_data.append(v)

            self._src_data.append(nodes[2])
