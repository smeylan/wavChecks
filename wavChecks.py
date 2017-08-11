from array import array
import sys
import copy
import wave
import argparse
import struct

def is_silent(data_chunk, THRESHOLD):
    """Returns 'True' if below the 'silent' threshold"""
    return max(data_chunk) < THRESHOLD

def normalize_wav(data_all, NORMALIZE_MINUS_ONE_dB, FRAME_MAX_VALUE):
    """Amplify the volume out to max -1dB"""
    # MAXIMUM = 16384
    normalize_factor = (float(NORMALIZE_MINUS_ONE_dB * FRAME_MAX_VALUE)
                        / max(abs(i) for i in data_all))
    r = array('h')
    for i in data_all:
        r.append(int(i * normalize_factor))
    return r

def trim_wav(data_all, THRESHOLD, TRIM_APPEND):
    _from = 0
    _to = len(data_all) - 1
    for i, b in enumerate(data_all):
        if abs(b) > THRESHOLD:
            _from = max(0, i - TRIM_APPEND)
            break
    for i, b in enumerate(reversed(data_all)):
        if abs(b) > THRESHOLD:
            _to = min(len(data_all) - 1, len(data_all) - 1 - i + TRIM_APPEND)
            break
    return copy.deepcopy(data_all[_from:(_to + 1)])


def postProcessFile(inputFile):
    trim = True
    normalize = True

    THRESHOLD = 2400  # audio levels not normalised.
    CHUNK_SIZE = 256
    SILENT_CHUNKS = 1 * 44100 / 1024  # about 3sec
    FRAME_MAX_VALUE = 2 ** 15 - 1
    NORMALIZE_MINUS_ONE_dB = 10 ** (-1.0 / 20)
    RATE = 44100
    CHANNELS = 1
    TRIM_APPEND = RATE / 16

    #should accept a file path as inputFile
    inputFilePath = inputFile
    inputFile = wave.open(inputFilePath, 'r')

    #get properties of the input file
    length = inputFile.getnframes()
    CHANNELS = inputFile.getnchannels()
    sample_width = inputFile.getsampwidth()
    RATE = inputFile.getframerate()

    #get an integer array representation of the input file
    rd = list()
    for i in range(0,length):
        waveData = inputFile.readframes(1)
        if len(waveData) > 2:
            sys.exit('wavChecks only handles mono audio files')
        elif (len(waveData) == 2):
            data = struct.unpack("<h", waveData)
            rd.append(int(data[0])) 

    returnDict = {}
    returnDict['silent'] = is_silent(rd, THRESHOLD)
    if returnDict['silent']:
        rfile = ''
    else:
        if trim and normalize:
            toWrite = [struct.pack("<h",x) for x in normalize_wav(trim_wav(rd,THRESHOLD, TRIM_APPEND), NORMALIZE_MINUS_ONE_dB, FRAME_MAX_VALUE)]
            print('trimmed and normalized')
        elif trim and not normalize:
            toWrite = [struct.pack("<h",x) for x in trim_wav(rd, THRESHOLD, TRIM_APPEND)]
            print('trimmed')
        elif not trim and normalize:
            toWrite = [struct.pack("<h",x) for x in normalize_wav(rd, NORMALIZE_MINUS_ONE_dB, FRAME_MAX_VALUE)]
            print('normalized')
        else:    
            toWrite = [struct.pack("<h",x) for x in rd] 
            print('raw')

        wave_file = wave.open(inputFilePath.replace('.wav','_processed.wav'), 'wb')
        wave_file.setnchannels(CHANNELS)
        wave_file.setsampwidth(sample_width)
        wave_file.setframerate(RATE)
        wave_file.writeframes(''.join(toWrite))
        wave_file.close()   

        rfile = inputFilePath.replace('.wav','_processed.wav')        
    
    return(rfile)
