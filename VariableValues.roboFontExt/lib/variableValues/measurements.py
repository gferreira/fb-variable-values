import os, csv
from fontTools.agl import UV2AGL
from variableValues.linkPoints import *

# -------
# objects
# -------

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
        self.definitions = [(name, attrs['direction'], attrs['glyph 1'], int(attrs['point 1']), attrs['glyph 2'], int(attrs['point 2']), attrs.get('parent')) for name, attrs in M['font'].items()]

    def measure(self, font):
        for d in self.definitions:
            M = Measurement(*d)
            self.values[M.name] = M.measure(font)

    def print(self):
        for k, v in self.values.items():
            print(k, v)

class Measurement:

    '''
    M = Measurement('XTRA', 'x', 'H', 10, 'H', 9)
    print(M.measure(font))

    '''

    font = None

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
            if self.glyphName1 in self.font:
                return self.font[self.glyphName1]
        #     else:
        #         print(f"glyph 1 ({self.glyphName1}) not in font")
        # else:
        #     print('no font given')

    @property
    def glyph2(self):
        if self.font:
            if self.glyphName2 in self.font:
                return self.font[self.glyphName2]
        #     else:
        #         print(f"glyph 2 ({self.glyphName2}) not in font")
        # else:
        #     print('no font given')

    @property
    def point1(self):
        if self.glyph1 is not None:
            return getPointAtIndex(self.glyph1, self.pointIndex1)

    @property
    def point2(self):
        if self.glyph2 is not None:
            return getPointAtIndex(self.glyph2, self.pointIndex2)

    def measure(self, font):
        self.font = font

        if self.point1 is None or self.point2 is None:
            return

        if self.direction == 'x':
            d = self.point2.x - self.point1.x

        elif self.direction == 'y':
            d = self.point2.y - self.point1.y

        else:
            d = sqrt((self.point2.x - self.point1.x)**2 + (self.point2.y - self.point1.y)**2)

        return d

