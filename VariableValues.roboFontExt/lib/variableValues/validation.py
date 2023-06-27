
def isCentered(glyph, tolerance=1):
    if glyph.leftMargin == glyph.rightMargin:
        return True
    elif abs(glyph.leftMargin - glyph.rightMargin) == tolerance:
        return True        
    else:
        return False

def matchWidth(glyph, glyph2):
    if glyph.width == glyph2.width:
        return True
    else:
        return False

def matchLeft(glyph, glyph2, beam=None):
    if glyph.leftMargin == glyph2.leftMargin:
        return True
    else:
        return False

def matchRight(glyph, glyph2, beam=None):
    if glyph.rightMargin == glyph2.rightMargin:
        return True
    else:
        return False

f = CurrentFont()
g = f['O']

print(isCentered(g))
print(matchWidth(g, f['Q']))
print(matchLeft(g, f['Q']))
print(matchRight(g, f['Q']))
