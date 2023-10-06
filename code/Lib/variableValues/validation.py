import os
from fontParts.world import OpenFont

# ----------------------
# glyph-level validation
# ----------------------

def getSegmentTypes(glyph):
    '''
    Get a representation of all contour segments in a glyph, and their type.

    Returns:
        A list of 1-letter strings representing contour segments.

    '''
    segments = []
    for ci, c in enumerate(glyph.contours):
        for si, s in enumerate(c.segments):
            if s.type == 'curve':
                segmentType = 'C' # cubic
            elif s.type == 'qcurve':
                segmentType = 'Q' # quadratic
            else:
                segmentType = 'L' # straight
            segments.append(segmentType)
    return segments

def validateWidth(g1, g2):
    '''
    Check if the width of two glyphs match.

    Returns: `True` or `False`.

    '''
    return g1.width == g2.width

def validateAnchors(g1, g2):
    '''
    Check if the anchors in two glyphs match.

    - same number of anchors
    - same anchor names
    - same anchor order

    Returns: `True` or `False`.

    '''
    anchors1 = [a.name for a in g1.anchors]
    anchors2 = [a.name for a in g2.anchors]
    return anchors1 == anchors2

def validateComponents(g1, g2):
    '''
    Check if the components in two glyphs match.

    - same number of components
    - same component names
    - same component order

    Returns: `True` or `False`.

    '''
    components1 = [c.baseGlyph for c in g1.components]
    components2 = [c.baseGlyph for c in g2.components]
    return components1 == components2

def validateContours(g1, g2):
    '''
    Check if the contours in two glyphs match.

    - same number of contours
    - same number of segments
    - same segment types
    - same number of points (implied)

    Returns: `True` or `False`.

    '''
    if len(g1) != len(g2):
        return False
    segments1 = getSegmentTypes(g1)
    segments2 = getSegmentTypes(g2)
    return segments1 == segments2

def validateUnicodes(g1, g2):
    '''
    Check if the unicodes of two glyphs match.

    Returns: `True` or `False`.

    '''
    return g1.unicodes == g2.unicodes

def validateGlyph(g1, g2, width=True, points=True, components=True, anchors=True, unicodes=True):
    '''
    Check if two glyphs match.

    Returns:
        A dictionary of glyph attribute names and `True` or `False` results.

    '''
    results = {}
    if width:
        results['width'] = validateWidth(g1, g2)
    if points:
        results['points'] = validateContours(g1, g2)
    if components:
        results['components'] = validateComponents(g1, g2)
    if anchors:
        results['anchors'] = validateAnchors(g1, g2)
    if unicodes:
        results['unicodes'] = validateUnicodes(g1, g2)
    return results

# ---------------------
# font-level validation
# ---------------------

def validateFont(f1, f2, width=True, points=True, components=True, anchors=True, unicodes=True):
    '''
    Check if the *glyphs* in two fonts match.

    TO-DO: add checks for font-level data?

      - font dimensions
      - vertical metrics
      - kerning groups
      - kerning pairs/values

    Returns:
        A string with a report of all differences found.

    '''
    txt = f"validating font '{f1.info.familyName} {f1.info.styleName} ({f1.path})'...\n\n"
    for gName in f1.glyphOrder:
        if gName not in f2:
            txt += f'\t{gName}:\n'
            txt += f"\t- glyph not in font\n"
            txt += '\n'
            continue
        checks = validateGlyph(f1[gName], f2[gName], width=width, points=points, components=components, anchors=anchors, unicodes=unicodes)
        if not all(checks.values()):
            txt += f'\t{gName}:\n'
            for check, result in checks.items():
                if result is False:
                    txt += f"\t- {check} not matching\n"
            txt += '\n'

    return txt

def validateFonts(targetFonts, sourceFont, width=True, points=True, components=True, anchors=True, unicodes=True):
    '''
    Batch check if all fonts in `targetFonts` match the ones in sourceFont.

    Returns:
        A string with a report of all differences found in all fonts.

    '''
    txt = ''
    for targetFont in targetFonts:
        txt += validateFont(targetFont, sourceFont, width=width, points=points, components=components, anchors=anchors, unicodes=unicodes)
    return txt

def validateFont2(f1, f2, width=True, points=True, components=True, anchors=True, unicodes=True):
    '''
    Check if the *glyphs* in two fonts match.

    Returns:
        A dict with check results for each glyph in the target font.

    '''
    results = {}
    for gName in f1.glyphOrder:
        if gName not in f2:
            continue
        checks = validateGlyph(f1[gName], f2[gName])
        results[gName] = {}
        for check, result in checks.items():
            results[gName][check] = result
    return results

def validateFonts2(targetFonts, sourceFont, width=True, points=True, components=True, anchors=True, unicodes=True):
    '''
    Check if the *glyphs* in target fonts match with glyphs in a reference font.

    Returns:
        A dict with check results for each glyph in each target font.

    '''
    results = {}
    for targetFont in targetFonts:
        fileName = os.path.splitext(os.path.split(targetFont.path)[-1])[0]
        results[fileName] = validateFont2(targetFont, sourceFont, width=width, points=points, components=components, anchors=anchors, unicodes=unicodes)
    return results

# ----------------------
# designspace validation
# ----------------------

# DEPRECATED: use `validateFonts` instead

def validateDesignspace(designspace):
    txt = 'validating designspace...\n\n'
    defaultSrc = designspace.findDefault()
    defaultFont = OpenFont(defaultSrc.path, showInterface=False)
    txt += f'\tdefault source: {defaultSrc.filename}\n\n'
    for src in designspace.sources:
        if src == defaultSrc:
            continue
        srcFont = OpenFont(src.path, showInterface=False)
        txt += f'\tchecking {src.filename}...\n\n'
        for gName in defaultFont.glyphOrder:
            g1 = srcFont[gName]
            g2 = defaultFont[gName]
            checks = validateGlyph(g1, g2)
            if not all(checks.values()):
                txt += f'\t\t{gName}:\n'
                for check, result in checks.items():
                    if result is False:
                        txt += f"\t\t- {check} not matching\n"
                txt += '\n'
        srcFont.close()
    txt += '...done.\n\n'
    return txt

