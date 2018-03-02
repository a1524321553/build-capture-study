# coding=utf-8
# AUTHOR: CONG WANG
# DATE: 2017/3/12

from common import wfile
import commands
import os


# EXECUTE 'MAKE' IN BASH AND SAVE THE OUTPUT
def bcMake(bcc):
    script = "cd " + bcc.input_folder + " && make clean"
    (status, bash_output) = commands.getstatusoutput(script)
    if status != 0:
        print bash_output
        return -2

    script = "cd " + bcc.input_folder + " && make"
    script += " \"SHELL=" + bcc.shell + " -xv\""
    # if os.path.isfile(os.path.join(bcc.input_folder, "Makefile")):
    # script += " \"SHELL=" + bcc.shell + " -xv\" -f Makefile"
    # else:
    # script += " \"SHELL=" + bcc.shell + " -xv\" -f makefile"
    print "script: " + script

    (status, bash_output) = commands.getstatusoutput(script)
    # if status != 0:
    # print bash_output
    # return -1

    # 将make的程序输出写入到all文件中
    if wfile(bcc.all_file, bash_output) == -1:
        return -3
    bcc.line_in_all = bash_output.count("\n") + 1

    return 0
