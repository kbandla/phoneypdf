"""
Adobe JS Emulator
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
"""

import PyV8
from hashlib import md5

DEBUG = False
UNDEFINED = 'js_undefined'

PLUGINS = [
            'Accessibility',
            'ppklite',
            'Annots',
            'ADBE:DictionaryValidationAgent',
            'DIGSIG',
            'EScript',
            'Forms',
            'AcroHLS',
            'InetAxes',
            'Make Accessible',
            'Multimedia',
            'PDDom',
            'Checkers',
            'ReadOutLoud',
            'Reflow',
            'SaveAsRTF',
            'ADBE_Search',
            'SendMail',
            'Spelling',
            'WebLink',
            ]

class Events(object):
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class plugIn(PyV8.JSClass):
    certified = True
    loaded  = True
    name = ''

    def __init__(self, name, version=9.31):
        # version is 9.46, but using 9.31 to trigger some exploit kits
        self.name = name
        self.version = version
        if DEBUG : print '[adobe] %s plugIn object initialized'%(self.name)

    def __repr__(self):
        return '%s_%s'%(self.name,self.version)

class app(PyV8.JSClass):
    # app object properties
    activeDocs = []
    calculate = True
    focusRect = UNDEFINED
    formPDFConverters = UNDEFINED
    formsVersion = 9.5
    language = "ENU"
    numPlugins = UNDEFINED
    openInPlace = True
    platform = "WIN"
    plugIns = []  # This is now populated from the plugIn Object
    runtimeHighlight = True
    runtimeHighlightColor = ['RGB', 0.80000000000000004, 0.80000000000000004, 1]
    toolbar = True
    toolbarHorizontal = True
    toolbarVertical = True
    viewerType = 0
    viewerVariaiton = UNDEFINED
    viewerVersion = 9

    def __init__(self):
        if DEBUG : print '[adobe] app object initialized'
        for plugIn_name in PLUGINS:
            x = plugIn( plugIn_name)
            self.plugIns.append( x )

    def alert(self, args):
        print args['cMsg']

    def setTimeOut(self, args):
        print args

class Collab(PyV8.JSClass):
    def __init__(self):
        if DEBUG: print '[adobe] Collab object initialized'

    # Collab properties

    # Collan Methods
    def collectEmailInfo(self, args):
        print args

    def getIcon(self,args):
        print '[phoneyPDF] CVE-2009-0927 : Collab.getIcon() detected'

class util(PyV8.JSClass):
    def __init__(self):
        if DEBUG: print '[adobe] util object initialized'

    def printf(self, args):
        print '[phoneyPDF] CVE-2008-2992 : util.printf'

class Annot3D(PyV8.JSClass):
    activated = False
    context3D = UNDEFINED
    innerRect = [0,0,0,0]
    name    =   'name'
    page    = 0
    rect    = [0,0,0,0]

    def __init__(self):
        if DEBUG: print '[adobe] Annot3D object initialized'

class Doc(PyV8.JSClass):
    def __init__(self):
        if DEBUG : print '[adobe] Doc object initialized'

    def syncAnnotScan(self):
        print 'syncAnnotScan : '

    def getAnnots(self, args):
        print 'getAnnots : ',args['nPage']
        # Spec says: if there are no annotations found, return null
        return 'null'

class event(PyV8.JSClass):
    type = 'null'
    name = 'null'
    target = Doc()

    def __init__(self):
        if DEBUG : print '[adobe] event object initialized'

    def __getattibute__(self, attr):
        print '[event] ',attr
        return object.__getattribute__(self, attr)

class Global(PyV8.JSClass):

    def __init__(self):
        self.hookObjects = []

    def captureEvalCodeC(self, val):
        #print "[EVAL-C] "
        stri = []
        for c in val.split(","):
            if c != "":
                stri.append(unichr(int(c)))

        evalCode = "".join(stri)
        evalCode_md5 = md5(evalCode).hexdigest()
        #f = open('scripts/'+evalCode_md5,'w')
        #f.write(evalCode)
        #f.close()
        #print 'MD5 : %s '%(evalCode_md5)
        #print evalCode

    def captureEvalCodeJS(self, val):
        #print "[EVAL-js] "
        val_md5= md5(val).hexdigest()
        #f = open('scripts/'+val_md5,'w')
        #f.write(val)
        #f.close()
        #print 'MD5 : %s '%(val_md5)
        #print val

    def printSeps(self,msg):
        print '[printSeps] ',args

    def printSepsWithParams(self, args):
        print '[printSepsWithParams] ', args

    def log(self, function_name, function_arguments ):
        args = []
        for arg in function_arguments:
            args.append(arg)
        name = function_name
        event = Events( name , args)
        self.hookObjects.append( event)

    def get_app(self):
        return app()

    def get_collab(self):
        return Collab()

    def utill(self):
        return util()

    def docc(self):
        return Doc()

    def eventt(self):
        return event()

    app = property(get_app)

##################################################################

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 1:
        data = ''
    else:
        print 'Using %s'%(sys.argv[1])
        data = open(sys.argv[1]).read()

    pre_js = open('dom_bootstrap.js').read()
    with PyV8.JSContext(Global()) as ctx:
        ctx.eval(pre_js)
        ctx.eval(data)
