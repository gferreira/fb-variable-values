from defcon import Font
from fontTools.designspaceLib import DesignSpaceDocument
from fontMath.mathGlyph import MathGlyph
from mutatorMath.objects.mutator import Mutator, buildMutator

def calculateGlyph(font, glyphName, designspace, location, roundGeometry=True):

    # patch location with default values
    default = designspace.findDefault().location
    for k, v in default.items():
        if k not in location:
            location[k] = v

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

L = {
    # 'slnt' :   0,
    # 'XOPQ' :   192*0.5,
    # "YOPQ" :   158*0.5,
    # "XTRA" :  734*0.75,
    # "YTUC" :  1456*0.5,
    # "YTLC" :  1072*0.5,
    # "YTAS" :  1536*0.5,
    # "YTDE" :  -416*0.5,
    # "YTFI" :  1516*0.5,
}

f = CurrentFont()

for glyphName in f.selectedGlyphNames:
    g = f[glyphName].naked()
    calculateGlyph(g.font, g.name, D, L)

