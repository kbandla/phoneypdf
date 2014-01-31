///////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 util Object

 Kiran Bandla <kbandla@intovoid.com>
 */

var util = {};

function_list = ['printf','printx','scand','charToByte','byteToChar','fixOldString','stringFromStream','streamFromString','iconStreamFromIcon','readFileIntoStream','crackURL','xmlToSpans','spansToXML','printd',]

///////// Specific handlers for known functions
/*
util.printf = function(){
    log_event('CVE-2008-2992');
};
*/

///////// Generic function handles for the rest of the functions    ///////
/*
for ( temp in function_list ){
    if(!util.hasOwnProperty(function_list[temp])){
        util[function_list[temp]] = new Function("var args = [];  for ( i in arguments) args.push(arguments[i]); args.pop();  log_event('util.'+'"+function_list[temp]+"', args);");
    }
}
*/
handleObjectHooks(util, function_list, 'util');
