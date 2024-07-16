#!/usr/bin/python3

import argparse
import concurrent.futures
from operator import indexOf
import os
import random
import shutil
import subprocess
from threading import Lock
import time

useInternalCopy = True

sourcePath = ""
destinationPath = ""
csvLogFile = ""
threadCount = 16
maxFiles = 0
maxBytes = 0
blockSize = 16384

bytesCopied = 0
filesCopied = 0
filesDeleted = 0
stop = False

fastDir = False
lock = Lock()
destinationFileList = []

def updateCountersCallback(info):
    global bytesCopied

    bytesCopied += info['copiedPass']

def worker(name):
    global bytesCopied
    global filesCopied
    global stop
    global filesDeleted

    startTime = time.time()
    previousBytesCopied = 0
    previousTime =time.time()
    filesCopiedSinceDelete = 0
    
    while not stop:
        
        if name == 0:
            time.sleep(1)
            timeNow = time.time()
            timeRun = timeNow - startTime
            mbSec = (bytesCopied /timeRun) / (2 ** 20)
            mbSecInstantaneous = ((bytesCopied - previousBytesCopied) / (timeNow - previousTime)) / (2 ** 20)
            print(f"\r{time.strftime('%H:%M:%S', time.gmtime(timeRun))}: MB copied {bytesCopied / (2 **20):,.2f}, Files copied {filesCopied}, Rate {mbSec:,.2f}MB/s (overall) Rate {mbSecInstantaneous:,.2f}MB/s (instant), {filesDeleted} files deleted ", end="")

            logToCSV(f"{time.strftime('%H:%M:%S', time.gmtime(timeRun))}, {bytesCopied / (2 **20):.2f}, {filesCopied}, {mbSec:.2f},{mbSecInstantaneous:.2f}, {filesDeleted}")

            if maxFiles > 0 and filesCopied > maxFiles:
                stop = True
            elif maxBytes > 0 and bytesCopied > maxBytes:
                stop = True

            previousBytesCopied = bytesCopied
            previousTime = timeNow
        else:
            if useInternalCopy:
                picked = pickXOf(dir_list, 1)

                pickedSource = list(
                    map(
                        lambda x:
                        {
                            'source': os.path.join(sourcePath, x), 
                            'destination': os.path.join(destinationPath, x), 
                            'size': os.stat(os.path.join(sourcePath, x)).st_size
                        },
                        picked
                    )
                )[0]

                copyFileWithProgress(pickedSource['source'], pickedSource['destination'], updateCountersCallback)
                if fastDir:
                    lock.acquire()
                    destinationFileList.append(pickedSource['destination'])
                    lock.release()

                filesCopied += 1
                filesCopiedSinceDelete += 1
            else:
                result = copyXRandomFiles(sourcePath, destinationPath, dir_list, 100)

                bytesCopied += result['bytesCopied']
                filesCopied += result['filesCopied']
                filesCopiedSinceDelete += result['filesCopied']

            if filesCopiedSinceDelete > 100:
                filesDeleted += deleteXRandomFiles(destinationPath, 20)
                filesCopiedSinceDelete = 0

def logToCSV(text):
    if csvLogFile == "":
        return

    with open(csvLogFile, "a") as file_object:
        file_object.write(f"{text}\n")


def pickXOf (source, count):
    listLength = len(source)
    
    result = []

    for i in range(count):
        itemIndex = random.randint(0, listLength - 1)
        result.append(source[itemIndex])

    return result 

def deleteXRandomFiles (path, count):
    toRemove = []

    if fastDir:
        lock.acquire()
        toRemove = pickXOf(destinationFileList, count)
        lock.release()
    else:
        dir_list = os.listdir(path)

        files = pickXOf(dir_list, count)

        toRemove = list(
                map(lambda x: os.path.join(path, x), files)
            )

    removed = 0
    for i in toRemove:
        try:
            if os.path.exists(i):
                os.remove(i)
            removed += 1

            if fastDir:
                lock.acquire()
                destinationFileList.remove(i)
                lock.release()

        except FileNotFoundError:
            print("{i} not found")
            pass
        except:
            pass

    return removed

def copyXRandomFiles (sourcePath, destinationPath, fileList, count):
    picked = pickXOf(fileList, count)

    pickedSource = list(
            map(
                lambda x:
                {
                    'source': os.path.join(sourcePath, x), 
                    'destination': os.path.join(destinationPath, x), 
                    'size': os.stat(os.path.join(sourcePath, x)).st_size
                },
                picked
            )
        )

    copyCommand = list(map(lambda x: x['source'], pickedSource))
    copyCommand.insert(0, "cp")
    copyCommand.insert(1, "-vf")
    copyCommand.append(destinationPath)

    #print(' '.join(copyCommand))

    process = subprocess.Popen(copyCommand,
                        stdout=subprocess.PIPE, 
                        stderr=subprocess.PIPE)

    #print (sum(map(lambda x: x['size'], pickedSource)))

    stdout, stderr = process.communicate()

    if fastDir:
        lock.acquire()
        for item in pickedSource:
            if not item['destination'] in destinationFileList:
                destinationFileList.append(item['destination'])
        lock.release()

    return { 
        'bytesCopied': sum(map(lambda x: x['size'], pickedSource)),
        'filesCopied': count
    }

def copyFileWithProgress(source, destination, callback, length=0):
    fsrc = open(source, 'rb')

    # Open the destination file
    # in write mode and
    # get the file object
    fdst = open(destination, 'wb')
    
    # Now, copy the contents of
    # file object f1 to f2
    # using shutil.copyfileobj() method
    copyfileobj(fsrc, fdst, callback)
    
    # Close file objects
    fsrc.close()
    fdst.close()

# The below is borrowed from : https://stackoverflow.com/questions/29967487/get-progress-back-from-shutil-file-copy-thread
# Answer credit : Martijn Pieters

def copyfileobj(fsrc, fdst, callback, length=0):
    try:
        # check for optimisation opportunity
        if "b" in fsrc.mode and "b" in fdst.mode and fsrc.readinto:
            return _copyfileobj_readinto(fsrc, fdst, callback, length)
    except AttributeError:
        # one or both file objects do not support a .mode or .readinto attribute
        pass

    if not length:
        length = shutil.COPY_BUFSIZE

    fsrc_read = fsrc.read
    fdst_write = fdst.write

    copied = 0
    while True:
        buf = fsrc_read(length)
        if not buf:
            break
        fdst_write(buf)
        copied += len(buf)
        callback(copied)

# differs from shutil.COPY_BUFSIZE on platforms != Windows
READINTO_BUFSIZE = int(1024 * 1024 * 16)

def _copyfileobj_readinto(fsrc, fdst, callback, length=0):
    """readinto()/memoryview() based variant of copyfileobj().
    *fsrc* must support readinto() method and both files must be
    open in binary mode.
    """
    fsrc_readinto = fsrc.readinto
    fdst_write = fdst.write

    if not length:
        try:
            file_size = os.stat(fsrc.fileno()).st_size
        except OSError:
            file_size = READINTO_BUFSIZE
        length = min(file_size, READINTO_BUFSIZE)

    copied = 0
    with memoryview(bytearray(length)) as mv:
        while True:
            n = fsrc_readinto(mv)
            if not n:
                break
            elif n < length:
                with mv[:n] as smv:
                    fdst.write(smv)
            else:
                fdst_write(mv)
            copied += n
            callback({
                    'copied': copied,
                    'copiedPass': n
                })

parser = argparse.ArgumentParser(description="Test threaded performance of storage systems")
parser.add_argument('--source-path', help="The path from which to copy from", type=str, required=True)
parser.add_argument('--destination-path', help="The path to copy to", type=str, required=True)
parser.add_argument('--thread-count', help="The number of copy threads to run", type=int, default=16)
parser.add_argument('--max-files', help="Stop after copying this many files", type=int, default=0)
parser.add_argument('--max-gb', help="Stop after copying this many gigabytes (2^30 bytes)", type=int, default=0)
parser.add_argument('--block-size', help="The read/write block size in KB", type=int, default=16)
parser.add_argument('--csv', help="File to log telemetry", type=str, default="")
parser.add_argument('--slowdir', help="Scan the directory at the start of delete cycle", action="store_true")
args = parser.parse_args()

sourcePath = args.source_path
destinationPath = args.destination_path
threadCount = args.thread_count
maxFiles = args.max_files
maxBytes = args.max_gb * (2 ** 30)
blockSize = args.block_size * 1024
csvLogFile = args.csv
fastDir = not args.slowdir

print(
f'''
UiO Disk Performance Measurement Tool
-------------------------------------
Copying files using {threadCount} threads and {int(READINTO_BUFSIZE/1024)}kb block sizes.'''
)

if maxFiles > 0:
    print(f'Will stop after {maxFiles} copied')
elif maxBytes > 0:
    print(f'Will stop after {maxBytes / (2**30):.2f}GB copied')
else:
    print(f'No stop conditon defined, use ctrl-c')

print()

dir_list = os.listdir(sourcePath)
os.makedirs(destinationPath, exist_ok=True)

if fastDir:
    print(f'Fast directory is enabled')
    files = os.listdir(destinationPath)

    destinationFileList = list(
            map(lambda x: os.path.join(destinationPath, x), files)
        )
else:
    print(f'Fast directory is disabled')

if csvLogFile != "" and os.path.exists(csvLogFile):
    os.remove(csvLogFile)

with concurrent.futures.ThreadPoolExecutor(threadCount + 1) as executor:
        executor.map(worker, range(threadCount + 1))

print()

