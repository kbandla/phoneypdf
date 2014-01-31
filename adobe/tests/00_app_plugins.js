log('Found '+app.numPlugIns+' plugins');
var plugIns = app.plugIns;
var viewerVersion = parseInt(app.viewerVersion.toString().charAt(0));
log('Found app.viewerVersion = '+ viewerVersion);
for (var i = 0; i < plugIns.length; i++) {
    log(plugIns[i]);
    try{
        if (plugIns[i].name == 'Forms') {
            var formVersion = plugIns[i].version;
        }
    }
    catch(e){
        log('TEST FAILED!'+e);
    }
}
if (((viewerVersion == 8) && (formVersion < 8.21)) || ((viewerVersion == 9) && (formVersion < 9.31))) {
    log('SUCCESS, TEST PASSED');
} else {
    log('TEST FAILED');
}
