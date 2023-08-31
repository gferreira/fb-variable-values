from defcon import Font
from fontTools.designspaceLib import DesignSpaceDocument
from fontMath.mathGlyph import MathGlyph
from mutatorMath.objects.mutator import Mutator, buildMutator

def calculateGlyph(font, glyphName, designspace, location, roundGeometry=True):

    axes = {}
    for axis in designspace.axes:
        axes[axis.name] = {}
        for k in ['tag', 'name', 'minimum', 'default', 'maximum', 'map']:
            axes[axis.name][k] = getattr(axis, k)

    glyphMasters = []
    for src in designspace.sources:
        if glyphName in src.mutedGlyphNames:
            continue
        d = dict(font=src.font, location=src.location, glyphName=glyphName)
        glyphMasters.append(d)

    items = []
    for item in glyphMasters:
        locationObject = item['location']
        fontObject     = item['font']
        glyphName      = item['glyphName']
        if not glyphName in fontObject:
            continue
        glyphObject = MathGlyph(fontObject[glyphName])
        items.append((locationObject, glyphObject))

    bias, m = buildMutator(items, axes=axes)
    instanceObject = m.makeInstance(location)

    if roundGeometry:
        instanceObject = instanceObject.round()

    targetGlyphObject = font[glyphName]
    targetGlyphObject.clear()

    instanceObject.extractGlyph(targetGlyphObject, onlyGeometry=True)


designSpacePath = '/Users/sergiogonzalez/Desktop/hipertipo/fonts/roboto-flex-avar2/sources/RobotoFlex.designspace'

D = DesignSpaceDocument()
D.read(designSpacePath)
for src in D.sources:
    src.font = Font(src.path)

g = CurrentGlyph()

L = {
    'XOPQ' :   96,
    "YOPQ" :   79,
    "XTRA" :  468,
    "YTUC" :  712,
    "YTLC" :  514,
    "YTAS" :  750,
    "YTDE" : -203,
    "YTFI" :  738,
}

calculateGlyph(g.font, g.name, D, L)

