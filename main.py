'''
a cli interface
This file is part of the phoneyPDF Framework

Trevor Tonn <smthmlk@gmail.com>
Kiran Bandla <kbandla@in2void.com>
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
# stdlib
import sys
import optparse
import traceback
from collections import defaultdict

# local
import interpret

# Parse options from command line
usage = "usage: %prog [options]"
parser = optparse.OptionParser(usage=usage)
parser.add_option("-v", "--verbose", dest="verbose", action="store_true", help="enable verbose mode", default=False, metavar="VERBOSE")
options, args = parser.parse_args()

# Begining to paddle in the water
scannedFiles = 0.0
filesWithDetections = 0.0
scanResultsL = defaultdict(int)
fileCount = len(args)

# Catch a keyboardinterrupt across all files we've been asked to process
try:
    for filePath in args:
        scannedFiles += 1
        fileCount -= 1
        msgL = ['[*] %s: ' % filePath]

        # Catch any exceptions we are not expecting from this particular file we're processing
        try:
            pdfText = open(filePath).read()
            p = interpret.InterpretPDF(pdfText, options.verbose)

            if p.getHookObjects():
                filesWithDetections += 1
                msgL.append('\033[91m Detections! \033[0m')
                for event in p.getHookObjects():
                    scanResultsL[event.name] += 1
                    msgL.append(' [%s]' % event.name)
        except Exception, e:
            print "Caught unhandled exception: %s" % e
            print '-' * 60
            traceback.print_exc(file=sys.stdout)
            print '-' * 60

        if not fileCount % 10:
            msgL.append('\n[*] \033[91m %d files remaining.\033[0m' % fileCount)
        print ''.join(msgL)

except KeyboardInterrupt, e:
    pass

#### Display Results
print '\nResults:'
print 'Files scanned : %d' % scannedFiles
if scannedFiles == 0:
    percentage = 0.0
else:
    percentage = 100.0 * filesWithDetections / scannedFiles

print 'Files detected: %d (%d%%)' % (filesWithDetections, percentage)

if scanResultsL:
    print 'Detection breakdown:'
    for key, value in scanResultsL.iteritems():
        print '\t%s - %d' % (key, value)

print '\nDone'
