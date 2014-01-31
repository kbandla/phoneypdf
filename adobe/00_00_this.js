//////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
'this' object

 Kiran Bandla <kbandla@intovoid.com>
 */

var temp_this = this;
function_list = ['print']

//////// Specific function handlers
//handleObjectHooks(this, function_list , 'this');

this.print = function(){
    var args = [];
    for ( i in arguments ){
        if (typeof(arguments[i]) == 'string'){
            args.push(arguments[i]);
        }
        else if(typeof(arguments[i]) == 'object'){
            for (ii in arguments[i]){
                if(typeof(arguments[i][ii]) == 'string'){
                    args.push(arguments[i][ii]);
                }
            }
        }
        args.push(arguments[i]);
    }
    args.pop();
    log_event('this.print', args);
}

this.loadXML = function(){
    console.log('this.loadXML CALLED!!!');
}
