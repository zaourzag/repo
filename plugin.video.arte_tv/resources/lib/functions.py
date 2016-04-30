
def translate(tid):
    import xbmcaddon
    return xbmcaddon.Addon(id = 'plugin.video.arte_tv').getLocalizedString(tid).encode('utf-8')
    
def parameters_string_to_dict(parameters):
    paramDict = {}
    if parameters:
        paramPairs = parameters[1:].split('&')
        for paramsPair in paramPairs:
            paramSplits = paramsPair.split('=')
            if (len(paramSplits)) == 2:
                paramDict[paramSplits[0]] = paramSplits[1]
    return paramDict