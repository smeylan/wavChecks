import argparse
import wavChecks

parser = argparse.ArgumentParser(description='Check status of audio file')
parser.add_argument('-if','--inputFile', help='Path to .wav file')
parser.add_argument('-n','--normalize', help='integer switch for normalization')
parser.add_argument('-t','--trim', help='integer switch for trimming')
args = parser.parse_args()


wavChecks.postProcessFile(args.inputFile)