# About
phoneyPDF is a tool to help analyze PDF files, and maybe a starting place to 
identify malicious PDF files from. It uses a javascript engine to execute javascript 
from PDF files, and exposes Adobe Reader-esque objects and a DOM so that if the 
javascript tries to interact with the DOM or certain Reader-only objects, 
they'll be there, and execution can occur.

This tool was written by Trevor Tonn and Kiran Bandla over a few months at Verisign iDefense. 
With Verisign Inc permission, we are releasing this tool to the public to use and extend.

# Installation
Requires Python 2.6.x - 2.7.x

phoneyPDF has a few dependencies:
* V8: Google's javascript interpreter
* pyv8: python connector to v8 so you can execute javascript from within your Python scripts
* lxml: a well known XML parser

## PyV8
Building PyV8 is not going to be easy. If you have an option to install a 
pre-compiled version, go for it. 

On Jan23, 2014 bugs were finally fixed in PyV8 r572. 

The following version are confirmed to work:
* V8 -r18896
* PyV8 -r573

### OSX
You can install PyV8 from [here](https://github.com/brokenseal/PyV8-OS-X).
```bash
pip install -e git://github.com/brokenseal/PyV8-OS-X#egg=pyv8
```

## lxml
The easiest way to install lxml is using pip:
```bash
pip install lxml
```
On Linux, you can use apt-get or yum to install it.
You could also build from source. It might be a little work on some platforms (osx)

## LICENSE
See the LICENSE file
