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
    colorComponents = 1, 0.35, 0
    colorDefault    = 0, 0.65, 1

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

    cellMarginsColor = 0.93,

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

                    # glyph not in font / draw empty cell
                    if glyphName not in currentFont:
                        with DB.savedState():
                            DB.fill(*self.cellMarginsColor)
                            DB.rect(x, y, stepX, stepY)
                            DB.line((x, y), (x + stepX, y + stepY))
                            DB.line((x, y + stepY), (x + stepX, y))
                        n += 1
                        continue

                    currentGlyph = currentFont[glyphName]
                    results = checkGlyph(defaultGlyph, currentGlyph)

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

                    _x = x + (stepX - currentGlyph.width * s) / 2
                    _y = y + stepY * self.glyphBaseline

                    # draw margins
                    with DB.savedState():
                        _margin = (stepX - currentGlyph.width * s) / 2
                        DB.stroke(None)
                        DB.fill(*self.cellMarginsColor)
                        DB.rect(x, y, _margin, stepY)
                        DB.rect(x + stepX, y, -_margin, stepY)

                    # draw check labels & special cell colors
                    if currentFont is not defaultFont:
                        with DB.savedState():
                            DB.stroke(None)
                            DB.translate(x, y)

                            _results = results.copy()
                            del _results['pointPositions']
                            # equal to default glyph, no checks shown
                            if all(results.values()) or (not currentGlyph.contours and not currentGlyph.components and all(_results.values())):
                                c = self.colorDefault
                                c += (0.2,)
                                with DB.savedState():
                                    DB.fill(*c)
                                    DB.rect(0, 0, stepX, stepY)
                            else:
                                # all components
                                if currentGlyph.components and not currentGlyph.contours:
                                    c = self.colorComponents
                                    c += (0.2,)
                                    with DB.savedState():
                                        DB.fill(*c)
                                        DB.rect(0, 0, stepX, stepY)

                                # draw check results
                                DB.font(self.cellLabelFont)
                                DB.fontSize(self.cellLabelSize)
                                for check in results.keys():
                                    if check == 'pointPositions':
                                        continue
                                    if results[check]:
                                        if check == 'points' and results['pointPositions']:
                                            DB.fill(*self.cellLabelEqual)
                                            drawCheck = True
                                        else:
                                            DB.fill(*self.cellLabelCompatible)
                                            drawCheck = False
                                    else:
                                        DB.fill(*self.cellLabelIncompatible)
                                        drawCheck = True
    
                                    if drawCheck:
                                        label = check[0].upper()
                                        DB.text(label, (1, 1))
                                        w, h = DB.textSize(label)
                                        DB.translate(w + 0.5, 0)

                    # draw contours / components
                    if currentGlyph.bounds:
                        with DB.savedState():
                            DB.stroke(None)
                            if all(results.values()):
                                if currentFont is not defaultFont:
                                    c = self.colorDefault
                                else:
                                    c = 0,
                            else:
                                if currentGlyph.components and not currentGlyph.contours:
                                    if currentFont is not defaultFont:
                                        c = self.colorComponents
                                    else:
                                        c = 0.5,
                                else:
                                    c = self.colorContours
                            DB.fill(*c)
                            DB.translate(_x, _y)
                            DB.scale(s)
                            drawGlyph(g)

                    # draw cell border
                    DB.rect(x, y, stepX, stepY)

                    n += 1

        if savePDF:
            pdfPath = os.path.join(os.getcwd(), f"glyphset_{self.familyName.replace(' ', '-')}.pdf")
            DB.saveImage(pdfPath)

