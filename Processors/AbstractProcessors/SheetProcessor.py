import xlrd
from .Processor import Processor


class SheetProcessor(Processor):
    def __init__(self, file, process_impl):
        super(SheetProcessor, self).__init__(file, process_impl)
        self._name = "excel processor"

        # 用于 processByCol 的属性
        # self.maxColShift = 3  # 检测到列偏移次数大于此值时抛出异常跳过文件
        # self.bAllSheetEmpty = True
        # =====================

    # 没有用到
    @staticmethod
    def infoSheetStart(sheet):
        print("处理Sheet：{} 总行数 = {}".format(sheet.name, sheet.nrows))

    def read_data(self):
        """用xlrd读取excel文件，读取每个单元格信息到self.src_data
        (可以换用openpyxl实现)
        """

        def cell_value(wb):
            for ws in wb.sheets():
                if ws.nrows > 0:
                    for i in range(ws.nrows):
                        for j in range(ws.ncols):
                            cell_val = str(ws.cell(i, j).value)
                            yield cell_val

        # 目前打开时可能遇到编码问题而抛异常
        with xlrd.open_workbook(self.file) as wb:
            self._src_data.extend(cell_value(wb))
        return

        # def processByCol(self):
        #     """尝试直接取出列，相对遍历单元格提升效率"""
        #
        #     def guessMobileCol(sheet, startRow, nrows=20):
        #         """
        #         在sheet中，从fromRow开始遍历nrows个行，判断所有单元格，统计找出最可能是手机号的行
        #         一旦在一行中匹配到两个包含手机号的按单元格，抛出异常，放弃这个文件
        #         :param sheet:
        #         :param startRow: 开始统计的行号，从0开始
        #         :param nrows: 统计的行数
        #         """
        #         # 找0行的表格头
        #         for i in range(sheet.ncols):
        #             cellVal = str(sheet.cell(0, i).value).strip()
        #             for title in mobile_titles:
        #                 if title in cellVal:
        #                     return i
        #
        #         # 否则统计方法
        #         posCount = {}
        #         for i in range(nrows):
        #             rowId = startRow + i
        #
        #             foundMobileNumInRow = False
        #             for j in range(sheet.ncols):
        #                 cellData = sheet.cell(rowId, j)
        #                 cellVal = str(cellData.value)
        #                 if has_mobile_num(cellVal):
        #                     if not foundMobileNumInRow:
        #                         count_to_dict(posCount, j)
        #                         foundMobileNumInRow = True
        #                     else:
        #                         print(cellVal)
        #                         raise Exception('一行中匹配到多个包含手机号的单元格，行 %d，列 %d' % (rowId, j))
        #
        #         maxVal, maxKey = 0, -1
        #         for k, v in posCount.items():
        #             if v > maxVal:
        #                 maxVal = v
        #                 maxKey = k
        #
        #         # maxKey是最可能是手机号的列
        #         return maxKey
        #
        #     sumNRow = 0
        #     lastShiftPos = -1
        #     maxNotMobileCount = 20
        #
        #     with xlrd.open_workbook(self.file) as workbook:
        #         for sheet in workbook.sheets():
        #             if sheet.nrows == 0: continue
        #             self.infoSheetStart(sheet)
        #             self.bAllSheetEmpty = False
        #             sumNRow += sheet.nrows
        #
        #             nColShift = 0
        #             curRow = 0  # 这个sheet处理到的当前行
        #
        #             while curRow + 1 < sheet.nrows:
        #                 mobileCol = guessMobileCol(sheet, startRow=curRow)
        #                 if mobileCol == -1:
        #                     raise Exception('guessMobileCol寻找手机号列时失败')
        #
        #                 # print('mobile',mobileCol)
        #                 # 遍历同时判断是否是手机号，maxNotMobileCount个无法匹配，则推测是列发生变化
        #                 # 回退10个重新判断手机号列
        #                 notMobileCount = 0
        #
        #                 for i in range(sheet.nrows - curRow):
        #                     cellData = sheet.cell(curRow, mobileCol)
        #                     cellVal = str(cellData.value)
        #
        #                     if not has_mobile_num(cellVal):
        #                         notMobileCount += 1
        #
        #                         # 当累计值达到阈值，当前处理行位置倒退10个，跳出选列循环，重新找列
        #                         if notMobileCount == maxNotMobileCount:
        #                             curRow -= maxNotMobileCount
        #                             print(curRow, lastShiftPos, maxNotMobileCount, sep='  ')
        #                             if curRow == lastShiftPos:
        #                                 notMobileCount -= 1
        #                                 maxNotMobileCount += 10
        #
        #                             lastShiftPos = curRow
        #
        #                             print('出现不一致行，开始于行：%s' % str(curRow + 1))
        #
        #                             nColShift += 1
        #                             if nColShift > self.maxColShift:
        #                                 raise Exception('行偏移超过阈值，跳过文件')
        #                             break
        #
        #                     else:
        #                         notMobileCount = 0  # 有手机号时，累计值清零
        #                         self.optList.append(cellVal)
        #
        #                     # curRow += 1
