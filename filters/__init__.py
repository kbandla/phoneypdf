'''
PDF Filters
This file is part of the phoneyPDF Framework

Kiran Bandla <kbandla@intovoid.com>

Copyright (c) 2013, VERISIGN, Inc

All rights reserved.

Redistribution and use in source and binary forms, with or without modification,
are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice,
      this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright notice,
      this list of conditions and the following disclaimer in the documentation
      and/or other materials provided with the distribution.
    * Neither the name of VERISIGN nor the names of its contributors
      may be used to endorse or promote products derived from this software
      without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
"AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
'''
import cStringIO

# Implementation of various PDF Filters
#
# Arbitrary Decoders:
#   1. FlateDecode      -   Yes
#   2. LZWDecode        -   Yes
#   3. RunLengthDecode  -   Yes
#
# Image Decoders:
#   1. JBIG2-Decode     -   No
#   2. CCITTFaxDecode   -   No
#   3. DCTDecode        -   No
#   4. JPXDecode        -   No
#
# 8-bit ASCII Decoders:
#   1. ASCIIHexDecode   -   Yes
#   2. ASCII85Decode    -   Yes
#
# Others
#   1. Crypt            -   No

# http://code.google.com/p/pdfminerr/source/browse/trunk/pdfminer/pdfminer/ascii85.py
def ASCII85Decode(data):
  import struct
  n = b = 0
  out = ''
  for c in data:
    if '!' <= c and c <= 'u':
      n += 1
      b = b*85+(ord(c)-33)
      if n == 5:
        out += struct.pack('>L',b)
        n = b = 0
    elif c == 'z':
      assert n == 0
      out += '\0\0\0\0'
    elif c == '~':
      if n:
        for _ in range(5-n):
          b = b*85+84
        out += struct.pack('>L',b)[:n-1]
      break
  return out

def ASCIIHexDecode(data):
    import binascii
    return binascii.unhexlify(''.join([c for c in data if c not in ' \t\n\r']).rstrip('>'))

def FlateDecode(data):
    import zlib
    return zlib.decompress(data)

def RunLengthDecode(data):
    f = cStringIO.StringIO(data)
    decompressed = ''
    runLength = ord(f.read(1))
    while runLength:
        if runLength < 128:
            decompressed += f.read(runLength + 1)
        if runLength > 128:
            decompressed += f.read(1) * (257 - runLength)
        if runLength == 128:
            break
        runLength = ord(f.read(1))
#    return sub(r'(\d+)(\D)', lambda m: m.group(2) * int(m.group(1)), data)
    return decompressed

#### LZW code sourced from pdfminer
# Copyright (c) 2004-2009 Yusuke Shinyama <yusuke at cs dot nyu dot edu>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated
# documentation files (the "Software"), to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

class LZWDecoder(object):
    def __init__(self, fp):
        self.fp = fp
        self.buff = 0
        self.bpos = 8
        self.nbits = 9
        self.table = None
        self.prevbuf = None
        return

    def readbits(self, bits):
        v = 0
        while 1:
            # the number of remaining bits we can get from the current buffer.
            r = 8-self.bpos
            if bits <= r:
                # |-----8-bits-----|
                # |-bpos-|-bits-|  |
                # |      |----r----|
                v = (v<<bits) | ((self.buff>>(r-bits)) & ((1<<bits)-1))
                self.bpos += bits
                break
            else:
                # |-----8-bits-----|
                # |-bpos-|---bits----...
                # |      |----r----|
                v = (v<<r) | (self.buff & ((1<<r)-1))
                bits -= r
                x = self.fp.read(1)
                if not x: raise EOFError
                self.buff = ord(x)
                self.bpos = 0
        return v

    def feed(self, code):
        x = ''
        if code == 256:
            self.table = [ chr(c) for c in xrange(256) ] # 0-255
            self.table.append(None) # 256
            self.table.append(None) # 257
            self.prevbuf = ''
            self.nbits = 9
        elif code == 257:
            pass
        elif not self.prevbuf:
            x = self.prevbuf = self.table[code]
        else:
            if code < len(self.table):
                x = self.table[code]
                self.table.append(self.prevbuf+x[0])
            else:
                self.table.append(self.prevbuf+self.prevbuf[0])
                x = self.table[code]
            l = len(self.table)
            if l == 511:
                self.nbits = 10
            elif l == 1023:
                self.nbits = 11
            elif l == 2047:
                self.nbits = 12
            self.prevbuf = x
        return x

    def run(self):
        while 1:
            try:
                code = self.readbits(self.nbits)
            except EOFError:
                break
            x = self.feed(code)
            yield x
        return

def LZWDecode(data):
    return ''.join(LZWDecoder(cStringIO.StringIO(data)).run())

def hex_decode(name):
    '''
    Hex-Decode a key name
    Example : '/E#6dbed#64#65#64Fi#6c#65 -> /EmbeddedFile
    '''
    a = []
    fixed_name = ''
    found = False
    found_length = 0
    #tokens = enumerate(name)

    for token in name:
        if (found == False) and (token !='#'):
            fixed_name += token
        elif (found == False) and (token == '#'):
            # We just saw a #
            found = True
        elif (found == True) and (token != '#'):
            # We saw a token after #
            if found_length <2  :
                a.append(token)
                found_length += 1
            else:
                found = False
                fixed_name += chr(int(''.join(a),16))
                found_length = 0
                a = []
                fixed_name += token
        elif (found== True) and (token == '#'):
            # We saw a new # after consuming tokens
            found_length = 0
            fixed_name += chr(int(''.join(a),16))
            a = []
        else:
            fixed_name += token
            found = False
    if a:
        fixed_name += chr(int(''.join(a),16))
    return fixed_name




# Abbreviations
AHx =   ASCIIHexDecode
A85 =   ASCII85Decode
LZW =   LZWDecode
Fl  =   FlateDecode
RL  =   RunLengthDecode

# TODO
#CCF =   CCITTFaxDecode
#DCT =   DCTDecode

##########################################################################################
# PDFDocEncoding - Ripped from pyPDF's code
# All releases of pyPdf are distributed under the terms of a modified BSD license.
_pdfDocEncoding = (
  u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000',
  u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000',
  u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000', u'\u0000',
  u'\u02d8', u'\u02c7', u'\u02c6', u'\u02d9', u'\u02dd', u'\u02db', u'\u02da', u'\u02dc',
  u'\u0020', u'\u0021', u'\u0022', u'\u0023', u'\u0024', u'\u0025', u'\u0026', u'\u0027',
  u'\u0028', u'\u0029', u'\u002a', u'\u002b', u'\u002c', u'\u002d', u'\u002e', u'\u002f',
  u'\u0030', u'\u0031', u'\u0032', u'\u0033', u'\u0034', u'\u0035', u'\u0036', u'\u0037',
  u'\u0038', u'\u0039', u'\u003a', u'\u003b', u'\u003c', u'\u003d', u'\u003e', u'\u003f',
  u'\u0040', u'\u0041', u'\u0042', u'\u0043', u'\u0044', u'\u0045', u'\u0046', u'\u0047',
  u'\u0048', u'\u0049', u'\u004a', u'\u004b', u'\u004c', u'\u004d', u'\u004e', u'\u004f',
  u'\u0050', u'\u0051', u'\u0052', u'\u0053', u'\u0054', u'\u0055', u'\u0056', u'\u0057',
  u'\u0058', u'\u0059', u'\u005a', u'\u005b', u'\u005c', u'\u005d', u'\u005e', u'\u005f',
  u'\u0060', u'\u0061', u'\u0062', u'\u0063', u'\u0064', u'\u0065', u'\u0066', u'\u0067',
  u'\u0068', u'\u0069', u'\u006a', u'\u006b', u'\u006c', u'\u006d', u'\u006e', u'\u006f',
  u'\u0070', u'\u0071', u'\u0072', u'\u0073', u'\u0074', u'\u0075', u'\u0076', u'\u0077',
  u'\u0078', u'\u0079', u'\u007a', u'\u007b', u'\u007c', u'\u007d', u'\u007e', u'\u0000',
  u'\u2022', u'\u2020', u'\u2021', u'\u2026', u'\u2014', u'\u2013', u'\u0192', u'\u2044',
  u'\u2039', u'\u203a', u'\u2212', u'\u2030', u'\u201e', u'\u201c', u'\u201d', u'\u2018',
  u'\u2019', u'\u201a', u'\u2122', u'\ufb01', u'\ufb02', u'\u0141', u'\u0152', u'\u0160',
  u'\u0178', u'\u017d', u'\u0131', u'\u0142', u'\u0153', u'\u0161', u'\u017e', u'\u0000',
  u'\u20ac', u'\u00a1', u'\u00a2', u'\u00a3', u'\u00a4', u'\u00a5', u'\u00a6', u'\u00a7',
  u'\u00a8', u'\u00a9', u'\u00aa', u'\u00ab', u'\u00ac', u'\u0000', u'\u00ae', u'\u00af',
  u'\u00b0', u'\u00b1', u'\u00b2', u'\u00b3', u'\u00b4', u'\u00b5', u'\u00b6', u'\u00b7',
  u'\u00b8', u'\u00b9', u'\u00ba', u'\u00bb', u'\u00bc', u'\u00bd', u'\u00be', u'\u00bf',
  u'\u00c0', u'\u00c1', u'\u00c2', u'\u00c3', u'\u00c4', u'\u00c5', u'\u00c6', u'\u00c7',
  u'\u00c8', u'\u00c9', u'\u00ca', u'\u00cb', u'\u00cc', u'\u00cd', u'\u00ce', u'\u00cf',
  u'\u00d0', u'\u00d1', u'\u00d2', u'\u00d3', u'\u00d4', u'\u00d5', u'\u00d6', u'\u00d7',
  u'\u00d8', u'\u00d9', u'\u00da', u'\u00db', u'\u00dc', u'\u00dd', u'\u00de', u'\u00df',
  u'\u00e0', u'\u00e1', u'\u00e2', u'\u00e3', u'\u00e4', u'\u00e5', u'\u00e6', u'\u00e7',
  u'\u00e8', u'\u00e9', u'\u00ea', u'\u00eb', u'\u00ec', u'\u00ed', u'\u00ee', u'\u00ef',
  u'\u00f0', u'\u00f1', u'\u00f2', u'\u00f3', u'\u00f4', u'\u00f5', u'\u00f6', u'\u00f7',
  u'\u00f8', u'\u00f9', u'\u00fa', u'\u00fb', u'\u00fc', u'\u00fd', u'\u00fe', u'\u00ff'
)
assert len(_pdfDocEncoding) == 256

_pdfDocEncoding_rev = {}
for i in xrange(256):
    char = _pdfDocEncoding[i]
    if char == u"\u0000":
        continue
    assert char not in _pdfDocEncoding_rev
    _pdfDocEncoding_rev[char] = i

def encode_pdfdocencoding(unicode_string):
    retval = ''
    for c in unicode_string:
        try:
            retval += chr(_pdfDocEncoding_rev[c])
        except KeyError:
            raise UnicodeEncodeError("pdfdocencoding", c, -1, -1,
                    "does not exist in translation table")
    return retval

def decode_pdfdocencoding(byte_array):
    retval = u''
    for b in byte_array:
        c = _pdfDocEncoding[ord(b)]
        if c == u'\u0000':
            raise UnicodeDecodeError("pdfdocencoding", b, -1, -1,
                    "does not exist in translation table")
        retval += c
    return retval
# END PDFDocEncoding
##########################################################################################
