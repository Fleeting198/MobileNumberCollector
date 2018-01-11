import os
from Utils import files, write_list_to_file, try_decode, ext_in
from uniformLogger import logger


def merge_text(name, root_src, root_dest="", start_id=1, len_result_file=1000000):
    """
    将rootSource中的所有文本文件合并
    行数达len_result_file时写入文件保存再准备写入一个新文件
    结果文件命名是由name+startID组成，如"name1.txt", "name2.txt", ...
    :param name: 合并结果文本文件的名称部分
    :param root_src: 合并来源文本文件所在的文件夹路径
    :param root_dest: 合并结果文本文件保存的文件夹路径，若不指定位置，在root_src同目录下生成文件夹: mergeResult_+name
    :param start_id: 合并结果文本文件的id后缀部分
    :param len_result_file: 每个输出文件的最大行数
    """
    mergeBuffer = []

    if not root_dest:
        p1 = os.path.split(root_src)[0]
        root_dest = p1 + '\\mergeResult_' + name

    if not os.path.isdir(root_dest):
        os.makedirs(root_dest)
    else:
        logger.warning("root_dest已存在，同名合并结果文件将被覆盖")

    for file in files(root_src):
        logger.info("Reading file: {}.".format(file))
        with open(file, 'rb') as fRead:
            for line in fRead:
                line = try_decode(line).strip()
                mergeBuffer.append(line)

        while len(mergeBuffer) > len_result_file:
            mergeBufferTail = mergeBuffer[len_result_file:]
            mergeBuffer = mergeBuffer[:len_result_file]

            opt_txt_path = root_dest + '\\' + name + str(start_id) + '.txt'
            logger.info("Writing file: {}.".format(opt_txt_path))
            write_list_to_file(opt_txt_path, mergeBuffer)

            mergeBuffer = mergeBufferTail
            start_id += 1

    opt_txt_path = root_dest + '\\' + name + str(start_id) + '.txt'
    logger.info("Writing file: {}.".format(opt_txt_path))
    write_list_to_file(opt_txt_path, mergeBuffer)


def clean_empty_folders(root):
    """
    删除root下所有空的文件夹。若最后root为空，保留root
    :param root: 根目录
    """
    import os

    def try_remove_and_mark(path):
        try:
            os.rmdir(path)
        except WindowsError as e:
            raise e
        else:
            emptyFolderUrls.append(path)

    emptyFolderUrls = []
    for cur_root, dirs, files in os.walk(root, topdown=False):
        # 若当前目录下没有文件，且当前目录不是根目录
        if len(files) == 0 and cur_root != root:
            # 若没有子目录，标记并删除当前目录
            if len(dirs) == 0:
                try_remove_and_mark(cur_root)
            else:
                # 若所有子文件夹已标记为空，删除本目录并标记
                for folder in dirs:
                    folderFullPath = os.path.join(cur_root, folder)
                    if folderFullPath not in emptyFolderUrls:
                        break
                else:
                    try_remove_and_mark(cur_root)


def pick_mobile(root_src, root_dest, name_exception_file):
    """
    从root下所有文本文件中将严格符合格式的手机号和可能包含手机号的行分开保存
    :param root_src: 输入文件夹路径
    :param root_dest: 输出文件夹路径
    :param name_exception_file: 可能包含手机号的行的保存文件名
    """
    path_exception_file = root_dest + '\\' + name_exception_file

    if not os.path.isdir(root_dest):
        os.makedirs(root_dest)

    exception_buf = set()  # 缓存异常手机号

    for file in files(root_src):
        fileBuf = set()  # 缓存正常手机号
        with open(file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if len(line) == 11:  # 其实就用长度区分，因为之前处理下来，这里只要看长度就可以了。有可能要调整
                    fileBuf.add(line)
                elif len(line) > 11:
                    exception_buf.add(line)

        # 在root_dest保存相同的文件名
        file_opt_path = file[len(root_src):]
        file_opt_path = root_dest + '\\' + file_opt_path

        # 写出本文件中正常手机号
        logger.info("Writing normal mobile to file: {}.".format(file_opt_path))
        write_list_to_file(file_opt_path, fileBuf)

    logger.info("Writing exceptional mobile to file: {}.".format(path_exception_file))
    write_list_to_file(path_exception_file, exception_buf)


def connect_db():
    import pymysql
    conn = pymysql.connect(host='localhost', user='root', password='root', port=3307, local_infile=1, db='removerepeat')
    cursor = conn.cursor()
    return conn, cursor


def import_txt_to_db(root, table, col):
    """
    用来将结果整体去重
    将root下所有文本文件中的处理结果导入数据库
    :param root: 处理结果文件所在文件夹路径
    :param table: 表名
    :param col: 唯一列名
    """
    conn, cursor = connect_db()

    sql = 'load data local infile "{}" into table {}({})'
    for file in files(root):
        if not ext_in(file, ['txt']): continue
        print(file)
        _sql = sql.format(file, table, col)
        print(_sql)
        cursor.execute(_sql)
        conn.commit()


def export_db_to_txt(rootOpt, fileOptName, table, col, batchSize=1000000):
    """
    用来将结果整体去重
    从数据库中将所有记录导出到多个文本文件
    导出为多个文件是为了防止单个文件过大
    :param rootOpt: 保存输出文件
    :param fileOptName: 输出文件名称
    :param table: 表名
    :param col: 唯一列名
    :param batchSize: 一个文件所含行数上限
    """
    conn, cursor = connect_db()

    startID = 1
    sql = 'select count(*) from %s' % table
    cursor.execute(sql)
    countAll = int(cursor.fetchone()[0])
    print(countAll)

    fileID = 1
    optFileTemp = rootOpt + fileOptName + "{}.txt"
    sql = 'select {} from {} where id>={} and id<{} into outfile "{}" lines terminated by "\r\n"'

    while startID <= countAll:
        endID = startID + batchSize
        optFilePath = optFileTemp.format(fileID)
        print(startID, endID, optFilePath)
        _sql = sql.format(col, table, startID, endID, optFilePath)
        cursor.execute(_sql)
        conn.commit()

        fileID += 1
        startID = endID

    # mariadb导出成文本有空行，调用去除
    remove_empty_lines_from_opt(rootOpt)


def remove_empty_lines_from_opt(rootOpt):
    """ 打开根目录下每个文本文件，清除空行"""
    for file in files(rootOpt):
        if not ext_in(file, ["txt"]):
            continue
        buf = []
        with open(file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                if line[-1] == '\\':
                    line = line[:-1]
                buf.append(line)
        with open(file, 'w') as f:
            for line in buf:
                f.write(line + '\n')

