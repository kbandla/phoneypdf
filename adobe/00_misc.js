//////////////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 Misc objects

 Kiran Bandla <kbandla@intovoid.com>
 */

Pages = {}

this.mailto = function(){
    var args = [];
    for ( i in arguments)
        args.push(arguments[i]);
    args.pop();
    //log_event('CVE-2007-5020');
    log_event('mailto', args);
}
