///////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 Doc Object

 Kiran Bandla <kbandla@intovoid.com>
 */

var Doc = {};
Doc.unescape = this.unescape;
// Object Properties
// Doc.scaleHow = [object Object]; // object
// Doc.scaleWhen = [object Object]; // object
// Doc.search = [object Search]; // object
// Doc.security = [object Security]; // object
// Doc.securityHandler = null; // object
// Doc.shareIdentity = [object ShareIdentity]; // object
Doc.sounds = null; // object
Doc.spell = spell // object
Doc.spellDictionaryOrder = null; // object
Doc.spellLanguageOrder = null; // object
// Doc.style = [object Object]; // object
// Doc.submitFormUsageRights = [object Object]; // object
Doc.templates = null; // object
// Doc.trans = [object Object]; // object
// Doc.tts = [object TTS]; // object
Doc.util = util; // object
// Doc.view = [object Dest]; // object
// Doc.viewState = [object ViewState]; // object
// Doc.zoomtype = [object Object]; // object    Page. 263 JS API Ref v8


// Build an Annotation class
Doc.Annotation = function Annotation(subject){
    this.subject = subject;
}
Doc.annotations = new Array();
Doc.Collab = this.Collab;

// Properties
Doc.nocache     =   undefined;  // boolean, default is undefined
Doc.ANFB_ShouldAppearInPanel = 3; // number
Doc.ANFB_ShouldCollaborate = 6; // number
Doc.ANFB_ShouldEdit = 2; // number
Doc.ANFB_ShouldExport = 5; // number
Doc.ANFB_ShouldNone = 7; // number
Doc.ANFB_ShouldPrint = 0; // number
Doc.ANFB_ShouldSummarize = 4; // number
Doc.ANFB_ShouldView = 1; // number
Doc.ANSB_Author = 3; // number
Doc.ANSB_ModDate = 4; // number
Doc.ANSB_None = 0; // number
Doc.ANSB_Page = 1; // number
Doc.ANSB_Seq = 2; // number
Doc.ANSB_Subject = 6; // number
Doc.ANSB_Type = 5; // number
Doc.CBCanDoApprovalWorkflowCheckExpr = '((function () {var bReader = app.viewerType.match(/Reader/);var bResult = app.viewerVersion >= 9 && (!bReader || requestPermission(permission.annot, permission.create) == permission.granted);if (bResult && external) {var err = bReader ? (AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_READER ? AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_READER : (new String("This document appears to be an email based workflow invitation. To participate in the workflow, you must save the document locally and open it in Adobe Reader."))) : (AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_ACROBAT ? AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_ACROBAT : (new String("This document appears to be an email based workflow invitation. To participate in the workflow, you must save the document locally and open it in Adobe Acrobat.")));app.alert({cMsg: err});return false;}return bResult;})())'; // string
Doc.CBCanDoEBRReviewWorkflowCheckExpr = '((function () {var bReader = app.viewerType.match(/Reader/);var bResult = app.viewerVersion >= 6 && !bReader || app.viewerVersion >= 7 && requestPermission(permission.annot, permission.create) == permission.granted;if (bResult && external) {var err = bReader ? (AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_READER ? AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_READER : (new String("This document appears to be an email based workflow invitation. To participate in the workflow, you must save the document locally and open it in Adobe Reader."))) : (AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_ACROBAT ? AnnotsString.IDS_EMAIL_WORKFLOW_IN_BROWSER_ERROR_ACROBAT : (new String("This document appears to be an email based workflow invitation. To participate in the workflow, you must save the document locally and open it in Adobe Acrobat.")));app.alert({cMsg: err});return false;}return bResult;})())'; // string
Doc.CBCanDoReviewWorkflowCheckExpr = '((function () {return app.viewerVersion >= 6 && !app.viewerType.match(/Reader/) || app.viewerVersion >= 7 && requestPermission(permission.annot, permission.create) == permission.granted;})())'; // string
Doc.CBCanDoWorkflowCheckExprAPR = '((function () {return (app.viewerVersion >= 7 && app.viewerType.match(/Reader/) != null) && requestPermission(permission.annot, permission.create) == permission.granted;})())'; // string
Doc.CBFDBPerDoc = 4; // number
Doc.CBFNiceDBName = 2; // number
Doc.CBFNiceTableName = 1; // number
Doc.IDS_AM = 'am'; // string
Doc.IDS_GREATER_THAN = 'Invalid value: must be greater than or equal to %s.'; // string
Doc.IDS_GT_AND_LT = 'Invalid value: must be greater than or equal to %s and less than or equal to %s.'; // string
Doc.IDS_INVALID_DATE = 'Invalid date/time: please ensure that the date/time exists. Field '; // string
Doc.IDS_INVALID_DATE2 = ' should match format '; // string
Doc.IDS_INVALID_MONTH = '** Invalid **'; // string
Doc.IDS_INVALID_VALUE = 'The value entered does not match the format of the field'; // string
Doc.IDS_LESS_THAN = 'Invalid value: must be less than or equal to %s.'; // string
Doc.IDS_MONTH_INFO = 'January[1]February[2]March[3]April[4]May[5]June[6]July[7]August[8]September[9]October[10]November[11]December[12]Sept[9]Jan[1]Feb[2]Mar[3]Apr[4]Jun[6]Jul[7]Aug[8]Sep[9]Oct[10]Nov[11]Dec[12]'; // string
Doc.IDS_PM = 'pm'; // string
Doc.IDS_STARTUP_CONSOLE_MSG = 'Acrobat EScript Built-in Functions Version 9.0'; // string
Doc.IPV4Type = 0; // number
Doc.IPV6Type = 1; // number
Doc.RT = undefined; // undefined
Doc.URL = 'file:////home/kbandla/work/pdf/pdfs/research/test.pdf'; // string
Doc.XFAForeground = false; // boolean
Doc.annotFilter = undefined; // undefined
Doc.author = ''; // string
Doc.baseURL = ''; // string
Doc.cTableEvenRowColor = '#F8F8F8'; // string
Doc.cTableHeaderColor = '#E4E4FF'; // string
Doc.cTableOddRowColor = '#FFFFFF'; // string
Doc.calculate = true; // boolean
Doc.certified = false; // boolean
Doc.closed = false; // boolean
Doc.creationDate = ''; // string
Doc.creator = ''; // string
Doc.deadlineDate = 'No deadline'; // string
Doc.delay = false; // boolean
Doc.dirty = true; // boolean
Doc.disclosed = false; // boolean
Doc.documentFileName = 'test.pdf'; // string
Doc.dynamicXFAForm = false; // boolean
Doc.external = false; // boolean
Doc.filesize = 6452; // number
Doc.hidden = false; // boolean
Doc.internalDeadlineDate = ''; // string
Doc.isInCollection = false; // boolean
Doc.isModal = false; // boolean
Doc.keywords = ''; // string
Doc.layout = 'OneColumn'; // string
Doc.metadata = '<x:xmpmeta xmlns:x="adobe:ns:meta/" x:xmptk="Adobe XMP Core 4.2.1-c043 52.372728, 2009/01/18-13:18:53        "> \
\
 <rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">  \
\
  <rdf:Description rdf:about=""/>\
\
 </rdf:RDF>\
\
</x:xmpmeta>\
\
'; // string
Doc.modDate = ''; // string
Doc.mouseX = 232; // number
Doc.mouseY = 682; // number
Doc.numFields = 0; // number
Doc.numIcons = 0; // number
Doc.numPages = 1; // number
Doc.numTemplates = 0; // number
Doc.pageNum = 0; // number
Doc.pane = 'N'; // string
Doc.path = '/home/kbandla/work/pdf/pdfs/research/test.pdf'; // string
Doc.permStatusReady = true; // boolean
Doc.producer = ''; // string
Doc.requiresFullSave = false; // boolean
Doc.selectedAnnots = undefined; // undefined
Doc.subject = ''; // string
Doc.title = ''; // string
Doc.wireframe = false; // boolean
Doc.zoom = 165; // number
Doc.zoomType = 'FitWidth'; // string





function_list = ['gotoNamedDest','print','getPrintParams','printWithParams','getPrintSepsParams','printSepsWithParams','scroll','mailDoc','getURL','deletePages','replacePages','insertPages','movePage','getPageBox','setPageBoxes','addThumbnails','removeThumbnails','addWeblinks','removeWeblinks','getPageLabel','setPageLabels','getPageTransition','setPageTransitions','getPageRotation','setPageRotations','getPageNthWord','getPageNumWords','selectPageNthWord','getPageNthWordQuads','closeDoc','bringToFront','saveAs','extractPages','requestPermission','newPage','setAction','addScript','removeScript','EnableForERTC','setPageAction','addWatermarkFromText','addWatermarkFromFile','addRequirement','removeRequirement','getColorConvertAction','colorConvertPage','embedOutputIntent','applyRedactions','disableWindows','enableWindows','getSound','deleteSound','importSound','getDataObject','removeDataObject','embedDocAsDataObject','importDataObject','exportDataObject','createDataObject','getDataObjectContents','setDataObjectContents','openDataObject','getIcon','importIcon','deleteIcon','createIcon','addIcon','getNthIconName','removeIcon','getOCGs','getOCGOrder','setOCGOrder','getAnnots3D','getAnnot3D','stampAPFromPage','syncAnnotScan','addAnnot','getAnnot','getAnnots','migrateAnnotsFrom','getAnnotRichMedia','getAnnotsRichMedia','flattenPages','getLegalWarnings','getSignatureStatus','getModifications','setUserPerms','encryptForRecipients','addRecipientListCryptFilter','encryptUsingPolicy','calculateNow','submitForm','resetForm','mailForm','exportAsFDF','exportAsXFDF','exportAsText','exportXFAData','importAnFDF','importAnXFDF','importXFAData','importTextData','getField','getNthFieldName','addNewField','addField','removeField','setPageTabOrder','getTemplate','createTemplate','removeTemplate','getNthTemplate','spawnPageFromTemplate','exportAsFDFStr','exportAsXFDFStr','exportAsTextStr','exportAsXFAStr','addLink','getLinks','removeLinks','alert','status','num_function_params','get_object_info','ADBCAnnotEnumerator','ADBCAnnotStore','AFBuildRegExps','AFDateFromYMD','AFDateHorizon','AFDate_Format','AFDate_FormatEx','AFDate_Keystroke','AFDate_KeystrokeEx','AFExactMatch','AFExtractNums','AFExtractRegExp','AFExtractTime','AFGetMonthIndex','AFGetMonthString','AFMakeArrayFromList','AFMakeNumber','AFMatchMonth','AFMergeChange','AFNumber_Format','AFNumber_Keystroke','AFParseDate','AFParseDateEx','AFParseDateOrder','AFParseDateWithPDF','AFParseDateYCount','AFParseTime','AFPercent_Format','AFPercent_Keystroke','AFRange_Validate','AFSignatureLock','AFSignature_Format','AFSimple','AFSimpleInit','AFSimple_Calculate','AFSpecial_Format','AFSpecial_Keystroke','AFSpecial_KeystrokeEx','AFStringReplace','AFTime_Format','AFTime_FormatEx','AFTime_Keystroke','ANApprovalGetStrings','ANAuthenticateResource','ANClipPrec3','ANContinueApproval','ANCreateMLSEElementsFromArray','ANCreateMLSElement','ANCreateSkipElements','ANCreateTipElements','ANDefaultInvite','ANDoSend','ANDocCenterLogin','ANDocCenterLoginForAddReviewers','ANDocCenterSignup','ANDumpObj','ANERTC','ANEndApproval','ANFancyAlertImpl','ANIdentityDialog','ANMatchString','ANMatchStringCaseInsensitive','ANNormalizeURL','ANPlatformPathToURL','ANRejectApproval','ANRunSharedReviewEmailStep','ANSMBURLToPlatformPath','ANSendApprovalToAuthorEnabled','ANSendCommentsToAuthor','ANSendCommentsToAuthorEnabled','ANSendForApproval','ANSendForBrowserReview','ANSendForFormDistribution','ANSendForFormDistributionEnabled','ANSendForReview','ANSendForReviewEnabled','ANSendForSharedReview','ANSendForSharedReviewEnabled','ANSendSharedFile','ANShareFile','ANShareFile2','ANStartApproval','ANTrustPropagateAll','ANValidateIdentity','ANVerifyComments','ANstateful','ANsumFlatten','ANsummAnnot','ANsummarize','CBAutoConfigCommentRepository','CBBBRInit','CBBBRInvite','CBCreateGettingStartedStepDescription','CBCreateInviteStepDescription','CBCreateInviteStepDescriptionApproval','CBCreateSendInvitationStepDescription','CBCreateStepNavElements','CBCreateUploadStepDescription','CBDeleteReplyChain','CBEncodeMaybeInternalStrings','CBEncodeURL','CBFormDistributionComplete','CBFormDistributionEmailComplete','CBFreezeFunc','CBGetReplyChain','CBIsValidEmail','CBPutReplyChain','CBRunApproveDialog','CBRunBBRReviewWizard','CBRunERTCWizard','CBRunEmailApprovalWizard','CBRunEmailReviewWizard','CBRunFormDistributionWizard','CBRunFormDistributionWizardEmail','CBRunReturnResponseDialog','CBRunReviewOptionsDialog','CBRunShareFileWizard','CBRunSharedReviewWizard','CBRunSimpleWiz','CBRunSimpleWizNew','CBSetProductVariant','CBShareFileComplete','CBSharedReviewCloseDialog','CBSharedReviewComplete','CBSharedReviewConfigureServerStepDescription','CBSharedReviewDistributeStepDescription','CBSharedReviewIfOfflineDialog','CBSharedReviewInviteReviewers','CBSharedReviewSecurityDialog','CBSharedReviewSelectServerTypeDescription','CBSharedReviewStatusDialog','CBStartWizStep','CBStartWizStepNew','CBStrToLongColumnThing','CBTrustPropagateWiz','CBannotData','CBannotSetData','CBconnect','CBcreateTable','CBdef','CBgetInfo','CBgetTableConnect','CBgetTableDesc','CBsetInfo','ColorConvert','ColorEqual','CreateViewerVersionCheck70','CreateViewerVersionCheckCase','CreateViewerVersionCheckString','CreateViewerVersionCheckStringsCluster','DebugAlert','DebugPrintln','DebugThrow','DistributionServerStepCommitWork','DoIdentityDialog','DynamicAnnotStore','GetStepNum','IWBrowseAnyDoc','IWBrowseDoc','IWBrowseDocStepCommitWork','IWDistributeStepDescription','IWDistributionServer','IWERTCWelcome','IWEmailStepDescription','IWIdentityDialog','IWNewInternalServer','IWSaveProfileStepDescription','IWShareFileConfirmDialog','IWSharedReviewDocCenterCreateConfirm','IWSharedReviewDocCenterCreateID','IWSharedReviewDocCenterLogin','IWSharedReviewDocCenterServicesDialog','IWShowFileError','IWShowFolderError','IWShowLocalFolderError','IWShowSharepointWorkspace','IWSubmitButton','IWUploadFileError_UniqueFilenameDialog','IWUploadFileFailedDialog','InitializeFormsTrackerJS','InitializeMultimediaJS','LoginForGuardian','LookUpWordDefinitionURL','LookUpWordEnable','Matrix2D','RefreshPoliciesForGuardian','RemoveWebdav','SPSearchForServices','SharedString','SilentDocCenterLogin','SplitAddrs','TestHSShare','TestRemoveWorkflow','WDAnnotEnumerator','WDmungeURL','binsert','debugExcept','eMailValidate','encryptUsingPolicyForJSObject','filterAddrs','getFS','getFolderNameRemovedPath','getFormsString','getnextnumber','hasHanko','indexOfNextEssential','isAlphaNumeric','isAlphabetic','isNumber','isReservedMaskChar','isValidSaveLocationAtDocCtr','isort','maskSatisfied','myReviewTrackerDebugAlert','populateFilesAtDocCenter','setDateAndTime']

//////// Specific functions
Doc.getAnnots = function(){
    // returns a list of Annotation objects or null
    // This is used in exploits
    //temp = new Array();
    //temp.push( new Annotation());
    //temp.push( new Annotation());
    if (arguments[0] && arguments[0].hasOwnProperty('nPage')){
        pageNumber = arguments[0]['nPage'];
        return Pages[pageNumber].annotations;
    }
    else{
        Pages[0].annotations;
        return Pages[0].annotations;
    }
}
/*
Doc.printSeps = function(){
    log_event('CVE-2010-4091');
}

Doc.getAnnots = function(){
    log_event('CVE-2009-1492');
}
*/
//////// Generic handlers
/*
for( temp in function_list){
    if(!Doc.hasOwnProperty(function_list[temp])){
        Doc[function_list[temp]] = new Function("var args = [];  for ( i in arguments) args.push(arguments[i]); args.pop(); log_event('app.doc.'+'"+function_list[temp]+"', args);");
        };
}
*/

// Initialize app.doc
app.doc = Doc;
handleObjectHooks(app.doc, function_list, 'app.doc');
this.syncAnnotScan = app.doc.syncAnnotScan;
this.getAnnots = app.doc.getAnnots;

// END of Doc object
///////////////////////////////////////////////////////////////////////
