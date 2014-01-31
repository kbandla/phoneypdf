'''
Utilities
This file is part of the phoneyPDF Framework

Trevor Tonn <ttonn@verisign.com>

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
import curses.ascii

def makeAscii(lst) :
    """
    Used by makeReadableHexStr. This should not be used on its own.
    """

    aLst = []

    for i in lst :
        if i == '   ' :
            aLst.append(' ')
            continue

        x = int(i,16)
        if curses.ascii.isprint(x) :
            aLst.append( chr(x) )
        elif x == 10 or x == 13 :
            aLst.append( '\033[36;1m.\033[0m' )
        elif x == 9 :
            aLst.append( '\033[34;1m.\033[0m' )
        else :
            aLst.append( '\033[35;1m.\033[0m' )

    return aLst

def makeReadableHexStr(inHexStr, asciToo=False, width=16) :
    """
    Takes a collection of hex values like "\x3a\xd4\x01\x2f" and returns them as "3a d4 01 2f "
    This form is suitable for comparing to tshark's output; easily readable.

    This also has a few options/features that scapy's hexdump does not have:
      1. can output more than just 16 bytes per line, both as hex and printable ascii.
      2. ascii output is toggleable
      3. ascii output has colors for common unprintable chars (\r, \n, \t) and uses a different
         color for unprintable chars' dots (purple). This makes it really easy to spot
         unexpected data appearing in the middle of what should be normal text.

    Arguments:
    inHexStr       -- The string of hex values to be converted (in "\x00" form).
    asciToo        -- When making the output string, add ascii version of the bytes as well.
    width          -- The number of bytes to display per line. If used with asciToo, the line
                      will show somewhere around 2x this width, so be prepared for that.

    Returns:
    A string of formatted data safe for printing to a term. The color codes will be unsafe for
    use in tools like less/more, however, and if you redirect this output to disk, vi will go
    crazy on them. Keep that in mind :]
    """
    if inHexStr == None or inHexStr == '' :
        return ''

    outStrList = []
    rowStrL = []
    count = 0

    for i in inHexStr :

        rowStrL.append("%02x " % ord( i ))
        count += 1

        if count % width == 0 :
            if asciToo :
                rowStrL.extend( makeAscii(rowStrL) )

            rowStrL.append("\n")
            outStrList.append( ''.join(rowStrL) )
            rowStrL = []

    # don't forget any stragglers in the last row, and add some spaces to fill it up
    # in case we're showing ascii as well on the right--want to keep that in a nice column.
    if asciToo :
        x = width - len(rowStrL)
        for i in range(x) :
            rowStrL.append('   ')

        rowStrL.extend( makeAscii(rowStrL) )

    outStrList.append( ''.join(rowStrL) )

    finalStr = ''.join(outStrList)

    if finalStr[-1] == '\n' :
        finalStr = finalStr[:-1]

    return finalStr
