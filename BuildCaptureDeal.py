# coding=utf-8
# AUTHOR: CONG WANG
# DATE: 2017/3/12

import re
import os
import time
from common import execcommand, get_libfiles, get_libfiles2, wfile

pattern_cS = re.compile(".* -[cS] ")
pattern_nonExecutive = re.compile(".* -[cSE] ")
pattern_startWithCC = re.compile(".*^\\s*([/a-z0-9-_]*-)?(g?cc|ld).*")
pattern_out = re.compile("-o\\s+([^\\s]+)")
pattern_filename = re.compile(" (([^ ]+)\\.[c|cc|C|cxx|cpp]) ")
pattern_sorcefileSuffix = re.compile(".*\.[c|cc|C|cxx|cpp]$")
pattern_startWithAr = re.compile(".*^\\s*([/a-z0-9-_]*-)?ar ")
pattern_sharedlib = re.compile(".* -shared ")
pattern_startWithMv = re.compile("mv -f (.*?)")
intoFolder = re.compile(".*Entering directory ['\"`]([^']+)['\"`]")
outofFolder = re.compile(".*Leaving directory ['\"`]([^']+)['\"`]")
changeFolder = re.compile(".*make.*\\s+-C\\s+(.*)\\s+.*")

current_dir = ""
project_dir = ""
current_line = 0
out_folder = ""
current_task = 0
remaining_in_dir = 0
temp_dir = ""

fileMap = {}
libMap = {}
tasks = {"tasks": [], "nameToTaskNumber": {}, "number": 0}
middleTasks = []


def addFileMap(line):
    line_arr = line.split(" ")
    # 确认mv指令的有效性
    if len(line_arr) < 4:
        return
    file1 = os.path.join(current_dir, line_arr[2])
    file2 = os.path.join(current_dir, line_arr[3])
    # 如果源文件在fileMap中存有映射关系，复制源文件的映射关系，复制并保存为新文件的映射关系
    global fileMap
    if fileMap.has_key(os.path.abspath(file1)):
        fileMap[os.path.abspath(file2)] = fileMap[os.path.abspath(file1)]
    return


# 利用通过line传入的gcc指令
#   ① 在指定的位置重新编译源文件为.i文件，
#   ② 记录.c文件和.i文件的映射关系到fileMap中
# 程序的参数:
#   line是gcc指令，这条指令应是对某个/些.c文件的编译操作，但未必一定生成目标文件。
#   out_file_name用于指定生成的.i文件的位置
# 程序的返回值:
#   生成这个.i文件的gcc指令
def getPreprocessedFiles(line, out_file_name=""):
    # 如果gcc指令中所要编译的文件不是.c文件，则直接返回
    if line.find(".c ") < 0 and not line.endswith(".c") and line.find(".S") >= 0:
        print line
        print ""
        return ""
    # 否则，准备利用这条gcc指令在BCOUTPUT文件夹中生成.c对应的.i文件
    if out_file_name == "":
        new_folder = os.path.join(out_folder, "line" + str(current_line))
        os.mkdir(new_folder)
    result = line + " -E -g -O0"
    # 获取这条gcc指令所编译的.c源文件，如果在编译目录不存在，就到../BCFILES目录中去找（会有一个线程监视编译过程中的文件删除，一经有删除操作，会备份文件于BCFILES目录中）
    libs = get_libfiles2(result, current_dir)
    for lib in libs:
        if not os.path.exists(os.path.join(current_dir, lib)):
            result = result.replace(lib, "../BCFILES/" + lib)
            while (not os.path.isfile(os.path.join(current_dir, "../BCFILES/" + lib))):
                time.sleep(2)
                print "waiting for: " + os.path.join(current_dir, "../BCFILES/" + lib)
                print os.path.join(current_dir, lib)
    # 如果未指定.i文件生成位置，则将.i文件在BCOUTPUT的相应line文件夹下生成
    if out_file_name == "":
        changed_file_name = ""
        # 如果这条指令有-o，即有目标文件生成，则利用这个<目标文件的文件名>生成.i文件的文件名，并利用传入的gcc指令重新构造指令来生成这个.i文件
        if re.search(pattern_out, result):
            origin_file = re.search(pattern_out, result).group(1)
            changed_file_name = os.path.join(new_folder,
                                             os.path.basename(re.search(pattern_out, result).group(0)) + ".i")
            result = re.sub(pattern_out, "-o " + changed_file_name + " ", result, 1)
            execcommand(current_dir, result)
            if os.path.exists(os.path.abspath(changed_file_name)):
                if current_line == 111:
                    print os.path.abspath(os.path.join(current_dir, origin_file))
                # 全局维护fileMap这个字典，记录着原gcc指令中生成的目标文件（.o）与我们生成的.i文件的对应关系
                global fileMap
                fileMap[os.path.abspath(os.path.join(current_dir, origin_file))] = [os.path.abspath(changed_file_name),
                                                                                    current_line]
        # 如果这条指令中没有-o，则利用<.c等源文件的文件名>来生成.i文件的文件名
        else:
            # 首先在gcc指令中抽取所编译的源文件，即，.c, .cc, .C, .cxx, .cpp文件
            out_file_name = re.search(pattern_filename, result).group(2)
            origin_file = out_file_name
            if out_file_name.find(" -S ") >= 0:
                out_file_name += ".s"
            else:
                out_file_name += ".o"
            changed_file_name = os.path.join(new_folder, out_file_name + ".i")
            result += " -o " + changed_file_name
            execcommand(current_dir, result)
            # RECORD THE CORRESPONDING RELATION IN FILEMAP
            out_file_name = os.path.join(current_dir, out_file_name)
            if os.path.exists(os.path.abspath(changed_file_name)):
                global fileMap
                fileMap[os.path.abspath(out_file_name)] = [os.path.abspath(changed_file_name), current_line]
    # 否则直接在所指定的.i文件的生成位置生成.i文件，并且不维护fileMap
    # （维护fileMap的工作由调用本函数的上层函数去做）
    else:
        result += " -o " + out_file_name
        execcommand(current_dir, result)
    return result


# gcc通过-shared操作创建动态链接库，因此要维护libMap
def getSharedMap(line):
    output_file_name = ""
    if re.search(pattern_out, line):
        output_file_name = os.path.join(current_dir, re.search(pattern_out, line).group(1))
        line = re.sub(pattern_out, "", line)
    lib_files = get_libfiles(line, current_dir)
    global libMap
    libMap[output_file_name] = lib_files


# 利用所给的line指令——这条指令有-o操作
# ① 在BCOUTPUT目录中分配task子目录
# ② 利用line指令于task目录中生成对应源文件的.i文件，并记录源文件和.i文件的映射关系（维护fileMap）
# ③ 调取fileMap，查看目标文件（.o文件）是否还存在其他依赖文件（.i文件），如存在，拷贝至task目录中
# ④ 统计本task信息（维护tasks字典）：
#   # 维护tasks字典中的tasks字段，该字段记录所有task的信息，是个字典的数组，每个字典是一个任务task
#   tasks["tasks"].append({                             # 以字典形式记录本task信息并插入到数组中
#       "files": taskiFiles,                            # 本task所涉及到的所有.i文件
#       "linesAfterProcess": linesAfterProcess,         # 每个.i文件的代码行数（数组）
#       "size": len(linesAfterProcess),                 # .i文件数目
#       "rootDir": os.path.abspath(folder),             # 本task所在的BCOUTPUT中的task目录
#       "taskName": task_name,                          # 本task所生成的文件名
#       "allCodeLinesAfterProcess": sum(linesAfterProcess)})    #所有.i文件的总代码行数
#   })
#   # 维护tasks字典中的nameToTaskNumber字段，该字段记录<每个task所生成的文件名与task号>之间的映射关系
#   tasks["nameToTaskNumber"][task_name] = tasks["number"]
#   # 维护tasks字典中的number字段，该字段记录总的task数
#   tasks["number"] += 1
# ⑤ 如果生成的是.o文件，则记录本.o文件与本task目录之间的映射关系（维护fileMap）
# 返回值：
#   如果line中包含了-o操作，删除-o操作并返回
#   如果line中不包含-o操作，则返回空串
def getTasks(line):
    global current_task
    global fileMap
    current_task += 1
    result = ""
    task_name = ""
    # 配置本task对应于BCOUTPUT目录下的独立目录task
    folder = os.path.join(out_folder, "task" + str(current_task))
    os.mkdir(folder)
    # 用于记录本task所涉及到的.i文件
    taskiFiles = []
    # 生成函数返回值：若gcc指令涉及-o操作则返回值为删除-o操作后的指令，否则，返回值为空串
    if re.search(pattern_out, line):
        task_name = re.search(pattern_out, line).group(1)
        result = current_dir + task_name
        # 修改指令，在指令中把生成目标文件的操作（-o）删除，如：
        # gcc -DUNIX -o xxd xxd.c 修改为 -->
        # gcc -DUNIX  xxd.c
        line = re.sub(pattern_out, "", line)
    # 将line指令拆分，得到各个带有绝对路径的.o文件名，拆分后出现的“地址+gcc操作”会在后续过滤掉
    part_string = get_libfiles(line, current_dir)
    # 处理上面的结果（part_string）：
    processed_file = {}
    for i in range(len(part_string)):
        temp_string = part_string[i]
        # 对part_string去重
        if processed_file.has_key(temp_string):
            part_string[i] = None
            continue
        else:
            processed_file[temp_string] = 1
        # 利用libMap文件，对在libMap中出现的文件，直接导出并替换到part_string中来
        if libMap.has_key(temp_string):
            part_string[i] = None
            ofile_strings = libMap.get(temp_string)
            for j in range(len(ofile_strings)):
                part_string.append(ofile_strings[j])
    # newLine获取到line指令中除去.o和.c文件的剩余部分
    newLine = ""
    line_parts = line.split(" ")
    for line_part in line_parts:
        if not line_part.endswith(".o") and not line_part.endswith(".c"):
            newLine += line_part + " "
    line += " "
    # 对line中涉及到的所有源文件（.c, .cc, .C, .cxx, .cpp），
    # ① 利用原指令的选项，在BCOUTPUT文件夹下的task目录中生成对应源文件的.i文件
    # ② 记录源文件和task目录中的.i文件的映射关系（维护fileMap）
    for outs in re.findall(pattern_filename, line):
        # " (([^ ]+)\\.[c|cc|C|cxx|cpp]) "
        #   re.findall()，如果正则中存在括号，则返回括号内的匹配结果，否则返回整个结果
        #   如果存在多个括号，则每次匹配返回一个元组，按照括号的顺序依次匹配返回
        #   这里outs取回的是re.findall()的一个匹配结果，是一个元组
        #   故，outs[0]是第一个括号的结果，是文件全名，outs[1]是第二个括号的结果，是不带后缀的名
        out_file_name = outs[0]
        outFileNameWithoutSuffix = outs[1]
        # 截取出相对文件名
        iter = len(outFileNameWithoutSuffix) - 1
        while iter >= 0 and outFileNameWithoutSuffix[iter] != '/':
            iter -= 1
        outFileNameWithoutSuffix = outFileNameWithoutSuffix[(iter + 1):]
        # 维护fileMap映射关系：编译路径的源文件--task目录中的.i文件
        fileMap[os.path.abspath(os.path.join(current_dir, out_file_name))] = [
            os.path.abspath(os.path.join(folder, outFileNameWithoutSuffix + ".i")), current_line]
        # 重构指令：利用原line中的选项来编译这个源文件
        tmpNewLine = newLine + " " + out_file_name
        # 将指令传入getPreprocessedFiles()
        #   ① 修改指令并生成.c对应的.i文件
        #   ② 记录.c和.i文件的映射关系于fileMap中
        getPreprocessedFiles(tmpNewLine, os.path.join(folder, outFileNameWithoutSuffix + ".i"))
        # 将本task的.i文件存入taskiFiles中
        taskiFiles.append(os.path.abspath(folder + "/" + outFileNameWithoutSuffix + ".i"))
    # 创建拷贝指令：
    #   拷贝fileMap中记录的<本line所指定的.o文件在BCOUTPUT文件夹中对应的.i文件>到task目录中
    commands = []
    for i in range(len(part_string)):
        temp_string = part_string[i]
        if temp_string == None:
            continue
        # 筛选出不是.c, .cc, .C, .cxx, .cpp的文件
        if not re.search(pattern_sorcefileSuffix, temp_string):
            # 排除这些文件中，不是.o文件的文件，留下.o文件
            if not temp_string.endswith(".o"):
                continue
            # 排除在fileMap中找不到的.o文件
            if not fileMap.has_key(os.path.join(current_dir, temp_string)):
                continue
            # 利用fileMap，找到编译路径中.o文件对应于BCOUTPUT文件夹中的.o.i文件
            temp_string = fileMap[os.path.join(current_dir, temp_string)][0]
            # 如果.o文件在fileMap中直接对应.i文件，则直接改名并拷贝至task目录：
            if temp_string.endswith(".i"):
                task_file_name = temp_string
                # 截断两次，获取.o.i文件的文件名（父目录/文件名），如：'line2/arabic.o.i'
                iter = len(task_file_name) - 1
                while iter >= 0 and task_file_name[iter] != '/':
                    iter -= 1
                iter -= 1
                while iter >= 0 and task_file_name[iter] != '/':
                    iter -= 1
                task_file_name = task_file_name[iter + 1:]
                # 拷贝目标文件到BCOUTPUT文件夹中的task目录中
                task_file_name = task_file_name.replace("/", "-")
                taskiFiles.append(os.path.abspath(folder + "/" + task_file_name))
                commands.append("cp -f " + temp_string + " " + folder + "/" + task_file_name)
            # 如果.o文件在fileMap中对应的是一个目录，则对目录下所有（.i）文件，改名并拷贝至task目录
            elif os.path.isdir(temp_string):
                temp_dir = temp_string
                temp_files = os.listdir(temp_string)
                for temp_filename in temp_files:
                    temp_string = os.path.join(temp_dir, temp_filename)
                    task_file_name = temp_string
                    iter = len(task_file_name) - 1
                    while iter >= 0 and task_file_name[iter] != '/':
                        iter -= 1
                    iter -= 1
                    while iter >= 0 and task_file_name[iter] != '/':
                        iter -= 1
                    task_file_name = task_file_name[iter + 1:]
                    task_file_name = task_file_name.replace("/", "-")
                    taskiFiles.append(os.path.abspath(folder + "/" + task_file_name))
                    commands.append("cp -f " + temp_string + " " + folder + "/" + task_file_name)
                # 待注释
                global tasks
                for i in tasks['tasks']:
                    if i['rootDir'] == temp_dir:
                        global middleTasks
                        middleTasks.append(i['taskName'])
                        break
    # 上一步中如果有拷贝指令，则先执行拷贝指令，再统计task信息，存入tasks中
    if len(commands) > 0:
        executeResult = True
        for i in commands:
            execcommand(current_dir, i)
        # 开始统计这个task的相关信息
        global tasks
        linesAfterProcess = []
        # 统计该task中.i文件的代码行数
        for taskfile in taskiFiles:
            filename = taskfile
            myfile = open(filename)
            lines = len(myfile.readlines())
            linesAfterProcess.append(lines)
        # 将task所包含的.i文件名，.i文件的根目录（即task），代码行数信息写入到tasks数据结构中
        tasks["tasks"].append(
            {"files": taskiFiles, "linesAfterProcess": linesAfterProcess, "size": len(linesAfterProcess),
             "rootDir": os.path.abspath(folder), "taskName": task_name,
             "allCodeLinesAfterProcess": sum(linesAfterProcess)})
        tasks["nameToTaskNumber"][task_name] = tasks["number"]
        tasks["number"] += 1
    # 如果没有拷贝指令，则直接统计task信息
    else:
        global tasks
        linesAfterProcess = []
        for taskfile in taskiFiles:
            filename = taskfile
            myfile = open(filename)
            lines = len(myfile.readlines())
            linesAfterProcess.append(lines)
        tasks["tasks"].append(
            {"files": taskiFiles, "linesAfterProcess": linesAfterProcess, "size": len(linesAfterProcess),
             "rootDir": os.path.abspath(folder), "taskName": task_name,
             "allCodeLinesAfterProcess": sum(linesAfterProcess)})
        tasks["nameToTaskNumber"][task_name] = tasks["number"]
        tasks["number"] += 1
    # 如果task的目标是生成.o文件，则要维护fileMap：将".o文件:对应task目录"插入到fileMap字典中
    # 注：fileMap维护的是文件依赖关系：
    #   在gcc涉及编译指令时，向其插入.o与line文件夹内.o.i文件映射关系
    #   在gcc不涉及编译指令时，即为task指令（如链接等操作），向其插入.o与task文件夹内.o.i文件映射关系
    if task_name.endswith(".o"):
        global fileMap
        fileMap[os.path.abspath(os.path.join(current_dir, task_name))] = [os.path.abspath(folder), current_line]
    return result


# 分析ar指令，维护middleTasks列表和libMap字典
# ① 将被打包的文件的文件名存入middleTasks中
# ② 建立打包后文件与被打包文件（列表）之间的映射关系，存入libMap
# 附：AR
#   ar命令是Linux的一个备份压缩命令
#   可以创建、修改备存文件(archive)，或从备存文件中抽取成员文件。
#   常见的应用是，使用ar命令将多个目标文件（*.o）打包为静态链接库文件（*.a）。
def getLibMap(line):
    part_strings = line.split()
    # 确保指令的有效性
    if len(part_strings) < 4:
        return
    # 获取打包的输出文件名
    output_file_name = os.path.join(current_dir, part_strings[2])
    # 统计被打包的文件
    input_file_names = []
    iter = 3
    global middleTasks
    while iter < len(part_strings):
        middleTasks.append(part_strings[iter])
        input_file_names.append(os.path.join(current_dir, part_strings[iter]))
        iter += 1
    # 维护libMap，将打包后的文件与被打包的文件建立起映射关系存入libMap中
    global libMap
    libMap[output_file_name] = input_file_names


# 通过分析gcc指令，根据指令类型对其分类，分别处理
def parse(line):
    global current_dir
    global remaining_in_dir
    global temp_dir
    if changeFolder.match(line):
        if remaining_in_dir == 0:
            temp_dir = current_dir
        remaining_in_dir += 1
        current_dir = os.path.join(project_dir, changeFolder.match(line).group(1))
        return ""
    else:
        remaining_in_dir -= 1
    if intoFolder.match(line):
        current_dir = intoFolder.match(line).group(1)
        if remaining_in_dir == 0:
            current_dir = temp_dir
        return ""
    if outofFolder.match(line):
        current_dir = os.path.dirname(outofFolder.match(line).group(1))
        if remaining_in_dir == 0:
            current_dir = temp_dir
        return ""
    # 如果指令是gcc操作指令或ld操作指令
    if pattern_startWithCC.match(line):
        if line.endswith("'"):
            if remaining_in_dir == 0:
                current_dir = temp_dir
            return ""
        elif pattern_sharedlib.match(line):
            getSharedMap(line)
            if remaining_in_dir == 0:
                current_dir = temp_dir
            return ""
        # 如果指令的选项是-c或-S，即要对源文件进行编译操作，则通过该指令获取.i文件
        # -c:编译、汇编到目标代码，不进行链接
        # -S:仅编译到汇编语言，不进行汇编和链接
        elif pattern_cS.match(line):
            result = getPreprocessedFiles(line)
            if remaining_in_dir == 0:
                current_dir = temp_dir
            return result
        # 如果指令的选项不是-c或-S或-E，则该指令为链接等用于生成目标文件的操作，则获取task
        # -E:仅作预处理，不进行编译、汇编和链接
        elif not pattern_nonExecutive.match(line):
            result = getTasks(line)
            if remaining_in_dir == 0:
                current_dir = temp_dir
            return result
    # Linux的AR打包命令，用于创建动态链接库
    if pattern_startWithAr.match(line):
        getLibMap(line)
        if remaining_in_dir == 0:
            current_dir = temp_dir
        return ""
    # 更名操作
    if pattern_startWithMv.match(line):
        addFileMap(line)
        return ""
    if remaining_in_dir == 0:
        current_dir = temp_dir
    return ""


# libMap的规范化输出
def standard(curr_map):
    result = "{"
    for key in curr_map:
        if result != "{":
            result += "\n, "
        result += key + "=["
        tmp_files = ""
        for tmp_file in curr_map[key]:
            if tmp_files != "":
                tmp_files += ", "
            tmp_files += tmp_file
        result += tmp_files + "]"
    result += "}"
    return result


# fileMap的标准化输出
def standard2(curr_map):
    result = "{"
    for key in curr_map:
        result += key + "=( ABSOLUTE_FILE_PATH: " + curr_map[key][0] + " ,  LINE_NUMBER: " + str(
            curr_map[key][1]) + "),\n"
    result += "}"
    return result


def bcDeal(bcc):
    global current_dir
    global out_folder
    global project_dir
    global current_line
    global fs_folder
    current_dir = bcc.input_folder
    project_dir = bcc.input_folder
    out_folder = bcc.output_folder
    fs_folder = bcc.fs_folder
    output_string = ""
    # 读取过滤后的make输出
    output_file_object = open(bcc.output_file)
    all_the_text = output_file_object.read()
    list_of_output_file = all_the_text.split("\n")
    # 对每条make输出语句进行分析
    for line_in_output_file in list_of_output_file:
        current_line += 1
        if current_line % 500 == 0:
            print current_line
        # print current_line,
        # print line_in_output_file
        blacklist = []
        #	if current_line > 141:
        #		continue
        # if current_line < 16833:
        # 	continue
        # if current_line in blacklist:
        # continue
        # if line_in_output_file.find('elf_i386') >= 0:
        # continue
        lines_array = line_in_output_file.split(";")
        for lines_a in lines_array:
            # 注意以" -+ "形式出现的参数
            lines_end = lines_a.find(" -+ ")
            if lines_end >= 0:
                lines_a = lines_a[:lines_end]
            output_string += parse(lines_a) + "\n"

    wfile(out_folder + "/outputParsing", output_string)
    wfile(out_folder + "/libMap", standard(libMap))
    wfile(out_folder + "/fileMap", standard2(fileMap))
    finalTasks = []
    for i in tasks['tasks']:
        if i['taskName'] in middleTasks:
            continue
        if i['taskName'] == "":
            continue
        finalTasks.append(i)
    tasks['tasks'] = finalTasks
    wfile(out_folder + "/tasks.json", str(tasks))
