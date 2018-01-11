# MobileCollector

![py35][py35]

从一些常见类型的文件中用正则表达式提取手机号、身份证，输出到文本文件保存。

使用：打开MobileCollector.py，翻到文件最底部main部分，设置MobileCollector的参数，用命令行运行此脚本。或者在其他脚本中调用该类。

支持的文件类型有xls, xlsx, xlsm, doc, docx, txt, htm, csv。

读取docx文件依赖的docx库无法读取doc，目前的处理方式是先用win32com将doc另存为docx，完成后删除原doc文件，再统一处理。
win32com运行期间不能手动打开word程序，否则运行中的脚本会抛出打开文件失败的错误，而且win32com无法多进程运行。
win32com要求Python 3.5 或3.6，如果环境中没有win32com，脚本也能正常运行，但会将所有doc和docx文件视为处理失败。

Processors/AbstractProcessors中的类负责从各类型文件中读取数据到内存中，再调用ProcessorImpls处理数据。Processors/ProcessorImpls中的类负责对读取获得的数据做具体处理

## MobileCollector.py

### 说明
整个手机号提取脚本的入口类，初始化后调用process_files方法开始运行。

	MobileCollector(root_src, pro_type=0, full_core=False)

*	root_src: 待处理文件根目录路径。
*	pro_type: (可选)处理类型。手机号(0)(默认)、身份证(1)。
*	full_core: (可选)多进程用一半核或全部核，默认一半核。

调用process_files后，会在root_src同目录下新建名为complete, output, exception等文件夹，用于存储各种不同处理结果的文件。

*	complete存放成功处理的原文件，在output中有其对应的输出文件
*	output以对应每个原文件目录树的形式存放每个原文件的处理结果，处理结果是文本文件。
*	exception以及其他exception_*形式的文件夹存放因各种原因处理失败的原文件，这些需要手动处理
*	exception_encrypted: 加密文件
*	exception_noResult: 没有找到目标记录，比如处理出的手机号数是0
*	exception_codex: 因编码问题无法读取或打开

### 注意
处理结束后在原文件夹中可能还存在没处理的文件，可能是多进程导致的问题，所以可能需要反复运行，确保所有文件都被处理。

### 示例
	mobileCollector = MobileCollector(root_src=r"d:\process\source", pro_type=ProcessorFactory.pro_mobile)
	mobileCollector.process_files()

其中"d:\process\source"包含需要处理的文件,会在d:\process下新建complete, output, exception等文件夹用于区分处理结果，
所以最好确保d:\process下只存在包含待处理原文件的"source"文件夹，以免混淆输出文件。


## tools.py
包含一些用户有可能需要调用的工具方法

### merge_text
	merge_text(name, root_src, root_dest="", start_id=1, len_result_file=1000000)

将rootSource中的所有文本文件合并
行数达len_result_file时写入文件保存再准备写入一个新文件。
结果文件命名是由name+startID组成，如"name1.txt", "name2.txt", ...
*	name: 合并结果文本文件的名称部分
*	root_src: 合并来源文本文件所在的文件夹路径
*	root_dest: 合并结果文本文件保存的文件夹路径，若不指定位置，在root_src同目录下生成文件夹: mergeResult_+name
*	start_id: 合并结果文本文件的id后缀部分
*	len_result_file: 每个输出文件的最大行数

### clean_empty_folders
	clean_empty_folders(root)
删除root下所有空的文件夹，若最后root为空，保留root
*	root: 根目录

### pick_mobile
	pick_mobile(root_src, root_dest, name_exception_file)
从root下所有文本文件中将严格符合格式的手机号和可能包含手机号的行分开保存。
*	root_src: 输入文件夹路径
*	root_dest: 输出文件夹路径
*	name_exception_file: 可能包含手机号的行的保存文件名

### import_txt_to_db
	import_txt_to_db(root, table, col)
用来将结果整体去重。将root下所有文本文件中的处理结果导入数据库。
*	root: 处理结果文件所在文件夹路径
*	table: 表名
*	col: 唯一列名

### export_db_to_txt
	export_db_to_txt(rootOpt, fileOptName, table, col)
用来将结果整体去重。从数据库中将所有记录导出到多个文本文件。导出为多个文件是为了防止单个文件过大。
*	rootOpt: 保存输出文件
*	fileOptName: 输出文件名称
*	table: 表名
*	col: 唯一列名
*	batchSize: 一个文件所含行数上限


## MobileEvidenceHtmlChatFinder.py
从手机取证系统输出的html报告里提取包含传文件的聊天记录，结果写进xlsx。
要根据具体报告格式写代码，现在写了readChats1和readChats2两种。

## ReportFileGatherer.py
### 说明：
遍历报告excel文件，对每个报告，读取记录中的文件路径，从root_search中复制出来放到一个文件夹中，并计数去重后的手机号数，记录到文件

ReportFileGatherer(root_src, root_search, report_file)
*	root_src: 报告所在的目录，最好确保目录中只有报告文件
*	root_search: 
*	report_file: 输出记录文件的路径

### 示例：
	reportFileGatherer = ReportFileGatherer(r"D:\reports", r"D:\search_from",r"D:\result.txt")
	reportFileGatherer.procedure()


[py35]: https://img.shields.io/badge/python-3.5-red.svg