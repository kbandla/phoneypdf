//////////////////////////////////////////////////////////////////////////
/*
 phoneyPDF
 Collab Object
 Kiran Bandla <kbandla@intovoid.com>
 */

var Collab = {};

Collab.AlertWithHelpWidth = 508; // number
Collab.addedAnnotCount = 0; // number
Collab.buttonRowMarginHeight = 11; // number
Collab.buttonRowMarginWidth = 11; // number
Collab.defaultStore = 'NONE'; // string
Collab.docID = '3thGgdtqRf1MJuCEBinNqC'; // string
Collab.hasSynchonizer = true; // boolean
Collab.initiatorEmail = undefined; // undefined
Collab.isDocCtrInitAvailable = true; // boolean
Collab.isOutlook = false; // boolean
Collab.marginHeight = 20; // number
Collab.marginWidth = 20; // number
Collab.modifiedAnnotCount = 0; // number
Collab.navIconHeight = 12; // number
Collab.navIconWidth = 12; // number
Collab.privateAnnotsAllowed = false; // boolean
Collab.showAnnotToolsWhenNoCollab = false; // boolean
Collab.showBasicAuditTrail = false; // boolean
Collab.tipIconHeight = 32; // number
Collab.tipIconWidth = 32; // number
Collab.wizardHeight = 428; // number
Collab.wizardMarginWidth = 25; // number
Collab.wizardWidth = 575; // number

function_list = ['init','sync','animateSyncButton','takeOwnershipOfComments','addAnnotStore','createAnnotStore','newWrStreamToCosObj','stream2CosObj','cosObj2Stream','URL2PathFragment','hashString','getStoreSettings','setStoreSettings','getStoreFSBased','setStoreFSBased','getStoreNoSettings','setStoreNoSettings','documentToStream','streamToDocument','addStateModel','removeStateModel','getStateModels','registerReview','unregisterReview','setReviewRespondedDate','registerProxy','getProxy','canProxy','createUniqueDocID','alertWithHelp','registerApproval','unregisterApproval','makeAllCommentsReadOnly','removeApprovalDocScript','beginInitiatorMailOperation','endInitiatorMailOperation','isOnlineReview','isOfflineReview','isEmailReview','isApprovalWorkflow','isSharedReview','getReviewFolder','setReviewFolder','setReviewFolderForMultipleReviews','addReviewFolder','removeReviewFolder','getReviewFolders','unregisterOffline','browseForNetworkFolder','browseForFolder','convertMappedDrivePathToSMBURL','mountSMBURL','uriEncode','uriNormalize','uriConvertReviewSource','uriToDIPath','uriCreateFolder','uriDeleteFolder','uriPutData','uriEnumerateFiles','uriDeleteFile','isPathWritable','stringToUTF8','launchHelpViewer','swConnect','swSendVerifyEmail','swAcceptTOU','swRemoveWorkflow','getCCaddr','hasInitiatorEmailRequest','finalApprovalEmailEnabled','enableFinalApprovalEmail','isUbiquitized','getIdentity','goBackOnline','bringToFront','getFdfUrl','updateMountInfo','addReviewServer','setDefaultReviewServer','getAlwaysUseServer','setAlwaysUseServer','unsetAlwaysUseServer','setERTCWelcomeInvisible','unsetERTCWelcomeInvisible','getCustomEmailMessage','setCustomEmailMessage','getReviewInfo','returnToInitiator','convertDIPathToPlatformPath','convertPlatformPathToDIPath','getAggregateReviewInfo','getNumberOfReviewsOnServer','removeMultipleSelectedReviewsInTracker','expandTrackerSelection','collapseTrackerSelection','hasReviewCommentRepositoryIntact','hasReviewDeadline','getReviewState','getReviewError','isDocCenterURL','getServiceURL','saveTrackerHTML','dumpTrackerHTML','getSelectedNodeHierarchy','allReviewServers','docCenterLogin','shareFileBezel','dcSignup','shareFile','getDateAndTime','getDefaultDateAndTime','AVUMLogEventWrapper','AVUMStartPayloadWrapper','AVUMEndPayloadWrapper','AVUMAddStringToPayloadWrapper','AFPrepareFormForDistribution','AFCheckSubmitButtonStatus','GetActiveDocIW','getDocCenterReviewServer','getEmailDistributionReviewServer','isDocDirty','isFirstLaunch','unsetFirstLaunch','takeOwnershipAndPublishComments','getFullyQualifiedHostname','getProgressInfo','getUserIDFromStore','addDocToDocsOpenedByWizard','removeDocsOpenedByWizard','isDocReadOnly','invite','collectEmailInfo','getIcon'];

handleObjectHooks(Collab, function_list, 'Collab');
