# coding=utf-8
# AUTHOR: CONG WANG
# DATE: 2017/3/12

import re
from common import wfile


# FILTER ALL THE OUTPUT AND SAVE THE OUTPUT AS 'OUTPUT'
def bcFilter(bcc):
    output_string = ""

    # PATTERNS
    startWithPlus = re.compile("^\\+* ")
    startWithArCC = re.compile("^\\s*([/a-z0-9-_]*-)?(g?cc|ar|ld) ")
    startWithMv = re.compile("^\\s*([/a-z0-9-_]*-)?mv ")
    all_file_object = open(bcc.all_file)
    list_of_all_file = all_file_object.readlines()

    for line_in_all_file in list_of_all_file:
        if startWithPlus.match(line_in_all_file):
            # 去掉+号（re.sub()是用""替换掉line_in_all_file中匹配的部分）
            result = startWithPlus.sub("", line_in_all_file)
            if startWithArCC.match(result):
                output_string += result.lstrip()
            elif startWithMv.match(result):
                output_string += result.lstrip()
        elif line_in_all_file.startswith("make"):
            output_string += line_in_all_file.lstrip()

    if wfile(bcc.output_file, output_string) == -1:
        return -1
    bcc.line_in_output = output_string.count("\n") + 1

    return 0
