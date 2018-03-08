# -*- coding:utf8 -*-
"""
Suricata Rules Replace

SRR is short for Suricata Rules Replace , a tool to replace the local rules by reading log file.

Author : ali0th
Date   : 18/3/7
Email  : martin2877 at foxmail.com

Usage  : python srr.py [rules file] [log file]
example: python srr.py emerging-web_specific_apps.rules log

"""

import re
import os
import sys
import time
import shutil

LOCAL_PATH = r"C:/Users/muhe/Desktop/links/tophant/suricata/nazgul-ids_prs2.1/rules/" # local rules path
TEMP_PATH = r"C:/Users/muhe/Desktop/links/wirte/Ali0thNotes/Protocols Security/script/suricata rules update management/" # temp addr for file cache
LOG_PATH = TEMP_PATH




def get_text(path, method):
    """
    three methods to get text
    1. open local file
    2. requests url
    3. read temp file first else download url
    """
    try:
        if method == 1:
            with open(path) as f:
                return f.read(), True
        elif method == 2:
            r = requests.get(path, stream=True)
            return r.text, True
        elif method == 3: 
            temp_file_name = os.path.basename(path)
            temp_file = TEMP_PATH + temp_file_name
            if os.path.exists(temp_file):
                print("file exist, opening : {0}".format(temp_file) )
                return get_text(temp_file, 1)
            else:
                print("downloading : {0}".format(path) )
                file_text, is_text = get_text(path, 2)
                with open(temp_file, "w") as f:
                    f.write(file_text)
                return file_text, True

    except Exception as e:
        return e, False


def find_regex(content, regex):
    pattern = re.compile(regex, re.I)
    match = pattern.findall(str(content))
    return match


def get_time():
    return time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())


def add_file(file1, content2):
    """
    add rules in the end
    """
    if content2 not in file1:
        return file1 + "\n\n" + content2
    else:
        return file1


def update_file(file_name, content):
    print("renaming the old file {0}".format(get_time()))
    new_name = file_name + "." + time.strftime("%Y-%m-%d-%H-%M-%S", time.localtime()) + ".old"
    if not os.path.exists(LOCAL_PATH + "/old_rules/"):
        os.mkdir(LOCAL_PATH + "/old_rules/")
    shutil.copyfile(LOCAL_PATH + file_name, LOCAL_PATH + "/old_rules/" + new_name)
    print("creating the new file {0}".format(get_time()))
    with open(LOCAL_PATH + file_name, "w") as f:
        f.write(content)


def read_log(content, method):
    """
    method:
    1. read official rule
    2. read add rule
    3. read both
    """
    if method == 1:
        regex = r'official : (.*)'
        match = find_regex(content, regex)
        return match
    elif method == 2:
        regex = r'add : (.*)'
        match = find_regex(content, regex)
        return match
    elif method == 3:
        regex = r'official : (.*)|add : (.*)'
        match = find_regex(content,regex)
        return match


def progress(num, sum):
    rate = float(num) / float(sum)
    print('progress : %.1f%% %s' % (rate * 100, get_time()))


def if_sid_in_line(file_list, content):
    if content == "\n":
        return content
    for value in file_list:
        sid = find_regex(value, r'sid:([0-9]*?);')[0]
        if sid in content:
            print("find sid line, now return : "+value)
            return value + "\n"
    return content


def start(commad, command2):
    print("="*20)
    print("process start {0} {1} {2}".format(command, command2, get_time()))
    file1, is_text1 = get_text(LOCAL_PATH + commad, 1)
    file2, is_text2 = get_text(LOG_PATH + command2, 1)
    if is_text1 and is_text2:
        # replace rules
        print("start replace the rules {0}".format(get_time()))
        file2_list = read_log(file2, 1)
        with open(LOCAL_PATH + commad, "r") as f:
            global  file_new
            file_new = ""
            lines = f.readlines()
            rate = 0
            for line in lines:
                rate += 1
                progress(rate, len(lines))
                file_new += if_sid_in_line(file2_list, line)
        # add rules
        print("start add the rules {0}".format(get_time()))
        file2_list = read_log(file2, 2)
        rate = 0
        for value in file2_list:
            file_new = add_file(file_new, value)
            rate +=1
            progress(rate, len(file2_list))
        # file update
        update_file(command, file_new)
        print("="*20)
        print("process end {0}".format(get_time()))
    else:
        print("empty file!")


if __name__ == '__main__':
    if len(sys.argv)>1:
        command = sys.argv[1]
    elif len(sys.argv)>2:
        command2 = sys.argv[2]
    else:
        command = "all"
        command2 = ""

    command = "emerging-web_specific_apps.rules"    ## 测试语句
    command2 = "log"    ## 测试语句

    start(command, command2)

