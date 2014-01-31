import re
from constants import *

def CopyWithoutWhiteSpace(content):
    result = []
    for token in content:
        if token[0] != CHAR_WHITESPACE:
            result.append(token)
    return result

def Obj2Str(content):
    return ''.join(map(lambda x: repr(x[1])[1:-1], CopyWithoutWhiteSpace(content)))

def IsNumeric(str):
    return re.match('^[0-9]+', str)


def TrimLWhiteSpace(data):
    while data[0][0] == CHAR_WHITESPACE:
        data = data[1:]
    return data

def TrimRWhiteSpace(data):
    while data[-1][0] == CHAR_WHITESPACE:
        data = data[:-1]
    return data

def FormatOutput(data, raw):
    if raw:
        if type(data) == type([]):
            return ''.join(map(lambda x: x[1], data))
        else:
            return data
    else:
        return repr(data)

def Canonicalize(sIn):
    if sIn == "":
        return sIn
    elif sIn[0] != '/':
        return sIn
    elif sIn.find('#') == -1:
        return sIn
    else:
        i = 0
        iLen = len(sIn)
        sCanonical = ''
        while i < iLen:
            if sIn[i] == '#' and i < iLen - 2:
                try:
                    sCanonical += chr(int(sIn[i+1:i+3], 16))
                    i += 2
                except:
                    sCanonical += sIn[i]
            else:
                sCanonical += sIn[i]
            i += 1
        return sCanonical

def EqualCanonical(s1, s2):
    return Canonicalize(s1) == s2

def ConditionalCanonicalize(sIn, nocanonicalizedoutput):
    if nocanonicalizedoutput:
        return sIn
    else:
        return Canonicalize(sIn)

## Following utils are marked for deletion in the next major update

def PrintObject(object, options):
    print 'obj %d %d' % (object.id, object.version)
    print ' Type: %s' % ConditionalCanonicalize(object.GetType(), options.nocanonicalizedoutput)
    print ' Referencing: %s' % ', '.join(map(lambda x: '%s %s %s' % x, object.GetReferences()))
    stream = object.ContainsStream()
    oPDFParseDictionary = None
    if stream:
        print ' Contains stream'
        print ' %s' % FormatOutput(stream, options.raw)
        oPDFParseDictionary = cPDFParseDictionary(stream, options.nocanonicalizedoutput)
    else:
        print ' %s' % FormatOutput(object.content, options.raw)
        oPDFParseDictionary = cPDFParseDictionary(object.content, options.nocanonicalizedoutput)
    print
    oPDFParseDictionary.PrettyPrint(' ')
    print
    if options.filter and not options.dump:
        filtered = object.Stream()
        if filtered == []:
            print ' %s' % FormatOutput(object.content, options.raw)
        else:
            print ' %s' % FormatOutput(filtered, options.raw)
    if options.dump:
        print 'Start dump:'
        print object.Stream(False)
        print 'End dump'
    print
    return
