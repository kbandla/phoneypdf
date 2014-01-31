/////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 app Object

 Kiran Bandla <kbandla@intovoid.com>
 */

// app Object
//  depends :   FullScreen
//  depends :   AppMedia
//  depends :   Thermometer
//  depends :   Monitors
//

var app  = {};
app.name = 'app';
app.unescape = this.unescape;

// app.activeDocs = ; // object
// app.capabilities = [object capabilities]; // object
// app.constants = [object constants]; // object
app.fs = FullScreen; // object
app.fsColor = ['RGB',0,0,0]; // object
// app.media = [object AppMedia]; // object
// app.monitors = [object Object]; // object
app.runtimeHighlightColor = ['RGB',0.8000030517578125,0.8431396484375,1]; // object
app.thermometer = Thermometer; // object
app.addressBookAvailable = false; // boolean
app.calculate = true; // boolean
app.focusRect = true; // boolean
app.formsVersion = 9.5; // number
app.fsClick = true; // boolean
app.fsCursor = 2; // number
app.fsEscape = true; // boolean
app.fsLoop = false; // boolean
app.fsTimeDelay = 5; // number
app.fsTransition = ''; // string
app.fsUsePageTiming = true; // boolean
app.fsUseTimer = false; // boolean
app.fullscreen = false; // boolean
app.ignoreNextDoc = undefined; // undefined
app.ignoreXFA = undefined; // undefined
app.language = 'ENU'; // string
app.numplugIns = 20; // number
app.openInPlace = true; // boolean
app.platform = 'WIN'; // string
app.printColorProfiles = undefined; // undefined
app.printerNames = undefined; // undefined
app.runtimeHighlight = true; // boolean
app.toolbar = true; // boolean
app.toolbarHorizontal = true; // boolean
app.toolbarVertical = true; // boolean
app.viewerType = 'Reader'; // string
app.viewerVariation = 'Reader'; // string
//app.viewerVersion = 9.407; // number
app.viewerVersion = 9.207; // number
app.viewerVersion = 8.10; // number


/////////////////
// extracted from objects
// These need to be pointed to proper objects, instead of definitions here
app.useTimer =  false;// boolean
app.usePageTiming =  true;// boolean
app.loop =  false;// boolean
app.escapeExits =  true;// boolean
app.clickAdvances =  true;// boolean
app.isFullScreen =  false;// boolean
app.defaultTransition = '' ;// string
app.timeDelay =  5;// number
app.backgroundColor =  ['RGB',0,0,0];// object
app.cursor =  2;// number
app.duration =  0;// number
app.value =  0;// number
app.text =  undefined;// undefined
app.cancelled =  false;// boolean

////////////////////////////
// Reader Plugin interface
function plugIn (name, filename){
    this.name = name;
    this.version = 9.29;
    this.path = "/C/Program Files/Adobe Reader 9.0/Reader/plug_ins/" +filename;
    this.loaded = true;
    this.certified = false;
    this.toString = function(){return this.path;}
    this.valueOf = function(){return this.path;}
}

// Add plugins to app
app.plugIns= new Array();
app.plugIns.push(new plugIn('Accessibility','Accessibility.api'));
app.plugIns.push(new plugIn('Forms','AcroForm.api'));
app.plugIns.push(new plugIn('Annots','Annots.api'));
app.plugIns.push(new plugIn('Checkers','Checkers.api'));
app.plugIns.push(new plugIn('DIGSIG','DigSig.api'));
app.plugIns.push(new plugIn('ADBE:DictionaryValidationAgent','DVA.api'));
app.plugIns.push(new plugIn('eBook','eBook.api'));
app.plugIns.push(new plugIn('EScript','EScript.api'));
app.plugIns.push(new plugIn('EWH','EWH32.api'));
app.plugIns.push(new plugIn('AcroHLS','HLS.api'));
app.plugIns.push(new plugIn('InetAxes','IA32.api'));
app.plugIns.push(new plugIn('SVG','ImageViewer.api'));
app.plugIns.push(new plugIn('Make Accessible','MakeAccessible.api'));
app.plugIns.push(new plugIn('Multimedia','Multimedia.api'));
app.plugIns.push(new plugIn('PDDom','PDDom.api'));
app.plugIns.push(new plugIn('ppklite','PPKLite.api'));
app.plugIns.push(new plugIn('ReadOutLoud','ReadOutLoad.api'));
app.plugIns.push(new plugIn('Reflow','reflow.api'));
app.plugIns.push(new plugIn('SaveAsRTF','SaveAsRTF.api'));
app.plugIns.push(new plugIn('ADBE_Search','Search.api'));
app.plugIns.push(new plugIn('ADBE_Search5','Search5.api'));
app.plugIns.push(new plugIn('SendMail','SendMail.api'));
app.plugIns.push(new plugIn('Spelling','Spelling.api'));
app.plugIns.push(new plugIn('Updater','Updater.api'));
app.plugIns.push(new plugIn('WebLink','weblink.api'));
app.numplugIns = app.plugIns.length // number

//// Extracted functions from Reader
function_list= ['alert','beep','response','goBack','goForward','popUpMenu','popUpMenuEx','execMenuItem','hideMenuItem','hideToolbarButton','addMenuItem','addSubMenu','listMenuItems','listToolbarButtons','browseForDoc','browseForMultipleDocs','mailMsg','mailMsgWithAttachment','getResolvedAddresses','mailGetAddrs','newDoc','openDoc','setTimeOut','clearTimeOut','setInterval','clearInterval','getString','getPath','setProfile','trustedFunction','trustPropagatorFunction','beginPriv','endPriv','launchURL','isValidSaveLocation','getNthplugInName','openFDF','newFDF','loadPolicyFile','compareDocuments','DisablePermEnforcement','EnablePermEnforcement','addToolButton','removeToolButton','execDialog','measureDialog','newCollection','Monitors']

///////// Specific handlers
app.alert = function () {
    var args = [];
    for( i in arguments)
        args.push(arguments[i]);
    args.pop();
    log_event('app.alert', args);
};

app.Monitors = function () {
    this.length = 0;
};

app.setTimeOut = this.setTimeOut
///////// Generic handlers for native functions
for ( temp in function_list){
    if(!app.hasOwnProperty(function_list[temp])){
        app[function_list[temp]] = new Function("var args = [];  for ( i in arguments) args.push(arguments[i]); args.pop(); log_event('app.'+'"+function_list[temp]+"', args);");
    }
} 

// END of app Object
////////////////////////////////////////////////////////////////////////////////////
