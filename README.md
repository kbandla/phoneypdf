About
=====

phoneyPDF is a tool to help analyze PDF files, and maybe a starting place to identify malicious PDF files from. It uses a javascript engine
to execute javascript from PDF files, and exposes Adobe Reader-esque objects and a DOM so that if the javascript tries to interact with the
DOM or certain Reader-only objects, they'll be there, and execution can occur.

This tool was written by Trevor Tonn and Kiran Bandla over a year or so at Verisign iDefense. With Verisign Inc permission, we are releasing
this tool to the public to use and extend.

Installation
============

Requires Python 2.6.x - 2.7.x

phoneyPDF has a few dependencies: Google's V8 javascript engine, pyv8, and lxml. We'll go over how to install each of those
 - *V8*: Google's javascript interpreter
 - *pyv8*: python connector to v8 so you can execute javascript from within your Python scripts
 - *lxml*: a well known XML parser

OSX
---

```bash
# brokenseal / Martin Loewis pyv8+v8 distribution for OSX 10.6.4+:
#   https://github.com/brokenseal/PyV8-OS-X
pip install -e git://github.com/brokenseal/PyV8-OS-X#egg=pyv8

# install lxml in a similar way
pip install lxml
```

GNU/Linux
---------

TODO


Tutorial
========

From within the phoneypdf directory, you can interpret/analyze a PDF file by providing its path:

```bash
python main.py ~/importantFile.pdf
```

And it will do its thing. More to come on what this actually does and how to interpret what it spits out...


## LICENSE
See the LICENSE file
