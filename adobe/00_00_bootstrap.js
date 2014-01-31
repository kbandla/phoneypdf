//////////////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 DOM Bootstrap : Create Necessary Adobe DOM
 Kiran Bandla <kbandla@intovoid.com>
 */

//
// Hack #1 : Add eval to the Object prototype. Required. See WMI
var DEBUG = true;
Object.prototype.eval = this.eval;
//
// Hack #2 : Patch behavior in V8/SMv1.8 to return -1 for indexOf called on 
// an undefined object
// reference JS snippet : ba73323e7d7a094cfdfe4420de0eb750
/*
var _indexOf = String.prototype.indexOf;
String.prototype.indexOf = function (){
    // If indexOf is called on an undefined object, return -1
    // thus mimicing SM 1.7
    console.log('indexof argument = '+ arguments[0]);
    console.log('indexof caller type  ='+ typeof(arguments.caller));
    if (typeof(arguments.caller) == "undefined"){
        if (DEBUG)
            console.log('indexOf() called on undefined! Returning -1');
        return -1;
    }
    else {
        return _indexOf( arguments );
    }
}

// Hack #3 : Patch behavior in V8/SM to return -1 for substr called on 
// an undefined object
// reference JS snippet : 75e61776e81d591453371760da16bf1c
// reference PCAP taskid : 16913576
var _substr =   String.prototype.substr;
String.prototype.substr =   function(){
    if (typeof(arguments.caller) == 'undefined'){
        if(DEBUG){
            console.log('substr() called on undefined! Returning -1');
        }
        return _substr( arguments );
        return -1;
    }
    else{
        return _substr ( arguments );
    }
}
*/
// Generic function handler for an object.
function handleObjectHookss(jsObject, function_list, object_name){
    for(function_name in function_list){
        if( !jsObject.hasOwnProperty( function_list[function_name] )){
            // We do not have an existing handler for this function. 
            // Lets handle it dynamically
            jsObject[function_list[function_name]] = new Function(" ");
        }
        else{
            //console.log(object_name[function_list[function_name]]);
        }
    }
}

function handleObjectHooks(jsObject, function_list, object_name){
    for(function_name in function_list){
        if( !jsObject.hasOwnProperty( function_list[function_name] )){
            // We do not have an existing handler for this function. 
            // Lets handle it dynamically
            jsObject[function_list[function_name]] = new Function("         \
                    var args = [];                                 \
                    for ( i in arguments ) {                                \
                        if ( typeof(arguments[i]) == 'string'){             \
                            args.push(arguments[i]);                        \
                        }                                                   \
                        else if (typeof(arguments[i]) == 'object') {        \
                            for ( ii in arguments[i]){                      \
                                if(typeof(arguments[i][ii]) != 'function'){  \
                                        args.push(arguments[i][ii]);        \
                                    }                                       \
                            }                                               \
                        }                                                   \
                    }                                                       \
                log_event('"+object_name+"'+'.'+'"+function_list[function_name]+"', args); "); 
        }//if
    }//for
}//function
