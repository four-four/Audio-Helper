import os,sys
import argparse

class Converter(object):

    def __init__(self):
        pass

    def m4aTomp3(self, filepath):
        m4a_file = os.listdir(filepath)
        for i, m4a in enumerate(m4a_file):
            tail = str(m4a).split(".")[-1]
            if 'm4a' not in tail:
                continue
            file_name_list = str(m4a).split(".")[0:-1]
            if len(file_name_list) > 1:
                file_name = '.'.join(file_name_list)
            else:
                file_name = file_name_list[0]
            cli = "ffmpeg -i " + filepath + m4a + " -acodec libmp3lame -aq 2 " + filepath + file_name + ".mp3"
            os.system(cli)
            cli = "rm -f " + filepath + m4a
            os.system(cli)

    def volume(self, filepath, output_volume):
        mp3_file = os.listdir(filepath)
        for i, mp3 in enumerate(mp3_file):
            tail = str(mp3).split(".")[1]
            if 'mp3' not in tail:
                continue
            cli = "ffmpeg -i " + filepath + mp3 + " -filter:a \"volume=" + output_volume + "\" " + filepath + "tmp.mp3"
            os.system(cli)
            os.system("mv %stmp.mp3 %s%s" %(filepath, filepath, mp3))


if __name__ == '__main__':
    converter = Converter()
    parser = argparse.ArgumentParser()
    parser.add_argument("outpath", help="dest path")
    parser.add_argument("-v", "--volume", help="volume times, eg. 2.0")
    args = parser.parse_args()
    path = args.outpath + '/'
    volume = '2.0'
    if args.volume:
        volume = args.volume
        converter.volume(path, volume)
    else:
        converter.m4aTomp3(path)


