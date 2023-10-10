import os, csv
from fontTools.agl import UV2AGL
from variableValues.linkPoints import *


class FontMeasurements:

    '''
    M = FontMeasurements()
    M.read(jsonPath)
    M.measure(f)

    # print all measurements
    M.print()

    print(M.definitions)
    print(M.values)

    '''

    def __init__(self, definitions=[]):
        self.definitions = definitions
        self.values = {}

    def read(self, jsonPath):
        M = readMeasurements(jsonPath)
        self.definitions = []
        for name, attrs in M['font'].items():
            try:
                pt1 = int(attrs['point 1'])
            except:
                pt1 = attrs['point 1']
            try:            
                pt2 = int(attrs['point 2'])
            except:
                pt2 = attrs['point 2']
            self.definitions.append((name, attrs['direction'], attrs['glyph 1'], pt1, attrs['glyph 2'], pt2, attrs.get('parent')))

    def measure(self, font, roundToInt=True, absolute=False):
        for d in self.definitions:
            M = Measurement(*d)
            M.absolute = self.absolute
            self.values[M.name] = M.measure(font, roundToInt=True, absolute=False)

    def print(self):
        for k, v in self.values.items():
            print(k, v)


class Measurement:

    '''
    M = Measurement('XTRA', 'x', 'H', 10, 'H', 9)
    print(M.measure(font))

    '''

    font     = None
    round    = True
    absolute = False

    def __init__(self, name, direction, glyphName1, pointIndex1, glyphName2, pointIndex2, parent=None):
        self.name        = name
        self.direction   = direction
        self.glyphName1  = glyphName1
        self.pointIndex1 = pointIndex1
        self.glyphName2  = glyphName2
        self.pointIndex2 = pointIndex2
        self.parent      = parent

    @property
    def glyph1(self):
        if self.font:
            if self.glyphName1 and self.glyphName1 in self.font:
                return self.font[self.glyphName1]

    @property
    def glyph2(self):
        if self.font:
            if self.glyphName2 and self.glyphName2 in self.font:
                return self.font[self.glyphName2]

    @property
    def point1(self):
        if self.glyph1 is not None:
            if isinstance(self.pointIndex1, int):
                return getPointAtIndex(self.glyph1, self.pointIndex1)
            else:
                return getAnchorPoint(self.font, self.pointIndex1)

    @property
    def point2(self):
        if self.glyph2 is not None:
            if isinstance(self.pointIndex2, int):
                return getPointAtIndex(self.glyph2, self.pointIndex2)
            else:
                return getAnchorPoint(self.font, self.pointIndex2)

    def measure(self, font, roundToInt=True, absolute=False, verbose=False):
        self.font = font

        if verbose:
            print(f'measuring {self.font}...')
            print(f'\tglyph 1   : {self.glyphName1} {self.glyph1}')
            print(f'\tpoint 1   : {self.pointIndex1} {self.point1}')
            print(f'\tglyph 2   : {self.glyphName2}  {self.glyph2}')
            print(f'\tpoint 2   : {self.pointIndex2} {self.point2}')
            print(f'\tdirection : {self.direction}')

        if self.font is None:
            return

        if self.point1 is None or self.point2 is None:
            return

        if self.direction == 'x':
            d = self.point2.x - self.point1.x

        elif self.direction == 'y':
            d = self.point2.y - self.point1.y

        else:
            d = sqrt((self.point2.x - self.point1.x)**2 + (self.point2.y - self.point1.y)**2)

        if absolute:
            d = abs(d)

        if roundToInt:
            d = round(d)

        if verbose:
            print(f'\tdistance : {d}')
            print('...done.\n')

        return d

