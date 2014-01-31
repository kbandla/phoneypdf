'''
phoneyPDF: A Virtual PDF Analysis Framework

Trevor Tonn  <smthmlk@gmail.com>
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

# stdlib
from StringIO import StringIO
import logging
import os
import re
import sys
import types

# lxml
from lxml import etree

# local to this package
from pdf.parser import *
from utils import *
import jsDOM
from pyv8 import PyV8
import logger
import features

# Toggle the value of USE_PURE_JS to use one of :
#   * [False] PyV8-based Adobe DOM
#   * [ True] Pure JavaScript-based Adobe DOM ( JS files are present in PATH_PURE_JS )

USE_PURE_JS = True
# Development Debugging mode
DEBUG = False
# PATH_SCRIPTS is where the JavaScript files will we saved if DEBUG
PATH_SCRIPTS    =   "scripts"

if USE_PURE_JS:
    PATH_PURE_JS = 'adobe'
    from reader import *
else:
    from adobe import *

# Some PDF dictionary keys
KEY_ROOT        =   '/Root'
KEY_CATALOG     =   '/Catalog'
KEY_ACTION      =   '/Action'
KEY_OPENACTION  =   '/OpenAction'
KEY_AA          =   '/AA'
KEY_JAVASCRIPT  =   '/JavaScript'
KEY_RENDITION   =   '/Rendition'
KEY_OUTLINES    =   '/Outlines'
KEY_JS          =   '/JS'
KEY_PAGES       =   '/Pages'
KEY_PAGE        =   '/Page'
KEY_METADATA    =   '/Metadata'
KEY_SUBTYPE     =   '/Subtype'
KEY_LENGTH      =   '/Length'
KEY_TYPE        =   '/Type'
KEY_S           =   '/S'
KEY_ACROFORM    =   '/AcroForm'
KEY_EMBEDDEDFILE=   '/EmbeddedFile'
KEY_XFA         =   '/XFA'
KEY_CATALOG     =   '/Catalog'
KEY_CONTENTS    =   '/Contents'
KEY_FILTER      =   '/Filter'
KEY_KIDS        =   '/Kids'
KEY_COUNT       =   '/Count'
KEY_PARENT      =   '/Parent'
KEY_LASTMODIFIED=   '/LastModified'
KEY_RESOURCES   =   '/Resources'
KEY_MEDIABOX    =   '/MediaBox'
KEY_ANNOTS      =   '/Annots'
KEY_ANNOT       =   '/Annot'
KEY_EMBEDDEDFILE=   '/EmbeddedFile'
KEY_EF          =   '/EF'
KEY_FONT        =   '/Font'
KEY_LAUNCH      =   '/Launch'
KEY_WIN         =   '/Win'
KEY_F           =   '/F'
KEY_P           =   '/P'
KEY_SUBJ        =   '/Subj'


class Event(object):
    def __init__(self, hookObject):
        self.hookObject = hookObject

class InterpretPDF:
    __pdfObjL = None
    '''All PDFObjects are stored in this list'''

    __xmlL = None
    '''All PDFObjects with XML are kept in this list'''

    __jsS = None
    '''All PDFObject IDs containing Javascript are kept in this set'''

    __jsL = None
    '''All JavaScript text is appended to this list - in the order that its found'''

    __pdfObjTypeD = {1: "PDF_ELEMENT_COMMENT",
                     2: "PDF_ELEMENT_INDIRECT_OBJECT",
                     3: "PDF_ELEMENT_XREF",
                     4: "PDF_ELEMENT_TRAILER",
                     5: "PDF_ELEMENT_STARTXREF",
                     6: "PDF_ELEMENT_MALFORMED",
                     "PDF_ELEMENT_COMMENT": 1,
                     "PDF_ELEMENT_INDIRECT_OBJECT": 2,
                     "PDF_ELEMENT_XREF": 3,
                     "PDF_ELEMENT_TRAILER": 4,
                     "PDF_ELEMENT_STARTXREF": 5,
                     "PDF_ELEMENT_MALFORMED": 6}
    '''For enumerations of PDFObject types for easier debugging'''

    featureCollection = None
    '''A features.FeatureCollection instance specific to this PDF being interpreted'''

    def __init__(self, pdfTEXT, verbose=False):
        """
        Arguments:
            - pdfTEXT (str) PDF Document data
            - verbose (bool, default=False) indicates whether to turn on ridiculous debugging
                output, which will be very colorful because Trevor has a never ending stream
                of lyrical consciousness stemming from octal ANSI color codes with various
                modifiers
        """
        self.logger = logger.buildLogger()
        self.verbose = verbose
        if self.verbose is True:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.ERROR)

        # So, in addition to 'verbose' there is another mode for people who are reading this
        # code: DEBUG mode. If you're reading this, it means you plan to add or fix something.
        # There's a few places where this mode will do some useful things for you.
        if DEBUG:
            # writes the pdf to /tmp/<md5>.pdf
            debugPdfFilepath = "/tmp/%s.pdf" % md5(pdfTEXT).hexdigest()
            f = open(debugPdfFilepath, 'w')
            f.write(pdfTEXT)
            f.close()
            self.logger.info("Wrote PDF string to %s" % debugPdfFilepath)

        self.__pdfObjL = []  # a list of all pdf objects parsed
        self.__pdfIndObjD = {}  # quick access to indirect objects by their ID number ( int => pdf obj )
        self.__jsS = set()
        self.__jsL = []  # all js strings we find are stored here so we retain order
        self.__hookObjects = []
        self.__visitedIndirectObjects = set()
        self.__openActionScripts = []
        self.__streams = []
        self._readerPages = -1  # track the number of 'Page' objects we saw
        self.__scriptCount = 0  # used to count scripts. used when writing scripts to disk in DEBUG mode
        self.featureCollection = features.FeatureCollection(self.logger)  # used to track features for a later ML phase
        self.featureCollection.setFeatureValue('F_L_PDF_LENGTH', len(pdfTEXT))
        self.__stats = {}  # Various stats from PDF objects

        # misc temp objects
        self._handlerKey = None
        self.__xfa__monitoredFieldNames = set()

        # these objects are necessary for 'rendering' the pdf after parsing
        self.trailerObj = None
        self.catalogObj = None

        # parse pdf with pdf-parser; get list of PDFpdfObj's back and classifies them
        self.__getPdfObjects(pdfTEXT)

        # JavaScript Context for this PDF
        self.__initJSEngine()

        # begins the 'render' process
        self.__traverseObjects()
        self.__handleActions()
        self.__checkJSChanges()

        self._print_stats()

    def _print_stats(self):
        return  # ??
        if not DEBUG:
            return
        for key, value in self.__stats.items():
            print key, value

    def _increment_stats(self, stat):
        if stat in self.__stats:
            self.__stats[stat] +=1
        else:
            self.__stats[stat] = 1

    def __handleActions(self):
        for js in self.__openActionScripts:
            self.featureCollection.incFeatureValue("F_C_JS_SCRIPTS_FOUND")
            self.__executeJavaScript(js)

    def __checkJSChanges(self):
        for fieldName in self.__xfa__monitoredFieldNames:
            self.__executeJavaScript('if(%s.rawValue) { analyzeData(%s.rawValue) }' % (fieldName, fieldName), isDom=True)

        # Add collected features from Javascript land
        for key, value in self.javascript_global.features.iteritems():
            self.featureCollection.setFeatureValue(key, value)

    def getHookObjects(self):
        """
        A simple method to add all hooked messages to a list
        """
        return self.javascript_global.hookObjects

    def __initJSEngine(self):
        """
        Sets up the javascript context and loads it up with objects and functions defined in our *.js files.
        This is how we 'expose' our Reader-esque functions and structures to javascript in a PDF to potentially call.
        """
        self.logger.debug("[JavaScript] Initializing Engine")
        self.javascript_global = Global(self.logger, DEBUG)

        with PyV8.JSContext(self.javascript_global) as ctx:
            self.ctx = ctx
            if not USE_PURE_JS:
                self.logger.debug("[JavaScript] Using PyV8 Engine")
                js_bootstrap = open('adobe_bootstrap.js').read()
                ctx.eval(js_bootstrap)
            else:
                self.logger.debug("[JavaScript] Using Pure JavaScript Engine")

                # [Trevor] find the dir containing the adobe JS files
                adobeDir = PATH_PURE_JS
                if adobeDir[-1] != '/':
                    adobeDir += '/'

                files = [i for i in os.listdir(adobeDir) if i.endswith('.js')]
                files.sort()

                try:
                    for js_file in files:
                        self.logger.debug('[JavaScript] Loading %s......' % (adobeDir + js_file))
                        data = open(adobeDir + js_file).read()
                        ctx.eval(data)
                except Exception, e:
                    self.logger.exception('[%s] %s' % (js_file, e))
                    exit(-1)

    def __executeJavaScript(self, script, saveScript=False, isDom=False):
        """
        Executes the requested Javascript snippet in the malicious context (ctx)
            *   saveScript  = Will save the script to scripts/. This is used during debugging
            *   isDom       = True for scripts which are used to build XFA DOM and other Adobe JS stuff
        """
        # Write the script to scripts/MD5
        if type(script) not in types.StringTypes:
            self.logger.warn("passed a script whose types is %r" % script)
            if isinstance(script, PDFIndObjRef):
                script= self.__getIndirectObjectJavaScript(script)
                self.logger.warn("successfully extracted JavaScript from indirect Object")
            else:
                return

        if DEBUG and saveScript:
            if not isDom:
                # writes executed scripts to PATH_SCRIPTS
                md5_val = md5(script).hexdigest()
                f = open('%s/%s_%s' % (PATH_SCRIPTS, self.__scriptCount, md5_val), 'w')
                f.write(script)
                f.close()

        self.__scriptCount += 1
        if self.verbose:
            if len(script) > 128:
                shortenedScript = script[:125] + '...'
            else:
                shortenedScript = script

            self.logger.debug("Executing %d bytes of Javscript: \033[33;3m%s\033[0m" % (len(script), shortenedScript))

        with self.ctx:
            try:
                if not isDom:
                    self.featureCollection.incFeatureValue("F_C_JS_SCRIPTS_EXECUTED")
                    self.featureCollection.incFeatureValue("F_L_JS_SCRIPTS_LENGTH_TOTAL", len(script))
                self.ctx.eval(script)
            except Exception, e:
                self.featureCollection.incFeatureValue("F_C_JS_SCRIPTS_EXECUTION_FAILED")
                self.logger.debug("\033[91m%s\033[0m" % e)

    def __JSDebug(self):
        """
        A simple JavaScript REPL shell
        For Debugging only!
        """
        print '"quit" to exit. use jsdbg.dir to do python-style dir()'
        goEval = True
        while goEval:
            try:
                eval_string = raw_input('>>')
                if eval_string.lower() == 'quit':
                    goEval = False
                else:
                    with self.ctx:
                        self.ctx.eval("console.log(%s)" % eval_string)
            except Exception, e:
                self.logger.error("caught exception executing javascript repl shell: %s" % e)

    def __getPdfObjects(self, pdfTEXT):
        '''
        Uses pdf-parser to parse PDF into PDFpdfObjs

        Fills this instances pdfObjectL with any objects pdf-parser could parse
        '''
        self.logger.debug("Parsing PDF, %d Bytes..." % len(pdfTEXT))

        # adapted from Didier's Main(); cPDFParser requires a file-like pdfObj
        pdfSIO = StringIO(pdfTEXT)

        # Get a parser and begin extracting pdfObjs
        oPDFParser = cPDFParser(pdfSIO, False, None, self.logger)
        pdfObj = 1
        while pdfObj is not None:
            pdfObj = oPDFParser.GetObject()

            if pdfObj is None:
                # exits while loop
                continue

            if pdfObj.type == self.__pdfObjTypeD["PDF_ELEMENT_TRAILER"]:
                self.trailerObj = pdfObj
                self.logger.debug("Trailer object found")

            elif pdfObj.type == self.__pdfObjTypeD["PDF_ELEMENT_INDIRECT_OBJECT"] and pdfObj.dict:
                # check the dict for /Type => /Catalog
                if KEY_TYPE in pdfObj.dict and pdfObj.dict[KEY_TYPE] == KEY_CATALOG:
                    self.logger.debug("Found Catalog object")
                    self.catalogObj = pdfObj

                # add this indirect object to the table for quick lookup by id
                if pdfObj.id is not None:
                    self.logger.debug("Registering Indirect PDF Object: %d" % pdfObj.id)
                    self.__pdfIndObjD[pdfObj.id] = pdfObj

            self.logger.debug("Added PDFObject %s" % self.__pdfObjTypeD[pdfObj.type])
            self.__pdfObjL.append(pdfObj)

    def __bruteForceJS(self):
        '''
        This is a last-attempt brute-force method, trying to find all stream objects and see
        if they contain JavaScript

        This will find JS that would be otherwise hard to walk the pdf tree. (deeply planted)
        Example : /Catalog -> /Name -> /JavaScript -> /Names -> /S -> x 0 R
        '''
        self.logger.debug("\n[Brute-Force] Trying one last time to exec JS from all streams")
        # Now, lets iterate all the indirect objects, searching for JS
        for indObjID, indObj in self.__pdfIndObjD.items():
            if KEY_S in indObj.dict and indObj.dict[KEY_S] in (KEY_JAVASCRIPT, KEY_RENDITION):
                # We found a JS object!
                self.__jsS.add(indObjID)
            if KEY_TYPE in indObj.dict and indObj.dict[KEY_TYPE] == KEY_ACTION:
                # Action object. Lets see if this has JS
                if KEY_JS in indObj.dict.has_key:
                    self.__jsS.add(indObjID)
            if KEY_FILTER in indObj.dict:
                # All streams need investigation
                self.logger.debug("[Brute-Force] Found a %s stream in object # %s" % (indObj.dict[KEY_FILTER], indObjID))
                try:
                    self.__executeJavaScript(indObj.stream)
                    self.logger.debug("[Brute-Force] Successfully found a JavaScript stream")
                except Exception:
                    # passing on exceptions... sigh
                    pass

    def __getIndirectObjectJavaScript(self, indirectObject):
        """
        Given an indirect object, return the embedded JavaScript
        """
        if isinstance(indirectObject, PDFIndObjRef):
            target_object = self.__pdfIndObjD[indirectObject.objectID]
            if isinstance(target_object, PDFIndObjRef):
                return self.__getIndirectObjectJS(target_object)
            elif isinstance(target_object, cPDFElementIndirectObject):
                if hasattr(target_object, 'stream'):
                    return target_object.stream
        else:
            self.logger.debug("Need an indirect object.")

    def __getIndirectObjectJS(self, jsObj):
        '''
        Walks a given Indirect object till it finds JS, and adds the JS to __jsL
        '''
        if jsObj.type != self.__pdfObjTypeD['PDF_ELEMENT_INDIRECT_OBJECT']:
            return

        # walk to the referenced indirect object
        if jsObj.GetReferences():
            for reference in jsObj.GetReferences():
                tmpObj = self.__pdfIndObjD[int(reference[0])]
                self.__getIndirectObjectJS(tmpObj)

        elif hasattr(jsObj, 'dict'):
            if jsObj.dict.get('/S', None) in ['/JavaScript', '/Rendition']:
                if '/JS' in jsObj.dict:
                    self.__jsL.append(jsObj.dict['/JS'])
            elif '/JS' in jsObj.dict:
                self.__getIndirectObjectJS(tmpObj)
            elif hasattr(jsObj, 'stream'):
                self.__jsL.append(jsObj.stream)

    def __isIndObjJS(self, objectID):
        '''
        #TODO: candidate for deletion
        Does an indirect object result in JS?
        Needs an ObjectID. NOT an object
        If yes, return the JS blob. Else, None
        '''
        obj = self.__pdfIndObjD[objectID]
        if KEY_S in obj.dict:
            if obj.dict[KEY_S] in [KEY_JAVASCRIPT, KEY_RENDITION]:
                if obj.dict.has_key(KEY_JS):
                    if hasattr(obj.dict[KEY_JS], "objectID"):
                        # indirect reference. Handle it. Recursive :
                        return self.__isIndObjJS( obj.dict[KEY_JS].objectID )
                    else:
                        return obj.dict[KEY_JS]
        elif hasattr( obj, 'stream'):
            if obj.stream:
                return obj.stream
        else:
            return None

    def __traverseObjects(self):
        '''
        Walks from the Trailer object to the root object (catalog) and then the page tree.
        See the PDF 1.7 spec, section 3.6.1, "Document Catalog" for more info on why the
        trailer/Catalog objects are the center of the universe for this method.

        /trailer -> /Root -> /Catalog -> Start!
        '''
        if self.logger.getEffectiveLevel() <= logging.INFO:
            self.logger.debug("\n")

        # check for root
        if not self.trailerObj:
            self.logger.debug("\033[91m No trailer object found\033[0m")
            return False
        elif not hasattr(self.trailerObj, 'dict'):
            self.logger.warn("Malformed Trailer Object. No dict found")
            return False
        elif KEY_ROOT not in self.trailerObj.dict:
            self.logger.warn("Trailer object does not contain a /Root name; cannot continue")
            return False

        # looking up the root obj by its ID
        if not hasattr(self.trailerObj.dict[KEY_ROOT],'objectID'):
            self.logger.debug("Cannot find an objectID for /Root. Perhaps its a /Root with out an objectID.")
            rootO   = self.trailerObj
            rootO.dict[KEY_TYPE] = KEY_CATALOG
        else:
            rootO = self.__pdfIndObjD.get( self.trailerObj.dict[KEY_ROOT].objectID, None)

        if not rootO:
            self.logger.warn('Root object not found. Aborting.')
            return

        # check to ensure this root obj is of type '/Catalog'
        catalogO = None
        if hasattr(rootO, 'dict')  and  KEY_TYPE in rootO.dict  and   rootO.dict[KEY_TYPE] == KEY_CATALOG:
            catalogO = rootO

        if not catalogO:
            self.logger.warn("Root object is not of type /Catalog; cannot continue")
            #return
            # It is possible that a Root object is not of Type /Catalog
            # Continue here
            catalogO = rootO

        ########################################################################################################
        # Start walking stuff from the Catalog object
        self._handle_Generic( catalogO )
        if self._handle_Orphans():
            pass
            # If we had orphans, then re-walk the tree once more,
            # with this new info.
            # Disabled for now
            #self._handle_Generic( catalogO )
        return

    def _walk_All(self):
        """
        In case we dont have a Root / Catalog, just walk all objects
        """
        for id, pdfObject in self.__pdfIndObjD.items():
            self._handle_Generic( pdfObject )


    def _handle_Orphans(self):
        """
        Handle objects which were not walked by _handle_Generic
        """
        all_objects = set(self.__pdfIndObjD.keys())
        orphans = all_objects.difference( self.__visitedIndirectObjects )
        if not orphans:
            return False
        for orphan in orphans:
            self._handle_cPDFElementIndirectObject( self.__pdfIndObjD[orphan] )

    def _handle_Generic(self, genericObject, handlerKey = None):
        """
        handles an object based on the instance
        """
        if genericObject.__class__.__name__ in ['str', 'float']:     #'str' also in the list eventually
            return
        elif genericObject.__class__.__name__ in ['dict']:
            # handle all conditions when you land here
            for key in genericObject.keys():
                self._handle_Generic( genericObject[key] )
            return
        elif genericObject.__class__.__name__ in ['list']:
            for item in genericObject:

                self._handle_Generic( item )
            return

        # Finally, some real handlers
        handler = getattr( self, '_handle_%s'%(genericObject.__class__.__name__), None)
        if not handler:
            self.logger.debug("No Handler for this object type (%s)"%(genericObject.__class__.__name__))
        else:
            return handler( genericObject, handlerKey)

    def _handle_PDFIndObjRef(self, pdfIndObj, handlerKey=None):
        assert isinstance ( pdfIndObj, PDFIndObjRef), "Wrong object type passed. Potential Bug"
        if not self.__pdfIndObjD.get( pdfIndObj.objectID ):
            self.logger.debug("\033[91m Could not find Object ID %s in our list of Objects \033[0m" %(pdfIndObj.objectID))
            return
        if pdfIndObj.objectID in self.__visitedIndirectObjects:
            # Noticed many loops when walking Indirect Objects.
            # hence this check
            self.logger.debug("\033[91m Already visited this objectID (%s) \033[0m"%(pdfIndObj.objectID))
            return
        self.__visitedIndirectObjects.add( pdfIndObj.objectID )
        targetObject = self.__pdfIndObjD[ pdfIndObj.objectID ]
        # Handlers here
        if isinstance(targetObject, PDFElement ):
            return self._handle_PDFElement( targetObject, handlerKey)

    def _handle_cPDFElementIndirectObject(self, pdfIndObj, handlerKey=None):
        assert isinstance( pdfIndObj, cPDFElementIndirectObject ), "Was expecting a cPDFElementIndirectObject object"
        return self._handle_PDFElement( pdfIndObj , indirectObject = True)

    def _handle_cPDFElementTrailer(self, pdfTrailer, handlerKey=None):
        assert isinstance( pdfTrailer, cPDFElementTrailer), "Was expecting a cPDFElementTrailer object"
        return self._handle_PDFElement( pdfTrailer)

    def _handle_PDFElement(self, pdfElement , handlerKey=None , indirectObject=False):
        if not indirectObject:
            assert isinstance( pdfElement, PDFElement ), "Was expecting a PDFElement object"

        if not pdfElement.dict.get(KEY_TYPE, None):
            # We do not have a /Type here
            self.logger.debug("[%s ID:%s ] Could not determine the Type of object via %s" %(handlerKey, pdfElement.id, KEY_TYPE))
            self.logger.debug("[%s ID:%s ] Available Keys : %s "%(handlerKey, pdfElement.id, ','.join(pdfElement.dict.keys())))
            """
            if hasattr(pdfElement, 'stream'):
                self.logger.debug("[%s ID:%s ] Found a Stream! Length = %s"%(handlerKey, pdfElement.id, len(pdfElement.stream)))
            """
            # So we dont have a type. Fine. Lets see what else we can do here
            if pdfElement.dict.get(KEY_S, None):
                # JavaScript object
                js = None
                if hasattr(pdfElement, 'stream'):
                    js = pdfElement.stream
                    self.logger.debug("[%s ID:%s ] Found a JavaScript Stream! Length = %s"%(handlerKey, pdfElement.id, len(pdfElement.stream)))
                elif pdfElement.dict.has_key(KEY_JS) and isinstance( pdfElement.dict[KEY_JS] , str):
                    js = pdfElement.dict[KEY_JS]
                elif pdfElement.dict.has_key(KEY_JS) and isinstance( pdfElement.dict[KEY_JS], PDFIndObjRef):
                    js = self.__getIndirectObjectJavaScript( pdfElement.dict[KEY_JS])
                if js:
                    self.__executeJavaScript ( js )
            elif hasattr(pdfElement, 'stream'):
                self.logger.debug("[%s ID:%s ] Found a Stream! Length = %s"%(handlerKey, pdfElement.id, len(pdfElement.stream)))
                return pdfElement.stream

            # Lets check if this has  /Subject /Author /Creator. If yes, add to it event.target object in JS
            # TF# : 7051216 ; MD5 : 04d7794da20b782d6a5f3b893f984b21
            for key in ['/Subject', '/Author', '/Creator']:
                if pdfElement.dict.has_key(key):
                    # Add this attribute(including lower-case )  to the event object in JS
                    self.__executeJavaScript( "event.target.%s = '%s';"%(key.strip('/'), pdfElement.dict[key]), isDom=False)
                    self.__executeJavaScript( "event.target.%s = '%s';"%(key.strip('/').lower(), pdfElement.dict[key]), isDom=False)

            # As a last resort, lets run generic handlers on all objects herein
            for key in pdfElement.dict.keys():
                self.logger.debug("[%s ID:%s] Handling %s .."%(pdfElement.dict.get(KEY_TYPE,None), pdfElement.id, key))
                self._handle_Generic( pdfElement.dict[key])
        else:
            # We have a '/Type' here
            self._increment_stats(pdfElement.dict[KEY_TYPE])
            for key in pdfElement.dict.keys():
                self.logger.debug("[%s ID:%s ] Found %s"%(pdfElement.dict[KEY_TYPE], pdfElement.id, key))

            # Specific handlers for various types
            if pdfElement.dict[KEY_TYPE] == KEY_ACTION:
                #/Action object
                keys = pdfElement.dict.keys()
                if KEY_S in keys:
                    if pdfElement.dict[KEY_S] == KEY_JAVASCRIPT:
                        js = None
                        # Handle JS here
                        # This has to be either 1) text string or 2) Stream
                        if hasattr(pdfElement, 'stream'):
                            # Stream!
                            #TODO: JS is served. Pick it up
                            js = pdfElement.stream
                        elif isinstance( pdfElement.dict[KEY_JS], str):
                            js = pdfElement.dict[KEY_JS]
                            #TODO: JS is served. Pick it up
                        elif isinstance( pdfElement.dict[KEY_JS], PDFIndObjRef ):
                            js = self.__getIndirectObjectJavaScript( pdfElement.dict[KEY_JS] )
                            #TODO: JS is served. Pick it up
                        self.logger.debug("[%s ID:%s] Executing Javascript" %(pdfElement.dict[KEY_TYPE], pdfElement.id) )
                        if js:
                            self.featureCollection.incFeatureValue("F_C_JS_SCRIPTS_FOUND")
                            self.__executeJavaScript( js )
                    elif pdfElement.dict[KEY_S] == KEY_LAUNCH:
                        self.logger.debug("[%s ID:%s] Found a /Launch action type item "%(pdfElement.dict[KEY_TYPE], pdfElement.id))
                        if pdfElement.dict.has_key(KEY_WIN):
                            # A dictionary containing Windows-specific launch parameters
                            filename = pdfElement.dict[KEY_WIN].get(KEY_F,None)
                            # A parameter string to be passed to the above application
                            params = pdfElement.dict[KEY_WIN].get(KEY_P, None)
                            self.logger.debug("[%s ID:%s] Potential launch target : %s %s"%(pdfElement.dict[KEY_S], pdfElement.id, filename, params))


                # Move JS Logic here

            elif pdfElement.dict[KEY_TYPE] == KEY_PAGES:
                # This is a /Pages object. Sanity checks next
                for key in [KEY_KIDS, KEY_COUNT]:
                    if not pdfElement.dict.get(key, None):
                        self.logger.debug("[%s] Missing a required key : %s"%(KEY_PAGES, key))
                if pdfElement.dict.has_key(KEY_COUNT):
                    self.logger.debug("[%s] %s leaf descendant node(s)"%(KEY_PAGES, int( pdfElement.dict.get(KEY_COUNT, None))))
                if pdfElement.dict.has_key(KEY_KIDS):
                    self.logger.debug("[%s] %s /Kids found " %(KEY_PAGES, len( pdfElement.dict.get(KEY_KIDS, None)) ))
                kids = pdfElement.dict.get(KEY_KIDS, None)
                if kids:
                    for kid in kids:
                        self._handle_Generic(kid, KEY_PAGE)

            elif pdfElement.dict[KEY_TYPE] == KEY_PAGE:
                # Handle a /Page object
                self.logger.debug("[%s ID:%s ] Found a new %s"%(KEY_PAGE, pdfElement.id, KEY_PAGE))
                self._readerPages += 1
                self.__executeJavaScript( "Pages[%s] = {}; Pages[%s].annotations = new Array();"%(self._readerPages, self._readerPages) , saveScript=False, isDom=True )
                for key in pdfElement.dict.keys():
                    # We are interested in /Contents, /Resources and other useful stuff
                    if key in [KEY_CONTENTS, KEY_RESOURCES, KEY_AA]:
                        self.logger.debug("[%s ID:%s ] Handling %s "%(KEY_PAGE, pdfElement.id, key))
                        self._handle_Generic( pdfElement.dict[key], key)
                    elif key == KEY_ANNOTS:
                        # This will point to a list
                        if isinstance(pdfElement.dict[key], list):
                            for annot in pdfElement.dict[key]:
                                self._handle_Generic(annot, KEY_ANNOT)

            elif pdfElement.dict[KEY_TYPE] == KEY_ANNOT:
                #/Annot object
                for key in pdfElement.dict.keys():
                    value = self._handle_Generic( pdfElement.dict[key])
                    if key == KEY_SUBJ:
                        # add this annotation to the current page
                        self.__executeJavaScript("Pages[%s].annotations.push(new app.doc.Annotation('%s'));"%(self._readerPages,value), saveScript=False, isDom=True)

            elif pdfElement.dict[KEY_TYPE] == KEY_EMBEDDEDFILE:
                #/EmbeddedFile - An Embedded File Stream Section 3.10.3
                # This could either be a stream or an /EF tag
                #(1) /EmbeddedFile based stream
                if hasattr(pdfElement, 'stream'):
                    self.logger.debug("[%s ID:%s]\033[91m Found an embedded stream. Length = %s \033[0m"%(pdfElement.dict[KEY_TYPE], pdfElement.id, len(pdfElement.stream)) )
                    return pdfElement.stream

            elif pdfElement.dict[KEY_TYPE] == KEY_FONT:
                for key in pdfElement.dict.keys():
                    self._handle_Generic( pdfElement.dict[key])

            elif pdfElement.dict[KEY_TYPE] == KEY_OUTLINES:
                for key in pdfElement.dict.keys():
                    self._handle_Generic( pdfElement.dict[key])

            elif pdfElement.dict[KEY_TYPE] == KEY_CATALOG:
                #/Catalog Object
                if KEY_OPENACTION in pdfElement.dict:
                    self.logger.debug("[%s ID:%s] /OpenAction object"%(pdfElement.dict[KEY_TYPE], pdfElement.id ) )
                    js = None
                    actionElement = pdfElement.dict[KEY_OPENACTION]
                    if isinstance(actionElement, dict):
                        if actionElement.get(KEY_S, None) == KEY_JAVASCRIPT:
                            js = actionElement.get(KEY_JS, None)
                    elif isinstance(actionElement,list):
                        # handle this condition
                        for item in actionElement:
                            # 1618d09ff580014b251794222bb0f0f9.pdf
                            self._handle_Generic( item )
                    if js:
                        self.__openActionScripts.append(js)

                if KEY_ACROFORM in pdfElement.dict:
                    self.logger.debug("[Catalog] Found %s"%(KEY_ACROFORM))
                    self.logger.debug("\tbuilding XFA from %s" % pdfElement.dict[KEY_ACROFORM])

                    xml = ''
                    if hasattr(pdfElement.dict[KEY_ACROFORM], 'objectID'):  #MALW-90
                        # Simple XFA
                        # AcroForm could be referencing a non-existant object.
                        xfaO = self.__pdfIndObjD.get( pdfElement.dict[KEY_ACROFORM].objectID, None)
                        if xfaO:
                            xml = self.__buildXFA( xfaO )

                    elif pdfElement.dict[KEY_ACROFORM].has_key(KEY_XFA):
                        # XFA is spread across a preamble, postamble, data etc
                        for _pdfObject in pdfElement.dict[KEY_ACROFORM][KEY_XFA]:
                            if isinstance(_pdfObject, PDFIndObjRef):
                                # We have an indirect object reference
                                xfaO = getattr(_pdfObject, 'objectID', None)
                                if xfaO:
                                    xml += self.__buildXFA( self.__pdfIndObjD[xfaO] )

                    if xml:
                        xmlTree, scriptL = self.__parseXML(xml)
                        for key in pdfElement.dict.keys():
                            self._handle_Generic( pdfElement.dict[key] )
                        if scriptL:
                            for _script in scriptL:
                                # eval the script in the context
                                self._increment_stats(F_C_JS_SCRIPTS_FOUND)
                                self.__executeJavaScript( _script )

                for key in pdfElement.dict.keys():
                    self.logger.debug("[%s] Handling %s"%(KEY_CATALOG, key))
                    self._handle_Generic( pdfElement.dict[key])
            else:
                #All other objects
                self.logger.debug("[%s] \033[91m Unhandled /Type found. Add support! \033[0m"%(pdfElement.dict[KEY_TYPE]))
                for key in pdfElement.dict.keys():
                    self._handle_Generic( pdfElement.dict[key] )


    def __parseXML(self, xmlStr):
        '''
        Takes in a string of XML extracted from the XFA and finds any script elements.
        Returns a tuple containing two elements:
            1) the root of the parsed XML tree structure
            2) a list of any script elements found in the tree
        '''
        # parse XML and look for 'script' elements
        self.logger.debug("Parsing XML...")

        # all JavaScript executions here are to build the DOM
        is_dom = True

        try:
            # The XML must be wrapped in a root element because there may not be just 1 root
            # after I smashed together all the xml ;]
            xml = "<xfa>%s</xfa>" % (xmlStr)
            #self.logger.info("xml: %s" % repr(xml))
            xmlTree = etree.fromstring(xml)
        except Exception, e:
            self.logger.warn("[lxml] exception from parsing XML: %s" % e)
            self.logger.info(" [lxml] going to try with html5lib..")
            return (None, None)
            import html5lib
            from html5lib import treebuilders
            parser = html5lib.HTMLParser(tree=treebuilders.getTreeBuilder("lxml"))
            xmlTree = parser.parse(xml)
        except:
            self.logger.error("[html5lib] failed to parse the XML. Giving up!")
            #TODO: Add more parsers
            return (None,None)

        # We can't just find 'script' tags because the namespace stuff it pushed into the tag
        scriptL = []

        # we now build the xfa DOM
        def buildElements(element):
            jsDOM.removeNamespace(element, self.logger)
            ancestors = []
            for ancestor in element.iterancestors():
                ancestors.append( ancestor.tag )
            ancestors.reverse()
            if ancestors:
                self.__executeJavaScript( "%s.%s = {}"%('.'.join(ancestors), element.tag) , isDom=is_dom)
            else:
                self.__executeJavaScript( "%s%s = {}"%('.'.join(ancestors), element.tag) , isDom=is_dom)
            if element.text and element.text.strip():
                if element.tag == 'script':
                    scriptL.append( element.text.strip())
                    #self.__executeJavaScript( "%s"%(element.text.strip()) )
                else:
                    self.__executeJavaScript( "%s.%s = \"%s\""%('.'.join(ancestors), element.tag,element.text.strip()) , isDom=is_dom)
                    self.__executeJavaScript("var %s = {}; %s.rawValue=\"%s\";"%(element.tag, element.tag, element.text.strip()) ,isDom=is_dom)

            for key, value in element.items():
                if key.lower() == 'name':
                    rawValue = ''
                    if element.text:
                        rawValue = element.text.strip()
                    self.__executeJavaScript("var %s = {}; %s.rawValue=\"%s\";"%(value, value, rawValue), isDom=is_dom)
                    self.__xfa__monitoredFieldNames.add(value)
                elif key.lower() == 'contenttype':
                    if value in ['image/tif','image/tiff']:
                        self.logger.debug('Found a TIFF of size %s bytes'%(len(element.text)))
                        self.logger.debug('\033[91m Potential TIFF Exploit.\033[0m');
                    elif value in ['application/x-javascript']:
                        # javascript placeholder. we know about this too.
                        pass
                    else:
                        self.logger.debug("\033[91m Unhandled Content-Type found. Please review")

            index = 0
            for childElement in element.getchildren():
                if not (type(childElement) is etree._Element and childElement.tag):
                    continue
                jsDOM.removeNamespace(childElement,self.logger)
                if ancestors:
                    self.__executeJavaScript( "%s.%s.%s = {};" % ('.'.join(ancestors), element.tag, childElement.tag), isDom=is_dom)
                    self.__executeJavaScript( "%s.%s[%d] = {};" % ('.'.join(ancestors), element.tag, index) , isDom=is_dom)
                    self.__executeJavaScript( "%s.%s[%d].%s = {};" % ('.'.join(ancestors), element.tag, index, childElement.tag) , isDom=is_dom)
                else:
                    self.__executeJavaScript( "%s%s.%s = {};" % ('.'.join(ancestors), element.tag, childElement.tag) , isDom=is_dom)
                    self.__executeJavaScript( "%s%s[%d] = {};" % ('.'.join(ancestors), element.tag, index) , isDom=is_dom)
                    self.__executeJavaScript( "%s%s[%d].%s = {};" % ('.'.join(ancestors), element.tag, index, childElement.tag) , isDom=is_dom)

                buildElements(childElement)
                index += 1

        buildElements(xmlTree)

        self.logger.debug("Found %d script elements" % len(scriptL))
        return xmlTree, scriptL

    def __buildXFA(self, pO):
        '''
        If a PDF catalog indicates there's an AcroForm, then we need to examine whatever
        object contains the "Interactive Form Dictionary" (section 8.6.1 in PDF 1.7 spec).

        The important key of this dictionary is /XFA, which indicates an Direct Object (array)
        or Indirect Object. The goal is to get out XML, and the two scenarios have rather different
        paths to getting at the XML:

            /XFA => array
                In this case, the array is a list of keys, followed by Indirect Object References
                which contain XML in a stream. The keys are usually just strings like 'preamble',
                'datasets', etc. For this scenario, we need to pull out all XML from these smoosh
                them together

            /XFA => Indirect Object Ref
                The indirect object may just have /Kids to go into recursively to find the XFA stuff
                in (could be an Array, or another IndirectObjectRef through /Kids, ...),
                or it may be of /Type /EmbeddedFile, with the XML as the EmbeddedFile stream, etc.
        '''
        xml = ''
        self.logger.debug("Checking PDF object %d for XFA entries.." % pO.id)

        if pO.dict is not None:
            # dict; check for embeddedfile
            if KEY_TYPE in pO.dict  and  pO.dict[KEY_TYPE] == KEY_EMBEDDEDFILE:
                # look for a stream
                #TODO : fix bug where non-encoded streams are not showing up in the 'stream' attr
                self.logger.info("[XFA] Found %s"%(KEY_EMBEDDEDFILE))
                xml = pO.stream

            # check for an /XFA name that points to goodies
            elif KEY_XFA in pO.dict:
                # does it point to an array...
                if type(pO.dict[KEY_XFA]) is list:
                    self.logger.debug("[XFA] Found /XFA entry; points to Array")

                    # the list contains an even number of elements: a string followed by an indirect obj reference
                    # that contains (or points to another indirect object that has) XML
                    i=0
                    while i < len(pO.dict['/XFA']):
                        element = pO.dict['/XFA'][i]

                        if type(element) in types.StringTypes:
                            # check for premable--we don't want to parse the xml refered to by the following ind obj
                            self.logger.debug("String: %s" % element)
                            if element == 'preamble' or element  == 'postamble':
                                i+= 1
                        else:
                            # Fix for bug MALW-99 : Check for proper type
                            if element.__class__.__name__ == "PDFIndObjRef":
                                if self.__pdfIndObjD.has_key(element.objectID):
                                    xml += self.followKidsWithStreams('  ', self.__pdfIndObjD[element.objectID] )

                        i += 1

                # ... or another PDF object?
                elif pO.dict[KEY_XFA].__class__.__name__ == "PDFIndObjRef":
                    self.logger.debug("Found /XFA entry; points to PDF object")

                    if self.__pdfIndObjD.has_key( pO.dict['/XFA'].objectID ):
                        xml += self.followKidsWithStreams('  ', self.__pdfIndObjD[ pO.dict['/XFA'].objectID] )

                else:
                    self.logger.debug("not a list or an Indirect PDF Obj Ref")
                    self.logger.debug("  %s" % type(pO.dict['/XFA']))
                    self.logger.debug("  %s" % pO.dict['/XFA'].__class__.__name__)

            # we may be looking at a dict that describes XFA stuff
            else:
                self.logger.debug("and um, else?")
                #TODO : handle more conditions here

        # check for preamble elements and remove them
        mO = re.search("(<\?xml .*?\?>)", xml)
        if mO:
            self.logger.debug("Found preamble in xml, removing: %s" % repr( mO.group(0) ))
            xml = xml.replace(mO.group(0), '')

        self.logger.debug("Found %d bytes of XML" % len(xml))
        return xml


    def followKidsWithStreams(self, spaces, pO):
        '''
        Used by the XFA building method, this follows an indirect obj's dictionary which indicates
        that it has children, collecting all XML found in streams along the way (recursive).

        Returns a string containing XML.
        '''
        self.logger.debug("%sChecking for Kids in %s" % (spaces, pO))

        # check for dictionary
        if pO.dict is None:
            self.logger.warn("%s -- Was asked to follow an indirect object, but it has no dict!" % spaces)
            return ''

        xml = ''

        # check for /Kids
        if '/Kids' in pO.dict:
            self.logger.debug("%s  Found %d kids.." % (spaces, len(pO.dict['/Kids'])))
            spaces += "    "

            for kidIndObj in pO.dict['/Kids']:
                kidObj = self.__pdfIndObjD[ kidIndObj.objectID ]
                xml += self.followKidsWithStreams(kidObj)

        # check for a stream & xml
        if hasattr(pO, 'stream'):
            self.logger.debug("%s  Found a stream (%d bytes)" % (spaces, len(pO.stream)))
            xml += pO.stream # check if it actually looks like xml? nah...
            self.logger.debug("%s    %s" % (spaces, repr(pO.stream[:256])))

        return xml
