import os, glob, datetime
import drawBot as DB
from fontParts.world import OpenFont
from defcon.pens.transformPointPen import TransformPointPen
from defcon.objects.component import _defaultTransformation
from variableValues.validation import *


def checkGlyph(g1, g2):
    return {
        'width'          : validateWidth(g1, g2),
        'points'         : validateContours(g1, g2),
        'pointPositions' : equalContours(g1, g2),
        'components'     : validateComponents(g1, g2),
        'anchors'        : validateAnchors(g1, g2),
        'unicodes'       : validateUnicodes(g1, g2),
    }

def drawGlyph(glyph):
    B = DB.BezierPath()
    glyph.draw(B)
    DB.drawPath(B)


class DecomposePointPen:

    def __init__(self, glyphSet, outPointPen):
        self._glyphSet = glyphSet
        self._outPointPen = outPointPen
        self.beginPath = outPointPen.beginPath
        self.endPath = outPointPen.endPath
        self.addPoint = outPointPen.addPoint

    def addComponent(self, baseGlyphName, transformation, *args, **kwargs):
        if baseGlyphName in self._glyphSet:
            baseGlyph = self._glyphSet[baseGlyphName]
            if transformation == _defaultTransformation:
                baseGlyph.drawPoints(self)
            else:
                transformPointPen = TransformPointPen(self, transformation)
                baseGlyph.drawPoints(transformPointPen)


class GlyphSetProofer:
    '''
    Visualize glyphset of UFO sources with validation checks against a default font.

    '''

    margins = 25, 10, 10, 10
    
    stepsX = 41
    stepsY = 26

    colorContours   = 0,
    colorComponents = 0.65,

    headerFont     = 'Menlo'
    headerFontSize = 8

    glyphScale    = 0.0047
    glyphBaseline = 0.36

    cellStrokeColor = 0.75,
    cellStrokeWidth = 0.5
    cellLabelFont   = 'Menlo-Bold'
    cellLabelSize   = 3.5

    cellLabelEqual        = 0, 0, 1
    cellLabelCompatible   = 0, 1, 0
    cellLabelIncompatible = 1, 0, 0

    def __init__(self, familyName, defaultFontPath, sourcePaths):
        self.familyName = familyName
        self.defaultFontPath = defaultFontPath
        self.sourcePaths = sourcePaths

    def build(self, savePDF=False):

        defaultFont = OpenFont(self.defaultFontPath, showInterface=False)
        sources     = [OpenFont(srcPath, showInterface=False) for srcPath in self.sourcePaths]
        sources.insert(0, defaultFont)

        m = self.margins
        s = self.glyphScale

        glyphNames  = defaultFont.glyphOrder

        now = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        for currentFont in sources:

            DB.newPage('A4Landscape')

            stepX = (DB.width()  - m[1] - m[3]) / self.stepsX
            stepY = (DB.height() - m[0] - m[2]) / self.stepsY

            # draw proof header
            DB.font(self.headerFont)
            DB.fontSize(self.headerFontSize)
            DB.text(f'{self.familyName}', (m[3], DB.height() - m[0] * 0.66), align='left')
            DB.text(f'{currentFont.info.styleName}', (DB.width() / 2, DB.height() - m[0] * 0.66), align='center')
            DB.text(now, (DB.width() - m[1], DB.height() - m[0] * 0.66), align='right')

            # draw cells
            DB.fill(None)
            DB.stroke(*self.cellStrokeColor)
            DB.strokeWidth(self.cellStrokeWidth)
            DB.fontSize(self.cellLabelSize)

            n = 0
            for i in range(stepsY):
                for j in range(stepsX):
                    x = m[3] + j * stepX
                    y = DB.height() - m[0] - (i + 1) * stepY

                    if n > len(glyphNames) - 1:
                        break

                    glyphName = glyphNames[n]
                    defaultGlyph = defaultFont[glyphName]

                    # draw empty cell
                    if glyphName not in currentFont:
                        DB.rect(x, y, stepX, stepY)
                        DB.line((x, y), (x + stepX, y + stepY))
                        DB.line((x, y + stepY), (x + stepX, y))
                        n += 1
                        continue

                    currentGlyph = currentFont[glyphName]

                    # decompose glyphs with components
                    if currentGlyph.components:
                        g = RGlyph()
                        pointPen = g.getPointPen()
                        decomposePen = DecomposePointPen(currentFont, pointPen)
                        currentGlyph.drawPoints(decomposePen)
                        g.name    = currentGlyph.name
                        g.unicode = currentGlyph.unicode
                        g.width   = currentGlyph.width
                    else:
                        g = currentGlyph

                    results = checkGlyph(defaultGlyph, currentGlyph)

                    _x = x + (stepX - currentGlyph.width * s) / 2
                    _y = y + stepY * self.glyphBaseline

                    if currentGlyph.bounds:

                        # draw contours / components
                        with DB.savedState():
                            DB.stroke(None)
                            if currentGlyph.components and not currentGlyph.contours:
                                c = colorComponents
                            else:
                                c = colorContours
                            DB.fill(*c)
                            DB.translate(_x, _y)
                            DB.scale(s)
                            drawGlyph(g)

                        # draw margins
                        with DB.savedState():
                            _margin = (stepX - currentGlyph.width * s) / 2
                            DB.stroke(None)
                            DB.fill(0.93)
                            DB.rect(x, y, _margin, stepY)
                            DB.rect(x + stepX, y, -_margin, stepY)

                    # draw cell
                    DB.rect(x, y, stepX, stepY)

                    # draw check labels
                    if currentFont is not defaultFont:
                        with DB.savedState():
                            DB.stroke(None)
                            DB.translate(x, y)
                            DB.font(self.cellLabelFont)
                            DB.fontSize(self.cellLabelSize)
                            for check in results.keys():
                                if check == 'pointPositions':
                                    continue
                                if results[check]:
                                    if check == 'points' and results['pointPositions']:
                                        DB.fill(*self.cellLabelEqual)
                                    else:
                                        DB.fill(*self.cellLabelCompatible)
                                else:
                                    DB.fill(*self.cellLabelIncompatible)
                                label = check[0].upper()
                                DB.text(label, (1, 1))
                                w, h = DB.textSize(label)
                                DB.translate(w + 0.5, 0)
                        
                    n += 1

        if savePDF:
            pdfPath = os.path.join(os.getcwd(), f'glyphset_{self.familyName}.pdf')
            DB.saveImage(pdfPath)
