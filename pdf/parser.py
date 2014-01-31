'''
PDF Parser
This file is part of the phoneyPDF Framework

Kiran Bandla <kbandla@intovoid.com>
Trevor Tonn <smthmlk@gmail.com>

Please see the LICENSE file for copyright information

This file is based on Didier Stevens pdf-parser.
It has been greatly extended to work with various PDFs found in the wild.
Below are docstring's from Didier's original file indicating when we diverged from his tool..

-------------------------------------------------------------------------
__description__ = 'pdf-parser, use it to parse a PDF document'
__author__ = 'Didier Stevens'
__version__ = '0.3.7'
__date__ = '2010/01/09'

Source code put in public domain by Didier Stevens, no Copyright
https://DidierStevens.com
Use at your own risk

History:
  2008/05/02: continue
  2008/05/03: continue
  2008/06/02: streams
  2008/10/19: refactor, grep & extract functionality
  2008/10/20: reference
  2008/10/21: cleanup
  2008/11/12: V0.3 dictionary parser
  2008/11/13: option elements
  2008/11/14: continue
  2009/05/05: added /ASCIIHexDecode support (thanks Justin Prosco)
  2009/05/11: V0.3.1 updated usage, added --verbose and --extract
  2009/07/16: V0.3.2 Added Canonicalize (thanks Justin Prosco)
  2009/07/18: bugfix EqualCanonical
  2009/07/24: V0.3.3 Added --hash option
  2009/07/25: EqualCanonical for option --type, added option --nocanonicalizedoutput
  2009/07/28: V0.3.4 Added ASCII85Decode support
  2009/08/01: V0.3.5 Updated ASCIIHexDecode to support whitespace obfuscation
  2009/08/30: V0.3.6 TestPythonVersion
  2010/01/08: V0.3.7 Added RLE and LZW support (thanks pARODY); added dump option
  2010/01/09: Fixed parsing of incomplete startxref

Todo:
  - handle printf todo
  - check 'real raw' option
  - fix PrettyPrint
  - support for JS hex string EC61C64349DB8D88AF0523C4C06E0F4D.pdf.vir
'''

# Local imports
from filters import *
from utils import *

# Core Charecter class
def CharacterClass(byte):
    if byte in [
            0,      #   NUL
            9,      #   TAB
            10,     #   LF
            12,     #   FF
            13,     #   CR
            32      #   Space
            ]:
        return CHAR_WHITESPACE
    if byte in [
            0x28,   #   (
            0x29,   #   )
            0x3C,   #   <
            0x3E,   #   >
            0x5B,   #   [
            0x5D,   #   ]
            0x7B,   #   {
            0x7D,   #   }
            0x2F,   #   /
            0x25    #   %
            ]:
        return CHAR_DELIMITER
    return CHAR_REGULAR


class cPDFDocument:
    def __init__(self, file_sio):
        self.file = file
        #self.infile = open(file, 'rb')
        self.infile = file_sio
        self.ungetted = []
        self.position = -1

    def byte(self):
        if len(self.ungetted) != 0:
            self.position += 1
            return self.ungetted.pop()
        inbyte = self.infile.read(1)
        if not inbyte:
            self.infile.close()
            return None
        self.position += 1
        return ord(inbyte)

    def unget(self, byte):
        self.position -= 1
        self.ungetted.append(byte)

class cPDFTokenizer:
    def __init__(self, file):
        self.oPDF = cPDFDocument(file)
        self.ungetted = []

    def Token(self):
        if len(self.ungetted) != 0:
            return self.ungetted.pop()
        if self.oPDF == None:
            return None
        self.byte = self.oPDF.byte()

        # @kbandla
        # Deal with backslashes for escaped bytes
        if self.byte == 0x5C:   # a backslash
            # Need to lookahead to see the next byte
            self.byte = self.oPDF.byte()
            if self.byte in [
                        0xA,    # Line Feed
                        0xD,    # Carriage return
                        0x9,    # Horizontal tab
                        0x8,    # Backspace
                        0xC,    # Form feed
                        0x28,   # (
                        0x29,   # )
                        0x5C,   # Backslash \
                                # TODO: We also need to cover octal numbers here. Example : \000
                        ]:
                # Was surely an escape backslash, so just consume the most recent byte as a CHAR_REGULAR
                self.token = ''
                self.token = self.token + chr(self.byte)
                return (CHAR_REGULAR, self.token)
            else:
                # The (previous) backslash was not an escape sequence. Lets restore stuff
                self.oPDF.unget(self.byte)  # Restore the lookahead byte
                # Move on as if we were not involved
                self.byte = 0x5C

        if self.byte == None:
            self.oPDF = None
            return None
        elif CharacterClass(self.byte) == CHAR_WHITESPACE:
            self.token = ''
            while self.byte != None and CharacterClass(self.byte) == CHAR_WHITESPACE:
                self.token = self.token + chr(self.byte)
                self.byte = self.oPDF.byte()
            if self.byte != None:
                self.oPDF.unget(self.byte)
            else:
                self.oPDF = None
            return (CHAR_WHITESPACE, self.token)
        elif CharacterClass(self.byte) == CHAR_REGULAR:
            self.token = ''
            while self.byte != None and CharacterClass(self.byte) == CHAR_REGULAR:
                self.token = self.token + chr(self.byte)
                self.byte = self.oPDF.byte()
            if self.byte != None:
                self.oPDF.unget(self.byte)
            else:
                self.oPDF = None
            return (CHAR_REGULAR, self.token)
        else:
            if self.byte == 0x3C:   # '<'
                self.byte = self.oPDF.byte()
                if self.byte == 0x3C:
                    return (CHAR_DELIMITER, '<<')
                else:
                    self.oPDF.unget(self.byte)
                    return (CHAR_DELIMITER, '<')
            elif self.byte == 0x3E:     # '>'
                self.byte = self.oPDF.byte()
                if self.byte == 0x3E:
                    return (CHAR_DELIMITER, '>>')
                else:
                    self.oPDF.unget(self.byte)
                    return (CHAR_DELIMITER, '>')
            elif self.byte == 0x25: #   '%'
                # @kbandla
                # NOT all line containing % are comments.
                # % is only defined outside a string or stream
                # TODO: To fix this, we will need a mini FSM. Will do this later
                self.token = ''
                while self.byte != None:
                    self.token = self.token + chr(self.byte)
                    if self.byte == 10 or self.byte == 13:  # LF or CR
                        self.byte = self.oPDF.byte()
                        break
                    self.byte = self.oPDF.byte()
                if self.byte != None:
                    if self.byte == 10: # LF
                        self.token = self.token + chr(self.byte)
                    else:
                        self.oPDF.unget(self.byte)
                else:
                    self.oPDF = None
                return (CHAR_DELIMITER, self.token)
            return (CHAR_DELIMITER, chr(self.byte))

    def TokenIgnoreWhiteSpace(self):
        token = self.Token()
        while token != None and token[0] == CHAR_WHITESPACE:
            token = self.Token()
        return token

    def unget(self, byte):
        self.ungetted.append(byte)

class cPDFParser:
    def __init__(self, file, verbose=False, extract=None, logger=None):
        self.context = CONTEXT_NONE
        self.content = []
        self.oPDFTokenizer = cPDFTokenizer(file)
        self.verbose = verbose
        self.extract = extract
        self.logger = logger

        self.trailerStarted = False
        self.trailerDone = False
        self.dict = None
        self.array = None
        self.stream = None

    def parseTokens(self, pO):
        '''
        Parse for tokens in a pdfObject
        '''
        self.logger.debug("\n\n<> Parsing tokens of %s..." % pO)

        if pO.type == pdfObjTypeD["PDF_ELEMENT_INDIRECT_OBJECT"]:
            # An indirect object is likely to contain a dictionary or a stream, or both

            # Examining the tokens
            if pO.content:
                # Remove whitespace tokens on either end of the token list
                pO.content = TrimLWhiteSpace(TrimRWhiteSpace(pO.content))
                self.logger.debug(" > tokens: %s .. %s " % (str(pO.content[0:4]),str(pO.content[-5:-1])))

                # try to parse the tokens down into direct objects (but not streams, yet)
                pdfDirectObj = PDFDirectObjectParser(self.logger, pO.content, True)

                self.logger.debug("checking for direct object...")
                if pdfDirectObj.dict is not None:
                    pO.dict = pdfDirectObj.dict
                    self.logger.debug(" ...found dict.")
                elif pdfDirectObj.array is not None:
                    pO.array = pdfDirectObj.array
                    self.logger.debug(" ...found array.")
                elif pdfDirectObj.stream is not None:
                    pO.stream = pdfDirectObj.stream
                    self.logger.debug(" ... found stream.")
                else:
                    self.logger.debug(" ..has no direct object")


                # STREAM: try to parse a stream from the tokens; we'll go ahead and filter it now as well
                stream = pO.Stream(filter=True)
                if stream:
                    self.logger.debug(" > contains \033[33mstream\033[0m: %s" % repr(stream[:100]))
                    pO.stream = stream

        elif pO.type == pdfObjTypeD["PDF_ELEMENT_TRAILER"]:
            # Examining the tokens
            if pO.content:
                # Remove whitespace tokens on either end of the token list
                pO.content = TrimLWhiteSpace(TrimRWhiteSpace(pO.content))

                # remove the opening 'trailer' token
                if pO.content[0][1] == 'trailer':
                    pO.content.pop(0)

                self.logger.debug(" > tokens: %s" % str(pO.content[:100]))

                # try to parse the tokens down into direct objects (but not streams, yet)
                pdfDirectObj = PDFDirectObjectParser(self.logger, pO.content, True)
                self.logger.debug("checking for direct object...")
                if pdfDirectObj.dict is not None:
                    pO.dict = pdfDirectObj.dict
                    self.logger.debug(" ...found dict.")
                elif pdfDirectObj.array is not None:
                    pO.array = pdfDirectObj.array
                    self.logger.debug(" ...found array.")
                else:
                    self.logger.debug(" ..has no direct object")

        elif pO.type == pdfObjTypeD["PDF_ELEMENT_XREF"]:
            pass
            #print pO.content

    def GetObject(self):
        while True:
            #print "context: %d / %d" % (self.context, CONTEXT_TRAILER)
            #if self.context == 4:
            #    print self.content

            if self.context == CONTEXT_OBJ:
                self.token = self.oPDFTokenizer.Token()
            else:
                self.token = self.oPDFTokenizer.TokenIgnoreWhiteSpace()

            if self.token:
                if self.token[0] == CHAR_DELIMITER:
                    #print "delimiter found; token=%s" % str(self.token)

                    if self.token[1][0] == '%':
                        if self.context == CONTEXT_OBJ:
                            self.content.append(self.token)
                        else:
                            return cPDFElementComment(self.token[1])
                    elif self.token[1] == '/':
                        self.token2 = self.oPDFTokenizer.Token()
                        if self.token2:
                            if self.token2[0] == CHAR_REGULAR:
                                if self.context != CONTEXT_NONE:
                                    self.content.append((CHAR_DELIMITER, self.token[1] + self.token2[1]))
                                elif self.verbose:
                                    print 'todo 1: %s' % (self.token[1] + self.token2[1])
                            else:
                                self.oPDFTokenizer.unget(self.token2)
                                if self.context != CONTEXT_NONE:
                                    self.content.append(self.token)
                                elif self.verbose:
                                    print 'todo 2: %d %s' % (self.token[0], repr(self.token[1]))
                    elif self.context != CONTEXT_NONE:
                        self.content.append(self.token)
                    elif self.verbose:
                        print 'todo 3: %d %s' % (self.token[0], repr(self.token[1]))
                elif self.token[0] == CHAR_WHITESPACE:
                    if self.context != CONTEXT_NONE:
                        self.content.append(self.token)
                    elif self.verbose:
                        print 'todo 4: %d %s' % (self.token[0], repr(self.token[1]))
                else:
                    #print "non delimiter, non-whitespace token: %s" % self.token[1]
                    # sometimes, we reach here when our token is 'trailer'

                    if self.context == CONTEXT_OBJ:
                        # sometimes, endobj and xref are not seperated with a delimiter
                        # in which case, self.token = 'endobjxref' or something like it
                        #if self.token[1] == 'endobj':
                        if 'endobj' in self.token[1]:
                            self.oPDFElementIndirectObject = cPDFElementIndirectObject(self.objectId, self.objectVersion, self.content, self.logger)
                            self.context = CONTEXT_NONE
                            self.content = []

                            self.parseTokens(self.oPDFElementIndirectObject)
                            return self.oPDFElementIndirectObject

                        else:
                            self.content.append(self.token)

                    elif self.context == CONTEXT_TRAILER:
                        if self.token[1] == 'startxref' or self.token[1] == 'xref':
                            self.oPDFElementTrailer = cPDFElementTrailer(self.content)
                            self.oPDFTokenizer.unget(self.token)
                            self.context = CONTEXT_NONE
                            self.content = []
                            self.trailerDone = True
                            self.parseTokens(self.oPDFElementTrailer)
                            return self.oPDFElementTrailer

                        else:
                            self.content.append(self.token)

                    elif self.context == CONTEXT_XREF:
                        if self.token[1] == 'trailer' or self.token[1] == 'xref':
                            self.oPDFElementXref = cPDFElementXref(self.content)
                            self.oPDFTokenizer.unget(self.token)
                            self.context = CONTEXT_NONE
                            self.content = []

                            self.parseTokens(self.oPDFElementXref)
                            return self.oPDFElementXref

                        else:
                            self.content.append(self.token)

                    else:
                        if IsNumeric(self.token[1]):
                            self.token2 = self.oPDFTokenizer.TokenIgnoreWhiteSpace()
                            if IsNumeric(self.token2[1]):
                                self.token3 = self.oPDFTokenizer.TokenIgnoreWhiteSpace()
                                if self.token3[1] == 'obj':
                                    self.objectId = eval(self.token[1])
                                    self.objectVersion = eval(self.token2[1])
                                    self.context = CONTEXT_OBJ
                                else:
                                    self.oPDFTokenizer.unget(self.token3)
                                    self.oPDFTokenizer.unget(self.token2)
                                    if self.verbose:
                                        print 'todo 6: %d %s' % (self.token[0], repr(self.token[1]))
                            else:
                                self.oPDFTokenizer.unget(self.token2)
                                if self.verbose:
                                    print 'todo 7: %d %s' % (self.token[0], repr(self.token[1]))
                        elif self.token[1] == 'trailer':
                            #print "trailer keyword found"
                            self.context = CONTEXT_TRAILER
                            self.content = [self.token]
                            self.trailerStarted = True
                            self.trailerDone = False

                        elif self.token[1] == 'xref':
                            #print "xref keyword found"
                            self.context = CONTEXT_XREF
                            self.content = [self.token]

                        elif self.token[1] == 'startxref':
                            #print "startxref found"
                            self.token2 = self.oPDFTokenizer.TokenIgnoreWhiteSpace()
                            if self.token2 and IsNumeric(self.token2[1]):
                                return cPDFElementStartxref(eval(self.token2[1]))
                            else:
                                self.oPDFTokenizer.unget(self.token2)
                                if self.verbose:
                                    print 'todo 9: %d %s' % (self.token[0], repr(self.token[1]))
                        elif self.extract:
                            self.bytes = ''
                            while self.token:
                                self.bytes += self.token[1]
                                self.token = self.oPDFTokenizer.Token()
                            return cPDFElementMalformed(self.bytes)
                        elif self.verbose:
                            print 'todo 10: %d %s' % (self.token[0], repr(self.token[1]))
            else:
                # if there's an object sitting here, lets try to push it out; it's likely an trailer or xref that's unfinished
                # because didier is waiting for stuff to show up in the file that's not required
                if self.content and self.trailerStarted and not self.trailerDone:
                    self.oPDFElementTrailer = cPDFElementTrailer(self.content)
                    self.oPDFTokenizer.unget(self.token)
                    self.context = CONTEXT_NONE
                    self.content = []
                    self.trailerDone = True
                    self.parseTokens(self.oPDFElementTrailer)
                    return self.oPDFElementTrailer

                break

class PDFElement:
    id = None

    __pdfObjTypeD = {   1: "PDF_ELEMENT_COMMENT",
                        2: "PDF_ELEMENT_INDIRECT_OBJECT",
                        3: "PDF_ELEMENT_XREF",
                        4: "PDF_ELEMENT_TRAILER",
                        5: "PDF_ELEMENT_STARTXREF",
                        6: "PDF_ELEMENT_MALFORMED" }

    def __repr__(self):
        return "\033[31;1m<PDFElement\033[0;31m id:\033[0m%s \033[31mtype:\033[0m%s \033[31;1m>\033[0m" % (self.id, self.__pdfObjTypeD[self.type])
class cPDFElementComment(PDFElement):
    def __init__(self, comment):
        self.type = PDF_ELEMENT_COMMENT
        self.comment = comment
class cPDFElementXref(PDFElement):
    def __init__(self, content):
        self.type = PDF_ELEMENT_XREF
        self.content = content

class cPDFElementTrailer(PDFElement):
    def __init__(self, content):
        self.type = PDF_ELEMENT_TRAILER
        self.content = content

class cPDFElementIndirectObject(PDFElement):
    def __init__(self, id, version, content, logger=None):
        self.type = PDF_ELEMENT_INDIRECT_OBJECT
        self.id = id
        self.version = version
        self.content = content
        self.dict = None
        self.array = None
        self.logger = logger


    def GetType(self):
        content = CopyWithoutWhiteSpace(self.content)
        dictionary = 0
        for i in range(0, len(content)):
            if content[i][0] == CHAR_DELIMITER and content[i][1] == '<<':
                dictionary += 1
            if content[i][0] == CHAR_DELIMITER and content[i][1] == '>>':
                dictionary -= 1
            if dictionary == 1 and content[i][0] == CHAR_DELIMITER and EqualCanonical(content[i][1], '/Type') and i < len(content) - 1:
                return content[i+1][1]
        return ''

    def GetReferences(self):
        content = CopyWithoutWhiteSpace(self.content)
        references = []
        for i in range(0, len(content)):
            if i > 1 and content[i][0] == CHAR_REGULAR and content[i][1] == 'R' and content[i-2][0] == CHAR_REGULAR and IsNumeric(content[i-2][1]) and content[i-1][0] == CHAR_REGULAR and IsNumeric(content[i-1][1]):
                references.append((content[i-2][1], content[i-1][1], content[i][1]))
        return references

    def References(self, index):
        for ref in self.GetReferences():
            if ref[0] == index:
                return True
        return False

    def ContainsStream(self):
        for i in range(0, len(self.content)):
            if self.content[i][0] == CHAR_REGULAR and self.content[i][1] == 'stream':
                return self.content[0:i]
        return False

    def Contains(self, keyword):
        data = ''
        for i in range(0, len(self.content)):
            if self.content[i][1] == 'stream':
                break
            else:
                data += Canonicalize(self.content[i][1])
        return data.upper().find(keyword.upper()) != -1

    def Stream(self, filter=True):
        state = 'start'
        countDirectories = 0
        data = ''
        filters = []

        for i in range(0, len(self.content)):
            if state == 'start':

                if self.content[i][0] == CHAR_DELIMITER and self.content[i][1] == '<<':
                    countDirectories += 1
                if self.content[i][0] == CHAR_DELIMITER and self.content[i][1] == '>>':
                    countDirectories -= 1
                if countDirectories == 1 and self.content[i][0] == CHAR_DELIMITER and EqualCanonical(self.content[i][1], '/Filter'):
                    state = 'filter'
                # Trevors addition: there can be embedded files that are NOT compressed/require filtering
                if countDirectories == 0 and self.content[i][0] == CHAR_REGULAR and self.content[i][1] == 'stream':
                    state = 'stream-whitespace'

            elif state == 'filter':
                if self.content[i][0] == CHAR_DELIMITER and self.content[i][1][0] == '/':
                    filters = [self.content[i][1]]
                    state = 'search-stream'
                elif self.content[i][0] == CHAR_DELIMITER and self.content[i][1] == '[':
                    state = 'filter-list'
            elif state == 'filter-list':
                if self.content[i][0] == CHAR_DELIMITER and self.content[i][1][0] == '/':
                    filters.append(self.content[i][1])
                elif self.content[i][0] == CHAR_DELIMITER and self.content[i][1] == ']':
                    state = 'search-stream'
            elif state == 'search-stream':
                if self.content[i][0] == CHAR_REGULAR and self.content[i][1] == 'stream':
                    state = 'stream-whitespace'
            elif state == 'stream-whitespace':
                if self.content[i][0] != CHAR_WHITESPACE:
                    data += self.content[i][1]
                state = 'stream-concat'
            elif state == 'stream-concat':
                if self.content[i][0] == CHAR_REGULAR and self.content[i][1] == 'endstream':
                    if filter and filters: # Trevors addition: we need to try to decompress only if we found a filter
                        try:
                            return self.Decompress(data, filters)
                        except DecompressException as e:
                            self.logger.debug('%s %s'%(e.filter, e.msg))
                            return data
                    else:
                        return data
                else:
                    data += self.content[i][1]
            else:
                # Unexpected filter state
                return False
        return filters

    def Decompress(self, data, filters):
        for filter in filters:
            try:
                if EqualCanonical(filter, '/FlateDecode') or EqualCanonical(filter, '/Fl'):
                    data = FlateDecode(data)
                elif EqualCanonical(filter, '/ASCIIHexDecode') or EqualCanonical(filter, '/AHx'):
                    data = ASCIIHexDecode(data)
                elif EqualCanonical(filter, '/ASCII85Decode') or EqualCanonical(filter, '/A85'):
                    data = ASCII85Decode(data.rstrip('>'))
                elif EqualCanonical(filter, '/LZWDecode') or EqualCanonical(filter, '/LZW'):
                    data = LZWDecode(data)
                elif EqualCanonical(filter, '/RunLengthDecode') or EqualCanonical(filter, '/R'):
                    data = RunLengthDecode(data)
                else:
                    raise DecompressException(filter)
            except:
                raise DecompressException(filter)

        if len(filters) == 0:
            # No filters; returning data anyways'
            return data
        return data

class cPDFElementStartxref(PDFElement):
    def __init__(self, index):
        self.type = PDF_ELEMENT_STARTXREF
        self.index = index

class cPDFElementMalformed(PDFElement):
    def __init__(self, content):
        self.type = PDF_ELEMENT_MALFORMED
        self.content = content

class PDFIndObjRef:
    def __init__(self, objectID, generation):
        self.objectID = objectID
        self.generation = generation
        self.indObject = None # set later; if left none, this is considered 'null'

    def __repr__(self):
        return "\033[33;1m<PDFIndObjRef \033[0;32mid=\033[0m%d \033[32mgen=\033[0m%d\033[33;1m>\033[0m" % (self.objectID, self.generation)

class PDFDirectObjectParser:
    def __init__(self, logger, content, nocanonicalizedoutput, indent=5):
        self.logger = logger
        self.dict = None
        self.array = None
        self.stream = None
        self.string = None
        self.numner = None
        self.content = content[:] # we do not want to modify the list given to us
        self.indent = indent
        self.nocanonicalizedoutput = nocanonicalizedoutput

        self.parseObjectTokens(content)

    def parseObjectTokens(self, tokens):
        if self.isOpenDictionary(self.content[0]):
            self.logger.debug("parsing dict...")
            try:
                self.dict = self.parseDictionary(self.content, 5)
            except DictParseException as e:
                # Lets use whatever we could parse so far
                # Most of the times, this has the /Action and /URL keys
                self.dict = e.dictionary
                self.logger.warn("Could not parse the complete dictionary")
            except (MalformedPDFException, Exception) as e:
                self.dict = None
                self.logger.warn("Error parsing dictionary [%s]"% e)

            if self.dict is None:
                self.logger.warn("Error parsing dictionary")
            elif len(self.dict) == 0:
                self.logger.debug("returned dict has no key/values!")
            else:
                self.logger.debug("returned dict has %d keys" % len(self.dict))


        elif self.isOpenArray(self.content[0]):
            try:
                self.array = self.parseArray(self.content, 5)
            except ArrayParseException as e:
                self.array = e.array
                self.logger.warn("Could not parse the complete array")
            except (MalformedPDFException, Exception) as e:
                self.array = None
                self.logger.warn("Error parsing array. [%s]"% e)

        elif self.isStream(self.content[0]):
            self.logger.debug('Found a stream in a Direct object. No Dictionary or Array found')
            self.stream = self.parseStream(self.content)

        elif self.isOpenString(self.content[0]):
            self.logger.debug('Found a string in a Direct Object')
            try:
                self.string =   self.parseString(self.content)
            except StringParseException as e:
                self.string = e.string
                self.logger.warn("Could not parse the complete string")
            except (MalformedPDFException, Exception) as e:
                self.string = None
                self.logger.warn("Error parsing string. [%s]"% e)

        elif self.isOpenKey(self.content[0]):
            self.logger.debug('Found a naked key in the object, with out << or >>')
            self.dict = self.parseDictionary(self.content)

        elif self.isNumber(self.content[0]):
            self.logger.debug('Found an Integer in the object.');
            self.number = self.parseNumeric(self.content[0])

        else:
            print "the initial tokens do not indicate that they describe an Array or Dictionary (missing '<<' or '[')"

    ''' The following short methods parse direct objects based on their opening token '''
    def isOpenDictionary(self, token):
        return token[0] == CHAR_DELIMITER and token[1] == '<<'

    def isCloseDictionary(self, token):
        return token[0] == CHAR_DELIMITER and token[1] == '>>'

    def isOpenArray(self, token):
        return token[0] == CHAR_DELIMITER and token[1] == '['

    def isCloseArray(self, token):
        return token[0] == CHAR_DELIMITER and token[1] == ']'

    def isStream(self, token):
        return token[0] == CHAR_REGULAR and token[1] == 'stream'

    def isOpenString(self, token):
        return token[0] == CHAR_DELIMITER and token[1] == '('

    def isCloseString(self, token):
        return token[0] == CHAR_DELIMITER and token[1] == ')'

    def isOpenKey(self, token):
        return token[0] == CHAR_DELIMITER and token[1][0] == '/'

    def isNumber(self, token):
        try:
            x = int(token[1][0])
            if x: return True
        except:
            return False

    ''' These parse the single-token direct objects, such as numbers or bools '''
    def parseStream(self,tokens):
        stream = []
        if tokens[0][0] == CHAR_REGULAR and tokens[0][1].lower() == 'stream' and tokens[-1][1].lower() == 'endstream':
            stream = [ _token[1] for _token in tokens[1:-1]]
            return ''.join(stream)
        else:
            return ''

    def parseBoolean(self, token):
        '''
        Determines if the token passed is a 'bool' direct object.
            PDF syntax examples, section 3.2.1 pg52:
                    true
                    false

        Returns True or False python objects if the token is a boolean direct object. Returns None if it
        is not. Please be careful when using this to parse--you must explicitly check for None!
        '''
        if token[0] == CHAR_REGULAR:
            if token[1] == "true":
                return True
            if token[1] == "false":
                return False

        return None


    def parseName(self, token):
        '''
        Determines if the token passed is a 'name' direct object.
            PDF syntax examples, section 3.2.4 pg56:
                /Type
                /S
                /Marked

        TODO: add ability to parse names w/ odd char encodings. Ex: /Type == /#84#121#112e

        Returns the name string if a name object is parsed; returns None otherwise.
        '''

        if token[0] == CHAR_DELIMITER and token[1][0] == '/':
            if '#' in token[1]:
                # @kbandla
                # hex-encoded? decode it!
                return hex_decode(token[1])
            else:
                return token[1]

        return None


    def parseNull(self, token):
        '''
        Determines if the token passed is a null direct object.
            PDF syntax example:
                null

        Returns True if this is the null object; False otherwise
        '''
        if token[0] == CHAR_REGULAR and token[1] == 'null':
            return True

        return False


    def parseNumeric(self, token):
        '''
        Determines if the token passed is a 'Numeric' direct object.
            PDF syntax examples, section 3.2.2 pg52:
                123
                +17
                -.002
                0.0
                0

        Returns a float if the token is a numeric; returns None otherwise.
        '''
        if token[0] == CHAR_REGULAR:
            try:
                numeric = float( token[1] )
            except ValueError:
                return None
            else:
                return numeric

        return None


    def parseIndObjRef(self, tokens, peek):
        '''
        Determines if the tokens given describe a reference to an indirect object. The form is as follows:
            int int R

        ... where the first int is a unique object id, the second int is often 0, but can increment past
        that, and the 'R' is a constant.

        Arguments:
        tokens          --  A list of tokens to examine
        peek            --  A boolean that indicates whether we're just peeking, or if we should consume
                            tokens in the provided token stream; if set to False and this method finds
                            an ind obj ref, the passed list of tokens will be 5 tokens shorter

        Returns a PDFObjRef object if the tokens indicate one; returns None otherwise.
        '''
        # two kinds: int ws int ws R    vs.   int int R

        # int int R first
        if len(tokens) < 3:
            return None

        if tokens[2][0] == CHAR_REGULAR and tokens[2][1] == 'R' and self.parseNumeric(tokens[0]) != None and self.parseNumeric(tokens[1]) != None:
            oID = int( self.parseNumeric(tokens[0]) )
            generation = int( self.parseNumeric(tokens[1]) )

            if not peek:
                for i in xrange(2):
                    tokens.pop(0)

            return PDFIndObjRef(oID, generation)


        # int ws int ws R second:
        # There will 3 non-whitespace tokens and at least 2 whitespace tokens, so we need 5 tokens to
        # make this determination. If we have less than that, we are not looking at an indirect obj ref.
        if len(tokens) < 5:
            return None

        # second & fourth should be whitespace
        if tokens[1][0] == CHAR_WHITESPACE and tokens[3][0] == CHAR_WHITESPACE and tokens[4][0] == CHAR_REGULAR and tokens[4][1] == 'R' and self.parseNumeric(tokens[0]) != None and self.parseNumeric(tokens[2]) != None:
            oID = int( self.parseNumeric(tokens[0]) )
            generation = int( self.parseNumeric(tokens[2]) )

            # We have an indirect object reference; return an instance after chewing through 5 tokens
            if not peek:
                for i in xrange(4):
                    tokens.pop(0)

            return PDFIndObjRef(oID, generation)

        return None


    def parseString(self, tokens):
        '''
        Determines if the tokens given describe a string object. There are several ways to define a string in PDFs,
        and this method covers those defined in the spec.
            PDF syntax exmaples, section 3.2.3 pg53:
                (muffins are happy in the sun)
                <A1F310414190>

        Returns a string if the tokens describe a PDF string object in either of the two styles; returns None otherwise.
        '''
        if tokens[0][0] == CHAR_DELIMITER:

            # Parenthesis/ascii style
            if tokens[0][1][0] == '(':
                # the chars that make up this string lie over many tokens; we need to traverse them and keep track
                # of the number of parentheses we see
                numOpenParens = 1
                done = False

                # If we fail to find a proper termination paren, we need to push back all the popped tokens
                # in the correct order -- this list will help us do that if we need to
                poppedTokensL = []

                # where the str contents will be kept
                y=[]

                # we need to progress to the next token since we're still on '('
                token = tokens.pop(0)

                while not done:
                    # do we have any tokens left?
                    try:
                        token = tokens.pop(0)
                    except Exception, e:
                        #self.logger.error("Ran out of tokens while attempting to parse (string): %s" % e)
                        raise StringParseException("Ran out of tokens while attempting to parse (string): %s" % e, ''.join(y))
                        # At this point, Reader tries to 'Rebuild' the pdf and re-attempt rendering it
                        # TODO: Research more on Adobe's 'Rebuild'ing
                        # Example : 9e6894a736268760fa37861b429606bc

                        # push back tokens?
                        return None

                    poppedTokensL.append(token)

                    if token[0] == CHAR_DELIMITER:
                        if token[1] == '(':
                            numOpenParens += 1

                        elif token[1] == ')':
                            numOpenParens -= 1

                        elif token[1] == '>>':
                            # We should *never* reach here when parsing a 'String'
                            # HACK ALERT!!!
                            # Lets wrap the parsing here and consume the string so far and exit
                            # and lets also add the Dictionary end token tuple to the tokens
                            # to keep parseObjectTokens() method happy
                            # The consumed string would still have an extra ')' :( #TODO - fix that
                            tokens.append(token)
                            numOpenParens = 0

                        if numOpenParens == 0:
                            # We found the end of the string
                            done = True
                            continue

                    y.append( token[1] )
                    #print "added %s" % token[1]

                if poppedTokensL:
                    tokens.insert(0, poppedTokensL.pop())

                return ''.join(y)

            # bracket/hex style
            elif tokens[0][1][0] == '<' and not tokens[0][1].startswith("<<"):
                # @kbandla: Some PDFs have Dictionary key/values like this:
                #   /Name <>
                #   /Address <>
                # Example PDF : 0116ba0ccc9cdb12a2b9f9d0f00a3f13
                # To handle these, pop till end of > and return ''
                if tokens[0][1] == '>':
                    tokens.pop(0)
                    return ''

                poppedTokensL = []
                done = False
                y = []

                while not done:
                    token = tokens.pop(0)
                    poppedTokensL.append(token)
                    if (token[0] == CHAR_REGULAR):
                        y.append(token[1])
                    if (token[0] == CHAR_DELIMITER) and (token[1] == '>'):
                        done = True
                string = ''.join(y)
                if poppedTokensL:
                    tokens.insert(0, poppedTokensL.pop())
                return string

                # TODO: get rid of old code below
                tokens.pop(0)
                i=0
                y=[]

                # all of the chars that make up the hex lie in one token
                x = tokens[0][1]

                # @kbandla: The next 3 lines pop till end of > and ret '' ( zero string )
                # Example PDF : 0116ba0ccc9cdb12a2b9f9d0f00a3f13
                if x == '>':
                    tokens.pop(0)
                    return ''

                if len(x) % 2 != 0:
                    x += '0'

                while i < len(x):
                    y.append( chr( int( "%s%s" % (x[i], x[i+1]), 16 ) ) )
                    i += 2

                if tokens[1][1] == '>':
                    tokens.pop(0)

                return ''.join(y)

        return None


    ''' The following two methods build up direct object collections recursively '''
    def parseDictionary(self, tokens, indent=5):
        state = 0 # start
        key = ''
        value = None
        dictionary = {}
        while tokens != []:
            self.logger.debug("%s\033[45m  State:\033[2m%d\033[0;45m Token: \033[1m%d\033[0;45m, \033[36m%s  \033[0m" % (indent*' ', state, tokens[0][0], tokens[0][1][:30]))

            if state == 0:
                if self.isOpenDictionary(tokens[0]):
                    state = 1
                else:
                    return None

            elif state == 1:
                # STATE 1: we're looking for keys
                # Keys must be a Name object.
                if self.isOpenDictionary(tokens[0]):
                    # we can't have "<< <<", so we have to pass here
                    # we should raise an exception on a damaged PDF file
                    raise MalformedPDFException('found dictionary in place of key, not allowed!')

                elif self.isCloseDictionary(tokens[0]):
                    self.logger.debug("%s{} done" % (indent*' '))
                    return dictionary

                elif tokens[0][0] == CHAR_WHITESPACE:
                    pass

                elif tokens[0][0] == CHAR_DELIMITER:
                    # Check to see if we've found a Name object
                    name = self.parseName(tokens[0])
                    if name is not None:
                        key = ConditionalCanonicalize(tokens[0][1], self.nocanonicalizedoutput)
                        if '#' in key:
                            key = hex_decode(key)
                        self.logger.debug("%s  [key] found name: \033[33;1m%s\033[0m" % (indent*' ', key))
                        value = None
                        state = 2

                    elif tokens[0][1][0] == '%':
                        # @kbandla
                        # This is a trick used by some exploit kits.
                        # Bascially, everything after a % till the end of a line is a comment.
                        # We still stay in the same state, because we are still looking for a key
                        tokens.pop(0)
                    else:
                        # this token is not a name, so it's an error that we can't recover from
                        key = ConditionalCanonicalize(tokens[0][1], self.nocanonicalizedoutput)
                        raise DictParseException("found non-name entry for dictionary key: %s" % key, dictionary)

                elif tokens[0][0] == CHAR_REGULAR:
                    # error: we cannot use anything but names here
                    # Sometimes, we see a stream in an object, before the object's ending delimiter (>>)
                    # Reader does not run these files. ( Tested against 8, 9 )
                    # Example PDFs:
                    #   050b0add9a8a1d18e6007018c6c3be34
                    #   0eacf0bb94acf66f199f5590b0cb60ad
                    #   3536a2492e7faae4375e2878a4c6128f
                    #   48e0cc8629d492a64a2767949d2ed9bc
                    #   6f3b2f8bc23e141a180b626fb28d0dbb
                    #   e88c3a7cac02dcac9168b9990b780e62
                    #   df9b71ea09d979b6e29feace47885277
                    #   adff972dc467e20527c82ac0ea8a5a86
                    #   b417207b69c51ef5fcc61e2009917ac6    -    This seems like an exploit. Not stream.
                    if 'stream' in tokens[0]:
                        # This is surely a malformed PDF, with a stream inside the object.
                        self.logger.debug("Found a stream inside an object, before ending delimiter, >>. This is a malformed PDF");
                    raise DictParseException("expected CHAR_DELIMITER, found CHAR_REGULAR token; value: %s" % tokens[0][1], dictionary)


            elif state == 2:
                # STATE 2: looking for values...
                # a dictionary's values can be any direct object (including dictionaries) as well as references to indirect objects
                #  string, numeric, boolean, dictionary, array, indirectobjref, but not a stream
                # This doesn't seem to be well defined, but for now, it seems a stream cannot be a value; they usually come after
                # the dictionary in an indirect object.

                if tokens[0][1].startswith('#'):
                    # We need to hex_decode this
                    # ex : in 126939c66f62baaa0784d4e7f5b4d973,  #6eull for null.
                    tokens[0] = (tokens[0][0], hex_decode(tokens[0][1]))

                if tokens[0][0] == CHAR_WHITESPACE:
                    pass

                elif tokens[0][1][0] == '%':
                    # @kbandla
                    # This is a trick used by some exploit kits.
                    # Bascially, everything after a % till the end of a line is a comment. Lets do that
                    # But we still want to stay in the same state, becuase we are stil looking for a value
                    tokens.pop(0)

                # check for nested dictionary
                elif self.isOpenDictionary(tokens[0]):
                    # We _can_ have a dictionary as a value, so recursively descent into new dictionary, and store it as the value
                    self.logger.debug("%s\033[42;34;1m %s \033[0;42;34m refers to a dict... \033[0m" % (indent*' ', key))
                    value = self.parseDictionary(tokens, indent+5)
                    self.logger.debug("%s  [value] found dict" % (indent*' '))
                    state = 3

                # check for closure of this array -- interesting scenario
                # I believe this means whatever key we have at the moment has a null value, and therefore, according to the spec,
                # we act as if the key does not exist in the dict.
                elif self.isCloseDictionary(tokens[0]):
                    # explicitly setting key's value to null and returning
                    dictionary[key] = None
                    self.logger.debug("%s{} done" % (indent*' '))
                    return dictionary

                # check for array
                elif self.isOpenArray(tokens[0]):
                    self.logger.debug("%s\033[42;35;1m %s \033[0;42;35m refers to an array... \033[0m" % (indent*' ', key))
                    value = self.parseArray(tokens, indent+5)
                    self.logger.debug("%s  [value] found array" % (indent*' '))
                    state = 3

                # check for name object
                elif tokens[0][1][0] == '/':
                    name = self.parseName(tokens[0])
                    value = name
                    self.logger.debug("%s  [value] found name: %s" % ((indent*' '), value))
                    state = 3

                # check for indirect object reference
                elif self.parseIndObjRef(tokens, peek=True) != None:
                    value = self.parseIndObjRef(tokens, peek=False)
                    self.logger.debug("%s  [value] found ind obj ref: %s" % ((indent*' '), value))
                    state = 3

                # check for string object
                elif tokens[0][1][0] == '(' or tokens[0][1][0] == '<':
                    # @kbandla
                    # have seen some strange cases here. Typically not finding the closing ) when parsing the string.
                    # TODO: To fix this, we lookahead into the tokens and pass only those which will make the string
                    value = self.parseString(tokens)
                    self.logger.debug("%s  [value] found string: %s" % ((indent*' '), value[:50]))
                    state = 3

                # check for boolean object
                elif self.parseBoolean(tokens[0]) != None:
                    value = self.parseBoolean(tokens[0])
                    self.logger.debug("%s  [value] found boolean: %s" % ((indent*' '), value))
                    state = 3

                # check for numeric object
                elif self.parseNumeric(tokens[0]) != None:
                    value = self.parseNumeric(tokens[0])
                    self.logger.debug("%s  [value] found numeric: %s" % ((indent*' '), value))
                    state = 3

                # check for null object
                elif self.parseNull(tokens[0]):
                    value = None
                    self.logger.debug("%s  [value] found null" % (indent*' '))
                    state = 3

                else:
                    # Some exploits, like 034c1aa7c84529a01b847cf08c8d51ed have a really long key
                    if len(key) > 1000:
                        self.logger.debug(' Very long key found. This is likely an exploit. (CVE unknown)')
                    # @kbandla: Examples that breaks this parser:
                    # 034c1aa7c84529a01b847cf08c8d51ed
                    # 126939c66f62baaa0784d4e7f5b4d973
                    raise DictParseException("Could not parse token while searching for value: %s" % str(tokens[0]), dictionary)

            elif state == 3:
                # STATE 3: store key-value pair


                # validate the key
                if key is None:
                    self.logger.error("we're in state 3 but key is None!")
                    raise DictParseException('Key is None', dictionary)

                # there's no point in validating the value--it can be None, legitimately

                dictionary[key] = value
                self.logger.debug("%s\033[32;1m%s\033[0;1m => \033[0;32m%s\033[0m" % (indent*' ', key, str(value)))

                # reset the state to 1, because we expect to find another key or the end of the dict
                state = 1
                key = ''
                value = None

            ###  end if-else blocks  ###

            # Moving on to the next token if we're not in state 3
            if state != 3:
                tokens.pop(0)



    def parseArray(self, tokens, indent):
        state = 0 # start
        value = None
        array = []


        while tokens != []:
            self.logger.debug("%s\033[46m  State:\033[2m%d\033[0;46m Token: \033[1m%d\033[0;46m, \033[31m%s  \033[0m" % (indent*' ', state, tokens[0][0], tokens[0][1][:30]))

            if state == 0:
                if self.isOpenArray(tokens[0]):
                    state = 1
                else:
                    return None

            elif state == 1:
                if tokens[0][0] == CHAR_WHITESPACE:
                    pass

                # check for nested dictionary
                elif self.isOpenDictionary(tokens[0]):
                    # We _can_ have a dictionary as a value, so recursively descent into new dictionary, and store it as the value
                    #self.logger.debug("%s\033[42;34;1m %s \033[0;42;34m refers to a dict... \033[0m" % (indent*' ', key))
                    value = self.parseDictionary(tokens, indent+5)
                    self.logger.debug("%s  [value] found dict" % (indent*' '))
                    state = 3

                # check for array
                elif self.isOpenArray(tokens[0]):
                    # @kbandla : key not found sometimes. #TODO
                    #self.logger.debug("%s\033[42;35;1m %s \033[0;42;35m refers to an array... \033[0m" % (indent*' ', key))
                    value = self.parseArray(tokens, indent+5)
                    self.logger.debug("%s  [value] found array" % (indent*' '))
                    state = 3

                # check for the closure of array
                elif self.isCloseArray(tokens[0]):
                    self.logger.debug("%s[] done" % (indent*' '))
                    #tokens.pop(0)
                    return array

                # check for name object
                elif tokens[0][1][0] == '/':
                    name = self.parseName(tokens[0])
                    if name:
                        value = name
                        self.logger.debug("%s  [value] found name: %s" % ((indent*' '), value))
                        state = 3

                # check for indirect object reference
                elif self.parseIndObjRef(tokens, peek=True) != None:
                    value = self.parseIndObjRef(tokens, peek=False)
                    self.logger.debug("%s  [value] found ind obj ref: %s" % ((indent*' '), value))
                    state = 3

                # check for string object
                elif tokens[0][1][0] == '(' or tokens[0][1][0] == '<':
                    value = self.parseString(tokens)
                    self.logger.debug("%s  [value] found string: %s" % ((indent*' '), value[:50]))
                    state = 3

                # check for boolean object
                elif self.parseBoolean(tokens[0]) != None:
                    value = self.parseBoolean(tokens[0])
                    self.logger.debug("%s  [value] found boolean: %s" % ((indent*' '), value))
                    state = 3

                # check for numeric object
                elif self.parseNumeric(tokens[0]) != None:
                    value = self.parseNumeric(tokens[0])
                    self.logger.debug("%s  [value] found numeric: %s" % ((indent*' '), value))
                    state = 3

                # check for null object
                elif self.parseNull(tokens[0]):
                    value = None
                    self.logger.debug("%s  [value] found null" % (indent*' '))
                    state = 3

                else:
                    # 01f839645d6123fe586fc5f17ee8017d
                    raise ArrayParseException("Could not parse token while searching for value: %s" % str(tokens[0]), array)

            elif state == 3:
                # STATE 3: store values in array
                self.logger.debug("%s\033[32;1mstoring value\033[0m '%s'" % ((indent*' '), str(value)))
                array.append( value )
                state = 1


            ###  end if-else block  ###
            if state != 3:
                tokens.pop(0)
