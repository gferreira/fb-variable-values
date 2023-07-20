import os
from fontParts.world import OpenFont
from fontTools.designspaceLib import DesignSpaceDocument

'''
An object to read a designspace and return lists of sources based on their 'distance' from the neutral.

Uses David Berlow's terminology: monovar (neutral), duovar, trivar, quadravar.

'''


def getVarDistance(src, default):
    n = 0
    for k in src.location.keys():
        if src.location[k] != default.location[k]:
            n += 1
    return n


class DesignSpacePlus:
    
    matchGlyphCount = True # use this to ignore sparse masters
    
    def __init__(self, designSpacePath):
        self.document = DesignSpaceDocument()
        self.document.read(designSpacePath)

    @property
    def folder(self):
        return os.path.dirname(self.document.path)
    
    @property
    def default(self):
        return self.document.findDefault()

    @property
    def monovar(self): 
        return self.default

    @property
    def duovars(self):
        return self._getSourceSet(1)

    @property
    def trivars(self):
        return self._getSourceSet(2)

    @property
    def quadrivars(self):
        return self._getSourceSet(3)

    def _getSourceSet(self, n):
        varSet = []
        for src in self.document.sources:
            if src == self.default:
                continue
            d = getVarDistance(src, self.default)
            if d == n:
                varSet.append(src)

        # get default glyph count
        srcPath = os.path.join(self.folder, self.default.filename)
        f = OpenFont(srcPath, showInterface=False)
        glyphCount = len(f)
        f.close()

        # check glyph counts against default
        if self.matchGlyphCount:
            _varSet = []
            for src in varSet:
                srcPath = os.path.join(self.folder, src.filename)
                f = OpenFont(srcPath, showInterface=False)
                if len(f) == glyphCount:
                    _varSet.append(src)
                f.close()
            varSet = _varSet

        return varSet



