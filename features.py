'''
PDF Feature extraction for Machine Learning
This file is part of the phoneyPDF Framework

Various features in PDF Format, used in ML
Legend:
 P_ : Presence
 F_ : Feature
 S_ : Stats
 C_ : Count
 L_ : Length / Size

Trevor Tonn <smthmlk@gmail.com>
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
import types

class NoSuchFeature(Exception):
    pass

def validateFeatureName(name):
    if type(name) not in types.StringTypes:
        raise Exception("Feature names must be strings; found %s instead" % type(name))
    if name is "":
        raise Exception("The empty string \"\" is not a valid feature name")
    return name.upper()

def featureSanity(func):
    """
    This decorator does a bunch of sanity checks on the feature, stuff that's done
    in several methods and so is worth factoring out.

    Checks performed:
        - is the feature name a string type?
        - is it the empty string?
        - does the feature exist? (it should)
    """
    def featureNameSanity(*args, **kwargs):
        # Sanity check first
        name = validateFeatureName(args[1])

        # Replace with uppercase version
        newArgsL = list(args)
        newArgsL[1] = name
        newArgsT = tuple(newArgsL)

        # Feature exists?
        if newArgsT[1] not in newArgsT[0].featuresD:
            raise NoSuchFeature("no feature: %s" % repr(newArgsT))

        return func(*newArgsT, **kwargs)

    return featureNameSanity


class FeatureCollection(object):
    """
    This class allows a simple, self-contained way of collecting various features during the parsing
    and execution of a PDF file. It keeps its own state outside of the PDF Interpreter instance, has
    its own methods for manipulating its internal data structures, and is supposed to work seamlessly
    with the PdfFeatureAnalyzer framework.
    """

    def __init__(self, logger):
        self.logger = logger

        # this dict is where all our features are stored, along with their values
        # the keys are the class variables defined above, while
        self.featuresD = {}
        self.registerCommonFeatures()

    def registerFeature(self, featureName):
        """
        Registers a new feature. If a feature by this name already exists, this call returns
        without modifying anything.

        This method must be called to register any features you want to use/track during the
        course of PDF execution or afterwards when analyzing the DOM, objects, etc.
        """
        featureName = validateFeatureName(featureName)
        self.logger.info("feature: %s" % featureName)
        if featureName in self.featuresD:
            self.logger.warn("feature %s already exists; ignoring" % repr(featureName))
            return

        # we may have features with different types; may have to make this slightly more complex
        # in that case
        self.featuresD[featureName] = 0

    def registerCommonFeatures(self):
        """
        This method registers features that we know we want to always collect.
        """
        # JavaScript related Features
        for featureName in ("F_JS_SUSPICIOUS_HEAPSPRAY", "F_JS_RAWVALUE"):
            self.registerFeature(featureName)

        # PDF related Features
        for featureName in ("F_PDF_OPENACTION", "F_PDF_RENDITION", "F_L_PDF_LENGTH"):
            self.registerFeature(featureName)

        # Statistical Features
        for featureName in ("F_C_JS_SCRIPTS_EXECUTION_FAILED", "F_C_JS_SCRIPTS_FOUND", "F_C_JS_SCRIPTS_EXECUTED", "F_L_JS_SCRIPTS_LENGTH_TOTAL", "F_S_PERCENTAGE_SCRIPT"):
            self.registerFeature(featureName)

        # JavaScript Execution Features
        for featureName in ("c_unescape_calls", "c_unescape_long_params", "l_unescape_param"):
            self.registerFeature(featureName)

    @featureSanity
    def setFeatureValue(self, featureName, value):
        featureName = featureName.upper()
        if featureName not in self.featuresD:
            raise NoSuchFeature("no such feature %s" % repr(featureName))
        self.featuresD[featureName] = value

    @featureSanity
    def incFeatureValue(self, featureName, value=1):
        """
        For features which are numeric (int/floats) this method takes their existing value and
        increments it by some amount (1 by default)
        """
        if type(self.featuresD[featureName]) not in (int, float):
            raise Exception("Trying to increment value of a non-numeric feature (%s is %s)" % (featureName, type(self.featuresD[featureName])))
        self.featuresD[featureName] += value

    @featureSanity
    def getFeatureValue(self, featureName):
        if featureName not in self.featuresD:
            raise NoSuchFeature("no such feature: %s" % repr(featureName))
        return self.featuresD[featureName]


if __name__ == "__main__":
    import logging
    import sys

    logging.basicConfig(stream=sys.stdout, format="%(levelname)s %(funcName)s | %(message)s")
    logger = logging.getLogger('FeatureCollection')
    logger.setLevel(logging.DEBUG)

    fc = FeatureCollection(logger)
    fc.registerFeature("x")
    fc.incFeatureValue('x')
    fc.incFeatureValue('x', 10)
    print fc.getFeatureValue('x')
    fc.registerFeature(None)
