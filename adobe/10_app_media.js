/////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 app.media Object

 Kiran Bandla <kbandla@intovoid.com>
 */

app.media = {};


// A lot the following properties are Enumerated objects.
// We need to add full support for this.

// app.media.align = [object Object]; // object
// app.media.canResize = [object Object]; // object
// app.media.closeReason = [object Object]; // object
// app.media.ifOffScreen = [object Object]; // object
// app.media.layout = [object Object]; // object
// app.media.monitorType = [object Object]; // object
// app.media.openCode = [object Object]; // object
// app.media.over = [object Object]; // object
// app.media.pageEventNames = [object Object]; // object
// app.media.priv = [object AppMediaPriv]; // object
// app.media.raiseCode = [object Object]; // object
// app.media.raiseSystem = [object Object]; // object
// app.media.renditionType = [object Object]; // object
// app.media.status = [object Object]; // object
// app.media.windowType = [object Object]; // object
app.media.defaultVisible = true; // boolean
app.media.trace = false; // boolean
app.media.version = 7; // number

// Properties
app.media.meet =  1;
app.media.slice =  2;
app.media.fill =  3;
app.media.scroll =  4;
app.media.hidden =  5;
app.media.standard =  6;
app.media.docked =  1;
app.media.floating =  2;
app.media.fullScreen =  3;
app.media.document =  1;
app.media.nonDocument =  2;
app.media.primary =  3;
app.media.bestColor =  4;
app.media.largest =  5;
app.media.tallest =  6;
app.media.widest =  7;
app.media.topLeft =  1;
app.media.topCenter =  2;
app.media.topRight =  3;
app.media.centerLeft =  4;
app.media.center =  5;
app.media.centerRight =  6;
app.media.bottomLeft =  7;
app.media.bottomCenter =  8;
app.media.bottomRight =  9;
app.media.no =  1;
app.media.keepRatio =  2;
app.media.yes =  3;
app.media.pageWindow =  1;
app.media.appWindow =  2;
app.media.desktop =  3;
app.media.monitor =  4;
app.media.allow =  1;
app.media.forceOnScreen =  2;
app.media.cancel =  3;
app.media.unknown =  0;
app.media.media =  1;
app.media.selector =  2;
app.media.clear =  1;
app.media.message =  2;
app.media.contacting =  3;
app.media.buffering =  4;
app.media.init =  5;
app.media.seeking =  6;
app.media.general =  1;
app.media.error =  2;
app.media.done =  3;
app.media.stop =  4;
app.media.play =  5;
app.media.uiGeneral =  6;
app.media.uiScreen =  7;
app.media.uiEdit =  8;
app.media.docClose =  9;
app.media.docSave =  10;
app.media.docChange =  11;
app.media.success =  0;
app.media.failGeneral =  1;
app.media.failSecurityWindow =  2;
app.media.failPlayerMixed =  3;
app.media.failPlayerSecurityPrompt =  4;
app.media.failPlayerNotFound =  5;
app.media.failPlayerMimeType =  6;
app.media.failPlayerSecurity =  7;
app.media.failPlayerData =  8;
app.media.fileError =  10;
app.media.fileNotFound =  17;
app.media.fileOpenFailed =  18;
app.media.Open =  true;
app.media.Close =  true;
app.media.InView =  true;
app.media.OutView =  true;
app.media.defaultVisible = true; // boolean
app.media.trace = false; // boolean
app.media.version = 7; // number

function_list = ['createPlayer','openPlayer','startPlayer','Events','Markers','Players','MediaPlayer','canPlayOrAlert','getRenditionSettings','getFirstRendition','getURLSettings','getAltTextSettings','addStockEvents','removeStockEvents','computeFloatWinRect','getPlayerStockEvents','getPlayerTraceEvents','getAnnotStockEvents','getAnnotTraceEvents','argsDWIM','alert','Alerter',]

///////// Specific Funcitons
app.media.alert = app.alert;

///////// Generic funciton handlers

for ( temp in function_list){
    if (!app.media.hasOwnProperty(function_list[temp])){
        app.media[function_list[temp]] = new Function("var args = [];  for ( i in arguments) args.push(arguments[i]); args.pop(); log_event('app.media.'+'"+function_list[temp]+"', args);");
    }
}
