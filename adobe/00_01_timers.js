//////////////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 Timeout hooks
 Kiran Bandla <kbandla@intovoid.com>
 */

this.setTimeout =   function( code, timeout){
    console.log(code);
    this.eval(code);
}

this.setInterval    =   function( code, timeout){
    console.log(code);
    this.eval(code);
}

this.clearTimeout   = function( timeoutID ){
    if (timeoutID != undefined)
        console.log(timeoutID);
}

//
this.setTimeOut =   this.setTimeout
this.clearTimeOut   =   this.clearTimeout
