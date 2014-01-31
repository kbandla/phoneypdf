////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 JS Console Object
 Partial implementation of Firefox Console API
 http://getfirebug.com/wiki/index.php/Console_API

 Kiran Bandla <kbandla@intovoid.com>
 */


write_log   =   this.write_log;

var console = {};

console.log     =   function( message ){
    write_log( 'DEBUG', message );
}

console.warn    =   function( message ){
    write_log( 'WARN' , message );
}

console.info=   function( message ){
    write_log( 'INFO' , message );
}

console.error=   function( message ){
    write_log( 'ERROR' , message );
}

console.shellcode = function( message ){
    write_hex( message );
}

console.test_shellcode = function( message ){
    test_shellcode( message );
}

// coverage for Adobe JS stuff
console.show    =   function(){
    //
}
console.println     =   console.log;
// END console object
////////////////////////////////////////////////////////////////////
// Analyze field data
analyzeFieldValue = this.analyzeData;
