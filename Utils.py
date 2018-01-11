import re

re_mobile = r"1[3,5,7,8]\d{9}"
re_register = r"^1\d{14}$"
re_person_id = r"(^\d{15}$)|(^\d{17}([0-9]|X|x)$)"

mobile_compiler = re.compile(re_mobile)
register_compiler = re.compile(re_register)
person_id_compiler = re.compile(re_person_id)


def has_mobile_num(item):
    if not item: return False

    match = mobile_compiler.search(item)
    if match:
        if register_compiler.search(item):
            return False
        if person_id_compiler.search(item):
            return False
        return True

    return False


def start_with_ch(item):
    num = ""
    inum = -1
    for i in range(len(item) - 1):
        if not item[i].isdigit() and item[i + 1].isdigit():
            # num starts at i+1
            inum = i + 1
            break

    if inum > 0:
        for i in range(inum, len(item)):
            if item[i].isdigit():
                num += item[i]
            else:
                break
        return len(num) == 11
    else:
        return False


def has_person_id(item):
    item = item.strip()
    item = item.upper()

    if item.endswith('.0'):
        item = item[:-2]
    match = person_id_compiler.search(item)
    if match:
        return True
    else:
        return False


def write_list_to_file(file, l):
    with open(file, 'w', encoding='utf-8') as f:
        for e in l:
            f.write(e.strip() + '\n')


def try_decode(line):
    """
    对字符串尝试多种解码，按顺序尝试，一旦成功就返回解码结果
    :param line: 要解码的字符串
    :return:
    """
    import logging

    codes = ['utf-8', 'gbk', 'ascii', 'latin-1']
    for code in codes:
        try:
            line = line.decode(code)
        except UnicodeDecodeError:
            # logging.info("Try decode by code: {} failed".format(code))
            pass
        except:
            logging.warning("Not decodeErr raised when decode")
            raise Exception("try_decode failed: {}".format(line))
        else:
            break
    else:
        raise UnicodeDecodeError
    return line


def mobile_str_pre_process(item):
    if not item: return ""
    item = item.strip()

    replaceChars = {'０': '0', '１': '1', '２': '2', '３': '3', '４': '4', '５': '5', '６': '6', '７': '7', '８': '8',
                    '９': '9',
                    'i': '1', '@': '0', '〇': '0',
                    '①': '1', '②': '2', '③': '3', '④': '4', '⑤': '5', '⑥': '6', '⑦': '7', '⑧': '8', '⑨': '9'}
    for k, v in replaceChars.items():
        item = item.replace(k, v)

    if item.endswith('.0'):
        item = item[:-2]

    return item


def files(root):
    """
    生成器
    返回根目录root下的所有文件的文件名，忽视目录结构
    :param root: 根目录
    :return:
    """
    import os

    # cur_root 遍历到的路径，字符串
    # dirs 该路径下的文件夹，列表
    # files 该路径下的文件，列表
    for cur_root, dirs, files in os.walk(root, topdown=False):
        for name in files:
            yield os.path.join(cur_root, name)


def ext_in(file, extList):
    import os

    suffix = os.path.splitext(file)[-1][1:]
    suffix = suffix.lower()
    return suffix in extList


def is_sheet_file(file):
    return ext_in(file, ['xls', 'xlsx', 'xlsm'])


def is_doc_file(file):
    return ext_in(file, ['doc', 'docx'])


def is_txt_file(file):
    return ext_in(file, ['txt'])


def is_csv_file(file):
    return ext_in(file, ['csv'])


def is_mdb_file(file):
    return ext_in(file, ['mdb'])


def is_html_file(file):
    return ext_in(file, ['htm', 'html'])


def is_compressed_file(file):
    return ext_in(file, ['rar', 'zip', '7z'])


def change_ext_to(file, extTo):
    import os

    part1, part2 = os.path.splitext(file)
    return part1 + '.' + extTo


def count_to_dict(_dict, key, increaseValue=1):
    if key in _dict:
        _dict[key] += increaseValue
    else:
        _dict[key] = increaseValue


def search_file(fileName, root):
    fileName = '\\' + fileName
    listFiles = list(files(root))
    possibleDirs = []
    for file in listFiles:
        if file.endswith(fileName):
            possibleDirs.append(file)

    return possibleDirs


def split_multi(s, sep_chars):
    buf = []
    for char in sep_chars:
        if char in s:
            items = s.split(char)
            buf.extend(items)
            break
    else:
        buf.append(s)
    return buf


def count_unique_mobile(file):
    buf = set()
    import xlrd
    with xlrd.open_workbook(file) as workbook:
        for sheet in workbook.sheets():
            if sheet.nrows == 0: continue

            for i in range(sheet.nrows):
                for j in range(sheet.ncols):
                    cellData = sheet.cell(i, j)
                    cellVal = str(cellData.value)

                    if has_mobile_num(cellVal):
                        cellVal = mobile_str_pre_process(cellVal)
                        if 11 <= len(cellVal) <= 12:
                            buf.add(cellVal)
    return list(buf)
