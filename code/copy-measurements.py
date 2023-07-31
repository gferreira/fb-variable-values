from variableValues.linkPoints import getLinks, getLinks_font
from variableValues.linkPoints import KEY as libKey

f1 = AllFonts().getFontsByFamilyName('Roboto Flex')[0]
f2 = AllFonts().getFontsByFamilyName('Amstelvar')[0]

# copy font measurements
fontMeasurements  = getLinks_font(f1)
f2.lib[libKey] = fontMeasurements

# copy glyph measurements
for gName in f1.glyphOrder:
    if gName not in f2:
        continue
    glyphMeasurements = getLinks(f1[gName])
    f2[gName].lib[libKey] = glyphMeasurements

f2.save()
f2.close()

f1.close()