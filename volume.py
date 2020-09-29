import os, sys
import argparse

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("input", help="Input mp3 file name")
    parser.add_argument("-v", "--volume", help="volume times, eg. 2.0")
    args = parser.parse_args()

    output_volume = '2.0'
    if args.volume:
        output_volume = args.volume

    cli = "ffmpeg -i " + args.input + " -filter:a \"volume=" + output_volume + "\" tmp.mp3"
    os.system(cli)
    os.system("mv tmp.mp3 %s" %(args.input))
