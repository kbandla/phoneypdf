//////////////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 Debugging Utils
 Kiran Bandla <kbandla@intovoid.com>
 */

var jsdbg = {};

jsdbg.unescape  =   this.unescape;
jsdbg.unescape_count = 0;
jsdbg.unescape_last =   null;
jsdbg.unescape_threshold_lower = this.UNESCAPE_THRESHOLD;
jsdbg.unescape_threshold_upper= 1500;
jsdbg.unescape_results = new Array();
jsdbg.debug    =   true;   

jsdbg.tokens = ['var'];
jsdbg.log   =   new Array();

// Hook unescape to detect heap-sprays
this.unescape = function(){
    // keep track of how many times unescape is called. Starts from zero.
    jsdbg.unescape_count += 1;
    increment_feature('c_unescape_calls')
    increment_feature('l_unescape_param', arguments[0].length)
    //console.warn('unescape '+arguments[0].length);
    //if ( arguments[0].length > jsdbg.unescape_threshold_lower && arguments[0].length < jsdbg.unescape_threshold_upper){
    if ( arguments[0].length > this.UNESCAPE_THRESHOLD){
        msg = 'Really long unescape parameter ('+arguments[0].length+' bytes). Potential heapspray';
        increment_feature('c_unescape_long_params')
        jsdbg.log.push(msg);
        //console.warn(msg);
    }
    var result = jsdbg.unescape(arguments[0]);
    //console.test_shellcode ( result );
    jsdbg.unescape_last = result;
    return result;
}

// a python-style dir method to display some object info
jsdbg.dir = function(obj){
    if (typeof(obj) == 'string'){
        console.log(obj + ' //string');
        return;
    }
    for(i in obj){
        switch(typeof(obj[i])){
            case "string":
                //console.log(i +'='+ obj[i] + ' //string' );
                console.log(i + ' //string' );
                break;
            case "object":
                console.log(i + ' //object');
                break;
            case "number":
                console.log(i + ' //number');
                break;
            case "function":
                console.log(i + ' //function');
                break;
            default:
                //nothing
        }
    }
}
