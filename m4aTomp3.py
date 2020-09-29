import os,sys

m4a_path = "/Users/Four/Documents/Music/Mine/m4a/"
mp3_path = "/Users/Four/Documents/Music/Mine/mp3/"
m4a_file = os.listdir(m4a_path)

def m4aTomp3():
    for i, m4a in enumerate(m4a_file):
        file_name = str(m4a).split(".")[0]
        cli = "ffmpeg -i " + m4a_path + m4a + " -acodec libmp3lame -aq 2 " + mp3_path + file_name + ".mp3"
        os.system(cli)
def formatName(start_tail):
    mp3_file = os.listdir(mp3_path)
    mp3_file.sort()
    for mp3 in mp3_file:
        cli = "mv " + mp3_path + mp3 + " " + mp3_path + "REC" + str(start_tail) + ".mp3"
        os.system(cli)
        start_tail += 1

def main():
    format_name = False

    for arg in sys.argv[1:]:
        if "--rename" in arg:
            start_tail = int(str(arg).split("=")[-1])
            format_name = True
    m4aTomp3()
    if format_name:
        formatName(start_tail)

if __name__ == '__main__':
    main()
