'''
provides a logging facility
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

import logging
import sys

class SpecificLevelsFilter(logging.Filter):
    def __init__(self, lvl):
        self.level = lvl
    def filter(self, record):
        return record.levelno <= self.level


def buildLogger():
    # This handler only applies to DEBUG and INFO levels and outputs to console in a way that doesn't interfere
    # with the msg formatting.
    debugInfoHandler = logging.StreamHandler( sys.stdout )
    debugInfoHandler.setLevel(logging.DEBUG)
    debugInfoHandler.addFilter( SpecificLevelsFilter(logging.INFO) )
    debugInfoHandler.setFormatter( logging.Formatter("%(message)s [%(funcName)s()]") )

    # This handler applies to WARNING, CRITICAL and ERROR levels, and shows a lot of detail.
    noteworthyHandler = logging.StreamHandler( sys.stdout )
    noteworthyHandler.setLevel(logging.WARNING)
    noteworthyHandler.setFormatter( logging.Formatter("[%(levelname)s %(filename)s:%(funcName)s:%(lineno)d] %(message)s") )

    # Adding these two handlers to the pcaphandler logger instance.
    lggr = logging.getLogger('phoneyPDF')
    lggr.addHandler( debugInfoHandler )
    lggr.addHandler( noteworthyHandler )

    return lggr
