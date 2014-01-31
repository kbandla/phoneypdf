

def extractMetaFeatures(pdf, featureCollection):
    # These are meta-features derived from other features collected during the interpretation/execution

    # clobber all the features together
    if F_L_JS_SCRIPTS_LENGTH_TOTAL in self.__features:
        self.__features[F_S_PERCENTAGE_SCRIPT] = (float(self.__features[F_L_JS_SCRIPTS_LENGTH_TOTAL]) / float(self.__features[F_L_PDF_LENGTH])) * 100

    if F_C_JS_UNESCAPE_CALLS in self.__features:
        if (self.__features[F_C_JS_UNESCAPE_CALLS] > 1):  # and ( self.__features[F_L_JS_UNESCAPE_LENGTH] > self.javascript_global.UNESCAPE_THRESHOLD ):
            event = Events('Suspicious', [self.__features[F_C_JS_UNESCAPE_CALLS], self.__features[F_L_JS_UNESCAPE_LENGTH]])
            self.javascript_global.hookObjects.append(event)
