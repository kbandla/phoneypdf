'''
V8-based JavaScript Emulator for phoneyPDF
This file is part of the phoneyPDF Framework

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
from pyv8 import PyV8
from hashlib import md5
import tools
from features import *

class Events(object):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class Global(PyV8.JSClass):

    def __init__(self, logger=None, DEBUG=False):
        self.hookObjects = []
        self.features = {}
        self.logger = logger
        self.fieldValue = ''
        self.DEBUG = DEBUG

        # const
        self.UNESCAPE_THRESHOLD = 500

    def captureEvalCodeC(self, val):
        #print "[EVAL-C] "
        stri = []
        for c in val.split(","):
            if c != "":
                stri.append(unichr(int(c)))
        #evalCode = "".join(stri)
        #evalCode_md5 = md5(evalCode).hexdigest()
        #f = open('scripts/'+evalCode_md5,'w')
        #f.write(evalCode)
        #f.close()
        #print 'MD5 : %s '%(evalCode_md5)
        #print evalCode

    def captureEvalCodeJS(self, val):
        if self.DEBUG:
            val_md5= md5(val).hexdigest()
            self.logger.info('eval() called. wrote to scripts/%s'%(val_md5))
            f = open('scripts/'+val_md5,'w')
            f.write(val)
            f.close()

    def write_hex(self, message):
        """
        Write HEX : This is for debugging purposes only.
                    Used to do some shellcode testing
        """
        result=[]
        length = 16
        if message == None:
            print 'NONE'
            return
        #FILTER=''.join([(len(repr(chr(x)))==3) and chr(x) or '.' for x in range(256)])

        for i in xrange(0, len(message), length):
           s = message[i:i+length]
           hexa = ' '.join(["%02X"%ord(x) for x in s])
           #printable = s.translate(FILTER)
           #result.append("%04X   %-*s   %s\n" % (i, length*3, hexa, printable))
           result.append(hexa)
        print ''.join(result)

    def analyzeData(self, jsValue):
        """
        Pass JavaScript values to this funciton from JSLand
        """
        if not jsValue.strip():
            return
        import base64
        try:
            decoded = base64.b64decode(jsValue)
            self.logger.debug("\033[91m Successfully decoded a field's rawValue. %sbytes \033[0m" % len(decoded))
            md5_value = md5(decoded).hexdigest()
            if self.DEBUG:
                f = open('exploits/%s'%(md5_value), 'w')
                f.write(decoded)
                f.close()
                print 'wrote to exploits/%s'%(md5_value)
            strings = tools.getStrings(decoded)
            if strings:
                for _string in strings:
                    if ('http' in _string.lower()) or ('A'*100 in _string) or ('.dll' in _string.lower()) or ('.exe' in _string.lower()):
                        # Most likely a malicious URL. Add an event
                        name = 'Exploit'
                        args = ['2010-0188'] # @kbandla: how do you know this is CVE-2010-0188? Just the long string A's?
                        event = Events(name, args)
                        self.hookObjects.append(event)
        except Exception,e:
            self.logger.debug("Could not base64-decode : %s" % e)

    def add_feature(self, feature, value):
        self.features[feature] = value

    def increment_feature(self, feature, value=1):
        if self.features.has_key(feature):
            self.features[feature] += value
        else:
            self.features[feature] = value

    def write_log(self, label, message):
        """
        Depending on the label, appropriate colors are chosen
        """
        if self.logger:
            level = {   'INFO': self.logger.info,
                        'WARN': self.logger.warn,
                        'ERROR':self.logger.error,
                        'DEBUG':self.logger.debug
                    }
            handler = level[label]
            handler('\033[91m %s \033[0m'%(message))
        else:
            print '\033[91m[%s] %s\033[0m'%(label,message)

    def test_shellcode( self, mesg):
        """
        This is for debugging purposes only.
        Used to do some shellcode testing
        """
        result  = []
        for x in mesg:
            result.append(x)

    def log_event(self, function_name, function_arguments ):
        args = []
        print "function_arguments=%s" % type(function_arguments)
        for arg in function_arguments:
            args.append(arg)
        name = function_name
        event = Events(name, args)
        self.hookObjects.append(event)

if __name__ == "__main__":
    """
    Some debugging code.
    """
    DIR = 'adobe/'
    import os
    import sys
    if len(sys.argv) < 1:
        data = ''
    else:
        print 'Using %s'%(sys.argv[1])
        script = open(sys.argv[1]).read()

    files = os.listdir(DIR)
    files.sort()
    js = []
    with PyV8.JSContext(Global()) as ctx:
        try:
            for file in files:
                if file.endswith('.js'):
                    print 'Loading %s......'%(DIR+file),
                    data = open(DIR+file).read()
                    ctx.eval(data)
                    print 'Done!'
        except Exception,e:
            print e
            raise
        try:
            ctx.eval(script)
        except Exception, e:
            print e
            pass
        # REPL!
        print '"quit" to exit. use jsdbg.dir to do python-style dir()'
        goEval = True
        while goEval:
            try:
                eval_string = raw_input('>>')
                if eval_string.lower() == 'quit':
                    goEval = False
                elif eval_string.startswith('load'):
                    filename = eval_string.split('load ')[-1]
                    if os.path.exists(filename):
                        data = open(filename).read()
                        ctx.eval(data)
                else:
                    ctx.eval( "console.log(%s)"%(eval_string))
                    #('console.log(%s)'%eval_string)
            except Exception,e:
                print e
