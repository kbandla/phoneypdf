/////////////////////////////////////////////////////////////////////////////////////////////////////
//
//START AppMedia 
var AppMedia = {};

//////// Functions ///////////
AppMedia.createPlayer = function (args) {
    try {
        return app.media.priv.createPlayer(app.media.argsDWIM(args));
    } catch (e) {
        app.media.alert("Exception", args, {error: e});
        return null;
    }
};
AppMedia.openPlayer = function (args) {
    var player = null;
    try {
        args = app.media.argsDWIM(args);
        player = app.media.createPlayer(args);
        if (player) {
            var result = player.open();
            if (result.code != app.media.openCode.success) {
                player = null;
                app.media.alert("Open", args, {code: result.code});
            } else if (player.visible) {
                player.setFocus();
            }
        }
    } catch (e) {
        player = null;
        app.media.alert("Exception", args, {error: e});
    }
    return player;
};
AppMedia.startPlayer = function (args) {
    try {
        args = app.media.argsDWIM(args);
        var player = args.annot && args.annot.player;
        if (player && player.isOpen) {
            player.play();
        } else {
            player = app.media.openPlayer(args);
        }
        return player;
    } catch (e) {
        app.media.alert("Exception", args, {error: e});
        return null;
    }
};
AppMedia.Events = function () {
    this.listeners = {};
    this.dispatching = 0;
    this.removed = {};
    this.privAddRemove(arguments, this.privAdd);
};
AppMedia.Markers = function (player) {
    this.player = player;
};
AppMedia.Players = function () {
    this.length = 0;
};
AppMedia.MediaPlayer = function () {
};
AppMedia.canPlayOrAlert = function (args) {
    var canPlay = args.doc.media.canPlay;
    if (canPlay.yes) {
        return true;
    }
    app.media.alert("CannotPlay", args, {canPlay: canPlay});
    return false;
};
AppMedia.getRenditionSettings = function (args) {
    var settings;
    var selection = args.rendition.select(true);
    if (selection.rendition) {
        try {
            settings = selection.rendition.getPlaySettings(true);
            settings.players = selection.players;
            app.media.priv.copyProps(args.settings, settings);
            return settings;
        } catch (e) {
            if (e.name != "RaiseError") {
                throw e;
            }
            if (e.raiseSystem != app.media.raiseSystem.fileError) {
                throw e;
            }
            if (e.raiseCode != app.media.raiseCode.fileNotFound &&
                e.raiseCode != app.media.raiseCode.fileOpenFailed) {
                throw e;
            }
            app.media.alert("FileNotFound", args, {fileName: selection.rendition.fileName});
        }
    } else {
        app.media.alert("SelectFailed", args, {selection: selection});
    }
    return app.media.getAltTextSettings(args, selection);
};
AppMedia.getFirstRendition = function (list) {
    for (var i = 0; i < list.length; i++) {
        if (list[i].rendition.type == app.media.renditionType.media) {
            return list[i].rendition;
        }
    }
    return null;
};
AppMedia.getURLSettings = function (args) {
    var settings = {data: app.media.getURLData(args.URL, args.mimeType)};
    app.media.priv.copyProps(args.settings, settings);
    return settings;
};
AppMedia.getAltTextSettings = function (args, selection) {
    if (!args.showAltText) {
        return null;
    }
    var rendition = selection.rendition ||
        app.media.getFirstRendition(selection.rejects);
    if (!rendition) {
        return null;
    }
    settings = rendition.getPlaySettings(false);
    app.media.priv.copyProps(args.settings, settings);
    if (!settings.windowType) {
        settings.windowType = app.media.priv.computeDefaultWindowType(args, settings);
    }
    if (settings.windowType != app.media.windowType.docked) {
        return null;
    }
    var text = rendition.altText;
    if (text.length == 0) {
        if (!args.showEmptyAltText) {
            return null;
        }
        text = app.media.priv.getString("IDS_ERROR_NO_ALT_TEXT_SPECIFIED");
    }
    settings.data = app.media.getAltTextData(text);
    settings.players = [app.media.priv.altTextPlayerID];
    return settings;
};
AppMedia.addStockEvents = function (player, annot) {
    if (player.stockEvents) {
        return;
    }
    app.media.priv.AddStockEventsHelper(player, app.media.getPlayerStockEvents(player.settings));
    if (annot) {
        player.annot = annot;
    }
};
AppMedia.removeStockEvents = function (player) {
    if (!player || !player.stockEvents) {
        return;
    }

    function removeProps(object) {
        if (object.events) {
            object.events.remove(object.stockEvents);
            delete object.stockEvents;
        }
    }

    removeProps(player);
    if (player.annot) {
        if (player.annot.stockEvents) {
            removeProps(player.annot);
        }
        delete player.annot.player;
        delete player.annot;
    }
};
AppMedia.computeFloatWinRect = function (doc, floating, whichMonitor, uiSize) {
    var overRect;
    switch (floating.over) {
      case app.media.over.pageWindow:
        overRect = doc.pageWindowRect;
        break;
      case app.media.over.appWindow:
        overRect = doc.innerAppWindowRect;
        break;
      case app.media.over.desktop:
        overRect = app.monitors.desktop()[0].rect;
        break;
      case app.media.over.monitor:
      default:
        overRect = app.monitors.select(whichMonitor, doc)[0].workRect;
        break;
    }
    var border = app.media.getWindowBorderSize(floating);
    rect = app.media.priv.rectAlign(overRect, floating.align, floating.width + border[0] + border[2], floating.height + border[1] + border[3]);
    if (uiSize) {
        rect = app.media.priv.rectGrow(rect, uiSize);
    }
    return rect;
};
AppMedia.getPlayerStockEvents = function (settings) {
    var events = new (app.media.Events);
    if (app.media.trace) {
        events.add(app.media.getPlayerTraceEvents());
    }
    events.add({onClose: function (e) {var annot = e.target.annot;app.media.removeStockEvents(e.target);if (annot) {annot.extFocusRect = null;if (e.media.hadFocus && e.target.settings.windowType == app.media.windowType.docked && e.media.doc.media.canPlay.yes) {annot.setFocus(true);}}}, afterDone: function (e) {e.target.close(app.media.closeReason.done);}, afterError: function (e) {app.media.alert("PlayerError", e.target.args, {errorText: e.media.text});e.target.close(app.media.closeReason.error);}, afterEscape: function (e) {e.target.close(app.media.closeReason.uiScreen);}});
    switch (settings.windowType) {
      case app.media.windowType.docked:
        events.add({onGetRect: function (e) {if (e.target.annot) {e.target.annot.extFocusRect = e.media.rect = app.media.priv.rectGrow(e.target.annot.innerDeviceRect, e.target.uiSize);}}, onBlur: function (e) {if (e.target.annot) {e.target.annot.alwaysShowFocus = false;}}, onFocus: function (e) {if (e.target.annot) {e.target.annot.alwaysShowFocus = true;}}});
        break;
      case app.media.windowType.floating:
        if (!settings.floating.rect &&
            (!settings.floating.width || !settings.floating.height)) {
            app.media.priv.throwBadArgs();
        }
        if (settings.visible === undefined) {
            settings.visible = app.media.defaultVisible;
        }
        if (settings.visible) {
            settings.visible = false;
            events.add({afterReady: function (e) {var floating = e.target.settings.floating;var rect = floating.rect;if (!rect) {rect = app.media.computeFloatWinRect(e.media.doc, floating, e.target.settings.monitorType, e.target.uiSize);} else {rect = app.media.priv.rectGrow(rect, e.target.uiSize);}if (floating.ifOffScreen == app.media.ifOffScreen.forceOnScreen) {rect = app.media.constrainRectToScreen(rect, app.media.priv.rectAnchorPt(rect, floating.align));}e.target.outerRect = rect;e.target.visible = true;e.target.setFocus();}});
        }
        break;
      default:;
    }
    return events;
};
AppMedia.getPlayerTraceEvents = function () {
    return new (app.media.Events)({onEveryEvent: function (e) {if (e.media.id != "GetRect") {app.media.priv.trace("player event: on" + e.media.id);}}, afterEveryEvent: function (e) {app.media.priv.trace("player event: after" + e.media.id);}, onScript: function (e) {app.media.priv.trace("player onScript('" + e.media.command + "','" + e.media.param + "')");}, afterScript: function (e) {app.media.priv.trace("player afterScript('" + e.media.command + "','" + e.media.param + "')");}, onStatus: function (e) {app.media.priv.trace("player onStatus: " + (e.media.progress >= 0 ? e.media.progress + "/" + e.media.total + ", " : "") + "  status code: " + e.media.code + ": '" + e.media.text + "'");}, afterStatus: function (e) {app.media.priv.trace("player afterStatus: " + (e.media.progress >= 0 ? e.media.progress + "/" + e.media.total + ", " : "") + "  status code: " + e.media.code + ": '" + e.media.text + "'");}});
};
AppMedia.getAnnotStockEvents = function (windowType) {
    var events = new (app.media.Events);
    if (app.media.trace) {
        events.add(app.media.getAnnotTraceEvents());
    }
    events.add({onDestroy: function (e) {if (e.target.player) {e.target.player.close(app.media.closeReason.docChange);}}});
    if (windowType == app.media.windowType.docked) {
        events.add({onFocus: function (e) {if (e.target.player.isOpen) {e.target.player.setFocus();}e.stopDispatch = true;}, onBlur: function (e) {e.stopDispatch = true;}});
    }
    return events;
};
AppMedia.getAnnotTraceEvents = function () {
    return new (app.media.Events)({onEveryEvent: function (e) {app.media.priv.trace("annot event: on" + e.media.id);}, afterEveryEvent: function (e) {app.media.priv.trace("annot event: after" + e.media.id);}});
};
AppMedia.argsDWIM = function (args) {
    if (args && args.privDWIM) {
        return args;
    }
    args = app.media.priv.copyProps(args);
    args.privDWIM = true;
    if (event && event.action) {
        if (!args.annot) {
            args.annot = event.action.annot;
        }
        if (!args.rendition) {
            args.rendition = event.action.rendition;
        }
    }
    if (!args.doc) {
        if (args.rendition && args.annot) {
            if (args.rendition.doc != args.annot.doc) {
                app.media.priv.throwBadArgs();
            }
        }
        if (args.rendition) {
            args.doc = args.rendition.doc;
        } else if (args.annot) {
            args.doc = args.annot.doc;
        }
    }
    if (args.fromUser === undefined) {
        args.fromUser = !!(event && event.name && !app.media.pageEventNames[event.name]);
    }
    if (args.showAltText === undefined) {
        args.showAltText = true;
    }
    if (args.showEmptyAltText === undefined) {
        args.showEmptyAltText = !args.fromUser;
    }
    return args;
};
AppMedia.alert = function (type) {
    var a = {};
    for (var i = 1; i < arguments.length; i++) {
        app.media.priv.copyProps(arguments[i], a);
    }
    a.type = type;
    if (!("stockAlerter" in a.doc.media)) {
        a.doc.media.stockAlerter = new (app.media.Alerter);
    }
    dispatch(a.alerter) ||
        dispatch(a.doc.media.alerter) || dispatch(a.doc.media.stockAlerter);

    function dispatch(alerter) {
        if (alerter === undefined) {
            return false;
        }
        return alerter == null ||
            typeof alerter != "object" ||
            typeof alerter.dispatch != "function" ||
            alerter.dispatch(a) !== false;
    }

};
AppMedia.Alerter = function () {
    this.skip = false;
};


/////////// Objects ///////////

AppMedia.postEvent =  function (event) {
    var doc = event.media.doc;
    var p = doc.media.priv;
    var q = p.queue;
    if (!q) {
        q = p.queue = {};
    }
    if (!q.list) {
        q.list = [];
    }
    q.list.push(event);
    if (!q.timer) {
        q.timer = app.setTimeOut("app.media.priv.dispatchPostedEvents(this);", 1, false);
        q.timer.media = {doc: doc};
    }
};
AppMedia.dispatchPostedEvents =  function (doc) {
    try {
        if (doc.closed) {
            return;
        }
        var q = doc.media.priv.queue;
        var list = q.list;
        delete q.list;
        delete q.timer;
        if (list && list.length) {
            for (var i = 0; i < list.length; i++) {
                if (doc.closed) {
                    return;
                }
                var e = list[i];
                if (e.media.events) {
                    e.media.events.privDispatchNow("after", e);
                }
            }
        }
    } catch (e) {
        app.media.priv.trace("dpe throw: " + e.message);
    }
};
AppMedia.AddStockEventsHelper =  function (object, events) {
    object.stockEvents = events;
    if (!object.events) {
        object.events = new (app.media.Events);
    }
    object.events.add(events);
};
AppMedia.createPlayer =  function (args) {
    app.media.priv.trace("app.media.priv.createPlayer");
    if (!args.doc) {
        app.media.priv.throwBadArgs();
    }
    if (!app.media.canPlayOrAlert(args)) {
        return null;
    }
    if (args.annot && args.annot.player) {
        args.annot.player.close(app.media.closeReason.play);
    }
    var player = args.doc.media.newPlayer({args: args});
    player.settings = args.URL ? app.media.getURLSettings(args) : args.rendition ? app.media.getRenditionSettings(args) : app.media.priv.throwBadArgs();
    if (!player.settings) {
        return null;
    }
    if (!player.settings.windowType) {
        player.settings.windowType = app.media.priv.computeDefaultWindowType(args, player.settings);
    }
    if (!player.settings.windowType) {
        app.media.priv.throwBadArgs();
    }
    switch (player.settings.windowType) {
      case app.media.windowType.docked:
        if (player.settings.page === undefined) {
            if (!args.annot) {
                app.media.priv.throwBadArgs();
            }
            player.settings.page = args.annot.page;
        }
        break;
      case app.media.windowType.fullScreen:
        player.settings.monitor = app.monitors.select(player.settings.monitorType, args.doc);
        break;
      default:;
    }
    if (!args.noStockEvents) {
        app.media.addStockEvents(player, args.annot);
    }
    if (args.events) {
        if (!player.events) {
            player.events = new (app.media.Events);
        }
        player.events.add(args.events);
    }
    return player;
};
AppMedia.computeDefaultWindowType =  function (args, settings) {
    var retWT;
    if (args.annot) {
        retWT = app.media.windowType.docked;
    } else if (settings.floating) {
        retWT = app.media.windowType.floating;
    }
    return retWT;
};
//AppMedia.docMediaProto =  [object Object];
AppMedia.dumpObject =  function (obj, str, bValues) {
    if (!str) {
        str = "";
    } else {
        str += " ";
    }
    str += "(" + obj + ") [" + typeof obj + "]\n";
    for (var prop in obj) {
        str += "   " + prop + (bValues ? ": " + obj[prop] : "") + "\n";
    }
    app.media.priv.trace(str);
};
AppMedia.dumpNames =  function (obj, str) {
    app.media.priv.dumpObject(obj, str, false);
};
AppMedia.dumpValues =  function (obj, str) {
    app.media.priv.dumpObject(obj, str, true);
};
AppMedia.dumpArray =  function (array, str) {
    if (!str) {
        str = "";
    } else {
        str += " ";
    }
    str += "(" + array + ") [" + typeof array + "]\n{ ";
    for (var i = 0; i < array.length; i++) {
        str += array[i] + (i < array.length - 1 ? ", " : " }");
    }
    app.media.priv.trace(str);
};
AppMedia.trace =  function (str) {
    if (app.media.trace) {
        console.println(str);
    }
};
AppMedia.stopAnnotPlayer =  function () {
    try {
        annot = event.action.annot;
        if (annot.player) {
            annot.player.close(app.media.closeReason.stop);
        }
    } catch (e) {
        app.alert(e.message);
    }
};
AppMedia.pauseAnnotPlayer =  function () {
    try {
        annot = event.action.annot;
        if (annot.player) {
            annot.player.pause();
        }
    } catch (e) {
        app.alert(e.message);
    }
};
AppMedia.resumeAnnotPlayer =  function () {
    try {
        annot = event.action.annot;
        if (annot.player) {
            annot.player.play();
        }
    } catch (e) {
        app.alert(e.message);
    }
};
AppMedia.copyProps =  function (from, to) {
    if (!to) {
        to = {};
    }
    if (from) {
        for (var name in from) {
            to[name] = from[name];
        }
    }
    return to;
};
AppMedia.xPosTable =  0.5,0,0.5,1,0,0.5,1,0,0.5,1;
AppMedia.yPosTable =  0.5,0,0,0,0.5,0.5,0.5,1,1,1;
AppMedia.rectAlign =  function (rect, align, width, height) {
    if (!align) {
        align = app.media.align.center;
    }
    var x = rect[0] + (rect[2] - rect[0] - width) * app.media.priv.xPosTable[align];
    var y = rect[1] + (rect[3] - rect[1] - height) * app.media.priv.yPosTable[align];
    return [x, y, x + width, y + height];
};
AppMedia.rectAnchorPt =  function (rect, align) {
    if (!align) {
        align = app.media.align.center;
    }
    var x = rect[0] + (rect[2] - rect[0]) * app.media.priv.xPosTable[align];
    var y = rect[1] + (rect[3] - rect[1]) * app.media.priv.yPosTable[align];
    return [x, y];
};
AppMedia.rectArea =  function (rect) {
    if (app.media.priv.rectIsEmpty(rect)) {
        return 0;
    } else {
        return (rect[2] - rect[0]) * (rect[3] - rect[1]);
    }
};
AppMedia.rectGrow =  function (rect, size) {
    return [rect[0] - size[0], rect[1] - size[1], rect[2] + size[2], rect[3] + size[3]];
};
AppMedia.rectIntersect =  function (rectA, rectB) {
    var newRect;
    if (app.media.priv.rectIsEmpty(rectA) ||
        app.media.priv.rectIsEmpty(rectB)) {
        newRect = [0, 0, 0, 0];
    } else {
        newRect = [Math.max(rectA[0], rectB[0]), Math.max(rectA[1], rectB[1]), Math.min(rectA[2], rectB[2]), Math.min(rectA[3], rectB[3])];
        if (app.media.priv.rectIsEmpty(newRect)) {
            newRect = [0, 0, 0, 0];
        }
    }
    return newRect;
};
AppMedia.rectIntersectArea =  function (rectA, rectB) {
    return app.media.priv.rectArea(app.media.priv.rectIntersect(rectA, rectB));
};
AppMedia.rectIsEmpty =  function (rect) {
    return !rect || rect[0] >= rect[2] || rect[1] >= rect[3];
};
AppMedia.rectCopy =  function (rect) {
    return [rect[0], rect[1], rect[2], rect[3]];
};
AppMedia.rectUnion =  function (rectA, rectB) {
    return app.media.priv.rectIsEmpty(rectA) ? app.media.priv.rectCopy(rectB) : app.media.priv.rectIsEmpty(rectB) ? app.media.priv.rectCopy(rectA) : [Math.min(rectA[0], rectB[0]), Math.min(rectA[1], rectB[1]), Math.max(rectA[2], rectB[2]), Math.max(rectA[3], rectB[3])];
};
AppMedia.getString =  function (idString) {
    return app.getString("Multimedia", idString);
};
AppMedia.valueOr =  function (value, def) {
    return value !== undefined ? value : def;
};
//AppMedia.altTextPlayerID =  vnd.adobe.swname:ADBE_AltText;
AppMedia.meet =  1;
AppMedia.slice =  2;
AppMedia.fill =  3;
AppMedia.scroll =  4;
AppMedia.hidden =  5;
AppMedia.standard =  6;
AppMedia.docked =  1;
AppMedia.floating =  2;
AppMedia.fullScreen =  3;
AppMedia.document =  1;
AppMedia.nonDocument =  2;
AppMedia.primary =  3;
AppMedia.bestColor =  4;
AppMedia.largest =  5;
AppMedia.tallest =  6;
AppMedia.widest =  7;
AppMedia.topLeft =  1;
AppMedia.topCenter =  2;
AppMedia.topRight =  3;
AppMedia.centerLeft =  4;
AppMedia.center =  5;
AppMedia.centerRight =  6;
AppMedia.bottomLeft =  7;
AppMedia.bottomCenter =  8;
AppMedia.bottomRight =  9;
AppMedia.no =  1;
AppMedia.keepRatio =  2;
AppMedia.yes =  3;
AppMedia.pageWindow =  1;
AppMedia.appWindow =  2;
AppMedia.desktop =  3;
AppMedia.monitor =  4;
AppMedia.allow =  1;
AppMedia.forceOnScreen =  2;
AppMedia.cancel =  3;
AppMedia.unknown =  0;
AppMedia.media =  1;
AppMedia.selector =  2;
AppMedia.clear =  1;
AppMedia.message =  2;
AppMedia.contacting =  3;
AppMedia.buffering =  4;
AppMedia.init =  5;
AppMedia.seeking =  6;
AppMedia.general =  1;
AppMedia.error =  2;
AppMedia.done =  3;
AppMedia.stop =  4;
AppMedia.play =  5;
AppMedia.uiGeneral =  6;
AppMedia.uiScreen =  7;
AppMedia.uiEdit =  8;
AppMedia.docClose =  9;
AppMedia.docSave =  10;
AppMedia.docChange =  11;
AppMedia.success =  0;
AppMedia.failGeneral =  1;
AppMedia.failSecurityWindow =  2;
AppMedia.failPlayerMixed =  3;
AppMedia.failPlayerSecurityPrompt =  4;
AppMedia.failPlayerNotFound =  5;
AppMedia.failPlayerMimeType =  6;
AppMedia.failPlayerSecurity =  7;
AppMedia.failPlayerData =  8;
AppMedia.fileError =  10;
AppMedia.fileNotFound =  17;
AppMedia.fileOpenFailed =  18;
AppMedia.Open =  true;
AppMedia.Close =  true;
AppMedia.InView =  true;
AppMedia.OutView =  true;


AppMedia.defaultVisible = true; // boolean
AppMedia.trace = false; // boolean
AppMedia.version = 7; // number

//END AppMedia
//
/////////////////////////////////////////////////////////////////////////////////////////////////////
