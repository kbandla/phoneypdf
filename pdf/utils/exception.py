# kiran bandla <kbandla@verisign.com>
# Exception classes for various Parsing issues

class PDFException(Exception):
    """
    Base PDF Exception class for everything.
    """
    def __init__(self, msg):
        self.msg = msg
    
    def __str__(self):
        return '%s : %s '%(self.__class__.__name__, self.msg)

    def __repr__(self):
        return self.__str__()

class ParserException(PDFException):
    pass

class MalformedPDFException(PDFException):
    pass

class DictParseException(ParserException):
    """
    Exception parsing a PDF Dictionary Object
    """
    def __init__(self, msg, dictionary):
        super(self.__class__, self).__init__(msg)
        self.dictionary = dictionary

class ArrayParseException(ParserException):
    """
    Exception parsing a PDF Array Object
    """
    def __init__(self, msg, array):
        super(self.__class__, self).__init__(msg)
        self.array = array

class StringParseException(ParserException):
    """
    Exception parsing a PDF Array Object
    """
    def __init__(self, msg, string):
        super(self.__class__, self).__init__(msg)
        self.string = string


class DecompressException(PDFException):
    """
    Exception decompressing a stream Object
    """
    def __init__(self, filter, msg='Decompress failed' ):
        super(self.__class__, self).__init__(msg)
        self.filter = filter

