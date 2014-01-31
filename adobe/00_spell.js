////////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 spell Object

 Kiran Bandla <kbandla@intovoid.com>
 */

var spell = {};

spell.dictionaryNames = ['English (Canada)','English (United Kingdom)','English (United States)']; // object
spell.dictionaryOrder = ['English (United States)']; // object
spell.domainNames = ['All comments and form fields','Comment','In Comments...','Form Field','In Form Fields...']; // object
spell.ignoredWords = null; // object
spell.languageOrder = ['en_US']; // object
spell.languages = ['en_CA','en_GB','en_US']; // object
spell.available = true; // boolean

function_list = ['check','checkText','checkWord','customDictionaryCreate','customDictionaryDelete','customDictionaryOpen','customDictionaryClose','customDictionaryExport','addDictionary','removeDictionary','addWord','removeWord','ignoreAll','userWords',]

//////// Specific functions
spell.customDictionaryOpen = function(){
    log_event('CVE-2009-1493');
};


/////// Generic Funciton handlers
for (temp in function_list){
    if(!spell.hasOwnProperty(function_list[temp])){
        spell[function_list[temp]] = new Function("var args = [];  for ( i in arguments) args.push(arguments[i]); args.pop(); log_event('spell.'+'"+function_list[temp]+"', args);");
    }
}
