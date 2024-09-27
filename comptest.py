#! /usr/bin/env python3

import os
import os.path
import glob
import time

from joblib import dump, load
import lzma
import lz4
import zlib

FILEDIR='/tmp'

compfns = (
        ('lz4', lz4.frame.compress, lz4.frame.decompress),
        ('lzma', lzma.compress, lzma.decompress),
        ('zlib', zlib.compress, zlib.decompress),
        )


for comptype,compfn,decompfn in compfns:
    for fn in glob.glob('/tmp/testdata*'):
        #print(f'{comptype} compressing {fn}...')
        start = time.perf_counter()
        with open(fn, 'rb') as fd:
            data = fd.read()
        bsize = len(data) / 1024 / 1024
        #print(f'File read took {time.perf_counter()-start:.3f}secs')

        start = time.perf_counter()
        cdata = compfn(data)
        ctimer = time.perf_counter()-start
        asize = len(cdata) / 1024 / 1024
        start = time.perf_counter()
        edata = decompfn(cdata)
        etimer = time.perf_counter()-start
        print(f'{comptype}\t{fn}\tcompress: {ctimer:.3f} secs\t{round(bsize, 1)} M -> {round(asize, 1)} M\tdecompress: {etimer:.3f} secs')
        if data != edata:
            print(f'WARNING: {comptype} decompressed data not the same')

