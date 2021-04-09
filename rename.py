import sys
import re
import os
import argparse


def rename_mp3_files(file_path):
    mp3_files = os.listdir(file_path)
    for i, mp3 in enumerate(mp3_files):
        tail = str(mp3).split(".")[-1]
        if 'mp3' not in tail:
            continue
        file_name_list = str(mp3).split(".")[0:-1]
        if len(file_name_list) > 1:
            file_name = '.'.join(file_name_list)
        else:
            file_name = file_name_list[0]
        target_name = format_filename(file_name, i) + '.mp3'
        cli = "mv " + file_path + '/' + mp3 + " " + file_path + '/' + target_name
        os.system(cli)

def format_filename(file_name, i):
    target_name = re.sub(r' +|\(|\)|\.|\'|\"|[\d]+|[\u3002]|[\u3001]|[\u3010]|[\u3011]|[\u00b7]|[\uff1a]|[\u300a]|[\u300b]', '', file_name)
    target_name = str(i) + '_' + target_name
    return target_name


file_path = '/Users/Four/Documents/Music/Mine/mr_qi_and_ms_miao'
rename_mp3_files(file_path)