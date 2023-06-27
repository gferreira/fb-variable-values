from math import sqrt

'''
Tools to work with linked pairs of points.

# forked from hTools3.modules.linkPoints

'''

KEY = 'com.fontBureau.glyphMeasurements'

def getPointAtIndex(glyph, i):
    # make a linear index of all points
    n = 0
    points = {}
    for ci, c in enumerate(glyph.contours):
        for pi, p in enumerate(c.points):
            points[n] = ci, pi
            n += 1
    # n+1 : right margin
    if i > len(points)-1:
        P = RPoint()
        P.x = glyph.width
        P.y = 0
        return P
    # -1 : left margin
    if i < 0:
        P = RPoint()
        P.x = 0
        P.y = 0
        return P
    # get point at index
    ci, pi = points[i]
    return glyph.contours[ci].points[pi]

def getIndexForPoint(glyph, pt):
    n = 0
    for ci, c in enumerate(glyph.contours):
        for pi, p in enumerate(c.points):
            if p == pt:
                return n
            n += 1

def getPointFromID(glyph, pointID):
    '''
    Get point object from a point identifier.

    Args:
        glyph (RGlyph): A glyph object.
        pointID (str): A point identifier.

    Returns:
        A point object (RPoint).

    '''
    for contour in glyph:
        for pt in contour.points:
            if pt.identifier == pointID:
                return pt

def getSelectedIDs(glyph):
    '''
    Get identifiers of selected points in glyph.

    Args:
        glyph (RGlyph): A glyph object.
        key (str): The key to the lib where the links are stored.

    Returns:
        A list of identifiers of selected points.

    '''
    return [pt.identifier if pt.identifier else pt.getIdentifier() for pt in glyph.selectedPoints]

def getDistance(p1, p2, direction=None):
    if direction == 'x':
        value = p2[0] - p1[0]
    elif direction == 'y':
        value = p2[1] - p1[1]
    else:
        value = sqrt((p2[0] - p1[0])**2 + (p2[1] - p1[1])**2)
    return abs(value)

### LINKS (measurements between two points)

def makeLink(glyph, pt1, pt2):
    '''
    Create a link between two given points.

    Args:
        pt1 (RPoint): A point.
        pt2 (RPoint): Another point in the same glyph.

    Returns:
        A tuple of two identifiers, one for each point.

    '''
    index1 = getIndexForPoint(glyph, pt1)
    index2 = getIndexForPoint(glyph, pt2)
    return index1, index2

def linkSelectedPoints(glyph, verbose=True):
    '''
    Create a new link between two selected points.

    Args:
        glyph (RGlyph): A glyph object.

    Returns:
        A tuple of two identifiers, one for each selected point.

    '''

    if not len(glyph.selectedPoints) == 2:
        if verbose:
            print('please select two points')
        return

    pt1 = glyph.selectedPoints[0]
    pt2 = glyph.selectedPoints[1]

    return makeLink(glyph, pt1, pt2)

def saveLinkToLib(glyph, link, name=None, direction=None, key=KEY, verbose=True):
    '''
    Save a given link to the glyph lib.

    Args:
        glyph (RGlyph): A glyph object.
        link (tuple): A pair of point indexes defining a link.
        name (str): The name of the link. (optional)
        direction (str): The direction of the measurement (x/y/a).
        key (str): The key to the lib where the links will be stored.

    '''
    if key not in glyph.lib:
        glyph.lib[key] = {}

    if link in glyph.lib[key] or reversed(link) in glyph.lib[key]:
        if verbose:
            print('link already in lib')
        return

    linkID = f'{link[0]} {link[1]}'
    glyph.lib[key][linkID] = {}

    if verbose:
        print(f'saving link "{linkID}" to the glyph lib ({glyph.name})...')

    if name is not None:
        glyph.lib[key][linkID]['name'] = name

    if direction is not None:
        glyph.lib[key][linkID]['direction'] = direction

def linkPoints(glyph, name=None, direction=None, key=KEY):
    '''
    Create a link between two selected points and save it in the glyph lib.

    Args:
        glyph (RGlyph): A glyph object.
        name (str): The name of the link.
        direction (str): The direction of the measurement (x/y). ### TO-DO: add angled
        key (str): The key to the lib where the links will be stored.

    '''
    L = linkSelectedPoints(glyph)
    if L is None:
        return
    saveLinkToLib(glyph, L, name=name, direction=direction, key=key)

def deleteLink(glyph, link, key=KEY):
    '''
    Delete the given link from the glyph lib.

    Args:
        glyph (RGlyph): A glyph object.
        link (tuple): A pair of point identifiers defining a link.
        key (str): The key to the lib where the links are stored.

    '''
    if key not in glyph.lib:
        print('no lib with this key.')
        return

    if link not in glyph.lib[key]:
        print('link not in lib.')
        return

    del glyph.lib[key][link]

def deleteAllLinks(glyph, key=KEY):
    '''
    Delete all links from the glyph lib.

    Args:
        glyph (RGlyph): A glyph object.
        key (str): The key to the lib where the links are stored.

    '''
    if key not in glyph.lib:
        # print('no lib with this key.')
        return
    glyph.lib[key] = {}

def deleteSelectedLinks(glyph, key=KEY):
    '''
    Delete selected links from the glyph lib.

    Args:
        glyph (RGlyph): A glyph object.
        key (str): The key to the lib where the links are stored.

    '''
    allLinks = set(getLinks(glyph))
    selectedLinks = set(getSelectedLinks(glyph))
    newLinks = allLinks.difference(selectedLinks)
    setLinks(glyph, list(newLinks))

def getLinks(glyph, key=KEY):
    '''
    Get all links in glyph.

    Args:
        glyph (RGlyph): A glyph object.
        key (str): The key to the lib where the links are stored.

    Returns:
        A list of all links in the glyph.

    '''
    if key not in glyph.lib:
        return {}
    return glyph.lib[key]

def setLinks(glyph, links, key=KEY):
    '''
    Store the given links in the glyph lib.

    Args:
        glyph (RGlyph): A glyph object.
        links (list): A list of links as tuples of point identifiers.
        key (str): The key to the lib where the links are stored.

    '''
    glyph.lib[key] = links

def getSelectedLinks(glyph, key=KEY):
    '''
    Get selected links in glyph.

    Args:
        glyph (RGlyph): A glyph object.
        key (str): The key to the lib where the links are stored.

    Returns:
        A list of links which are selected in the glyph.

    '''
    links = getLinks(glyph)
    IDs = getSelectedIDs(glyph)
    return [(ID1, ID2) for ID1, ID2 in links if (ID1 in IDs or ID2 in IDs)]

### MEASUREMENTS (font-level links)

def saveLinkToLib_font(font, name, link, key=KEY, verbose=True):
    if key not in font.lib:
        font.lib[key] = {}
    if verbose:
        print(f'saving link "{name}" to the font lib ({font.info.familyName} {font.info.styleName})...')
    if name not in font.lib[key]:
        font.lib[key][name] = {}
    for k, v in link.items():
        if k is None or v is None:
            continue
        k, v = str(k), str(v)
        if k == '<null>' or v == '<null>':
            continue
        font.lib[key][name][k] = v

def deleteLink_font(font, name, key=KEY):
    pass

def deleteAllLinks_font(font, key=KEY):
    pass

def getLinks_font(font, key=KEY):
    if key not in font.lib:
        return {}
    return font.lib[key]

def setLinks_font(font, links, key=KEY):
    pass

