# coding=utf-8
# AUTHOR: CONG WANG
# DATE: 2017/3/12

import shutil
import traceback
import commands
import sys
import os

# REMOVE A DIRECTORY RECUSIVELY
def removeDir(dir):
    shutil.rmtree(dir)

# WRITE STRING TO A TEXT FILE
def wfile(file, content):
    try:
        file_object = open(file, 'w')
        file_object.write(content)
        file_object.close()
    except:
        traceback.print_exc()
        return -1
    finally:
        return 1

def execcommand(dir, command):
    script = "cd " + dir + " && " + command
    (status, bash_output) = commands.getstatusoutput(script)
    if status != 0:
        print "[TYPE.5] Error in executing '" + script + "'"
        print bash_output
        sys.exit()
    return status

def hasInput(option):
    if option=="-aux-info" or option=="-include" or option == "-imacros" or option == "-iprefix" or option == "-MF" or option == "-MT" or option == "-MQ":
        return True
    else:
        return False

# 拆分line，将每个选项/参数单独保存。
def get_libfiles(line, current_dir):
    result = []
    line_array = line.split()
    for i in range(1, len(line_array)):
        if line_array[i].startswith("-"):
            if hasInput(line_array[i]):
                i += 1
                continue
        part_string = os.path.join(current_dir, line_array[i])
        result.append(os.path.abspath(part_string))
    return result
# 获取line这条gcc指令中所编译的.c源文件的文件名
def get_libfiles2(line, current_dir):
    result = []
    line_array = line.split()
    for i in range(1, len(line_array)):
        if line_array[i].startswith("-"):
            if hasInput(line_array[i]):
                i += 1
                continue
        part_string = line_array[i]
        if part_string.endswith(".c"):
            result.append(part_string)
    return result
