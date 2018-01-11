import multiprocessing
import shutil, traceback, os
from time import time
from uniformLogger import logger
from Processors import ProcessorFactory, docImported
from Utils import *
from tools import clean_empty_folders


class MobileCollector:
    """
    整个手机号提取脚本的入口类，目前用桥接模式实现了其他处理方法的接口，可以增加提取身份证号或其他信息的实现类
    Processors/AbstractProcessors中的类负责从各类型文件中读取数据到内存中
    Processors/ProcessorImpls中的类负责对读取获得的数据做具体处理，如提取手机号
    """

    def __init__(self, root_src, pro_type, full_core=False):
        """
        :param root_src: 待处理文件根目录
        :param pro_type: 处理类型，如手机号、身份证，默认手机号。整数，在ProcessorFactory的类属性中
        :param full_core: 是否用全部的内核处理
        """

        self.root_src = root_src
        self.pro_type = pro_type
        self.full_core = full_core

        p1 = os.path.split(root_src)[0]

        self.root_output = os.path.join(p1, 'output')
        self.root_complete = os.path.join(p1, 'complete')

        self.root_exception = os.path.join(p1, 'exception')
        self.root_encrypted = os.path.join(p1, 'exception_encrypted')
        self.root_codec = os.path.join(p1, 'exception_codex')
        self.root_no_results = os.path.join(p1, 'exception_noResult')

        self.process_factory = ProcessorFactory()

    def process_files(self):
        """主方法，负责调用多进程"""
        start_time = time()

        # doc转换docx的情况比较特别，没法多进程，所以目前打算单独拿到流程最前面转换成docx，转换好把原始doc文件删掉，
        # 之后下面多进程再处理docx文件
        if docImported:
            print("准备将doc文件转换为docx文件\n注意：转换期间不要用word打开任何文档，否则转换会失败或终止")
            if input("输入'y'继续，输入'n'跳过doc转换步骤").lower() == 'y':
                print("开始转换")
                logger.info("Start transferring doc to docx.")
                for file in files(self.root_src):
                    self.doc_to_docx(file)

                print("准备删除转换成功的doc文件\n注意：继续前请手动备份")
                input("按任意键继续")
                print("开始删除")
                logger.info("Start deleting transferred doc file.")
                for file in files(self.root_src):
                    self.del_transferred_doc(file)

                print("准备开始正式的处理过程\n"
                      "注意：确保将源文件夹({})内剩余doc文件(应该是转换失败或转换成功后删除失败的)手动处理后再继续"
                      .format(self.root_src))
                input("按任意键继续")
        else:
            print("win32com无法导入，忽视doc和docx的处理，会剪切到{}".format(self.root_exception))

        cores = multiprocessing.cpu_count() if self.full_core else int(multiprocessing.cpu_count() / 2)  # 用满核或一半核
        pool = multiprocessing.Pool(processes=cores)

        pool.imap(self.process_file, files(self.root_src))
        pool.close()
        pool.join()

        logger.info("Done. Time spent: {}.".format(time() - start_time))

    def process_file(self, file):
        """从处理器工厂获得处理器来处理file，调用处理异常和处理成功的处理方法"""
        p = self.process_factory.create_processor(file, self.pro_type)
        try:
            p.process_file()
            path_opt = self.make_path_opt(file)
            write_list_to_file(path_opt, p.results)

        except Exception as e:
            self.handle_process_err(p, e)
        else:
            self.handle_process_suc(p)

    def handle_process_err(self, processor, err):
        # traceback.print_exc()
        logger.exception(str(err))
        file = processor.file

        # 异常，不是word的情况
        if not is_doc_file(file):
            pathCutTo = self.root_exception

            if "encrypted" in str(err):
                pathCutTo = self.root_encrypted

            elif "codec" in str(err):
                pathCutTo = self.root_codec

            elif "Found no" in str(err):
                pathCutTo = self.root_no_results

            self.cut_file_with_path(file, pathCutTo)

        # 异常，是word的情况
        else:
            try:
                self.cut_file_with_path(file, self.root_exception)
                if ext_in(file, ['doc']):
                    docxPath = change_ext_to(file, 'docx')
                    if os.path.isfile(docxPath):
                        logger.info("Remove file: {}".format(docxPath))
                        os.remove(docxPath)

            # 这个异常可能由于doc文件未被word释放时剪切文件所引发，打印时可能再次引发未知原因的异常
            except:
                try:
                    logger.exception(str(err))
                    # traceback.print_exc()
                except:
                    print("Error raised in traceback.")

    def handle_process_suc(self, processor):
        file = processor.file
        self.cut_file_with_path(file, self.root_complete)

    def cut_file_with_path(self, src, dest_root):
        """
        从root_src剪切src文件到目标根目录，保留目录树
        :param src: 要剪切的文件路径
        :param dest_root: 目标根目录
        :return:
        """
        if not os.path.isfile(src):
            print("Source file to cut from doesn't exist: {}".format(src))
            return False

        tail = src[len(self.root_src):]
        dest_path = dest_root + tail
        dir = os.path.split(dest_path)[0]

        if not os.path.isdir(dir):
            os.makedirs(dir)

        if not os.path.isfile(dest_path):
            try:
                shutil.move(src, dest_path)
            except PermissionError:
                logger.critical("PermissionError, cut failed: {}.".format(src))
                return False
        else:
            logger.warning("File already exists at destination, fromPath = {}, dest_path = {}.".format(src, dest_path))
            return False

        return True

    def make_path_opt(self, file, prefix=""):
        """
        将文件路径前的root_src部分替换为root_output，作为该文件处理结果的输出文件路径
        和原文件保持同样的目录关系
        :param file: 文件路径
        :param prefix:
        :return:
        """
        part1, ext = os.path.splitext(file)
        pathOptText = part1 + '.txt'
        pathOptText = self.root_output + pathOptText[len(self.root_src):]
        p1, p2 = os.path.split(pathOptText)
        p2 = prefix + p2
        pathOptText = os.path.join(p1, p2)

        # 可能有多个进程同时进入此代码块并尝试新建不存在的目录，第一个进程建立后，之后的进程就会触发异常，无害
        # 确保输出文件路径上的目录结构存在
        if not os.path.isdir(p1):
            try:
                os.makedirs(p1)
            except FileExistsError:
                pass

        return pathOptText

    def doc_to_docx(self, file):
        """
        若file后缀名为doc，尝试用win32com另为docx文件，以同名保存在同目录下
        :param file:
        :return:
        """
        if ext_in(file, ['doc']) and not os.path.isfile(change_ext_to(file, 'docx')):
            try:
                # 这个pro_type 必须传入，因为不处理数据，所以无所谓类别，仅为了调用DocProcessor里的另存word方法
                p = self.process_factory.create_processor(file, pro_type=ProcessorFactory.pro_mobile)
                p.doc_to_docx()
            except:
                print("Save doc as docx failed: {}.".format(file))

    def del_transferred_doc(self, file):
        """
        若file后缀名为doc，且同目录下有同名的docx文件，则删除doc文件，保留docx文件
        :param file:
        :return:
        """
        if ext_in(file, ['doc']) and os.path.isfile(change_ext_to(file, 'docx')):
            try:
                os.remove(file)
            except:
                logger.critical("Remove doc: {} failed.".format(file))


if __name__ == '__main__':
    root_src = ""
    pro_type = -1

    if not root_src:
        root_src = input("输入待处理文件夹路径：")
    if pro_type == -1:
        pro_type = int(input("选择处理类型。手机号:0，身份证号:1："))

    mobileCollector = MobileCollector(root_src=root_src, pro_type=pro_type)
    mobileCollector.process_files()

    print("开始删除空文件夹")
    clean_empty_folders(mobileCollector.root_src)
    clean_empty_folders(mobileCollector.root_output)

    print('Done.')
