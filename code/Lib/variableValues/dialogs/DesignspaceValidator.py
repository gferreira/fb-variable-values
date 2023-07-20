from importlib import reload
import variableValues.validation
reload(variableValues.validation)

from fontParts.world import OpenFont
from fontTools.designspaceLib import DesignSpaceDocument
from vanilla import FloatingWindow, Button
from mojo.UI import GetFile, OutputWindow
from mojo.roboFont import OpenWindow
from variableValues.validation import *


class DesignspaceValidator:

    title = "DesignspaceValidator"
    defaultSource = None
    padding = 10
    textHeight = 20

    def __init__(self):
        h = self.textHeight*2 + self.padding*3
        self.w = FloatingWindow((200, h), self.title)
        x = y = p = self.padding
        self.w.getDesignspaceButton = Button(
                (x, y, -p, self.textHeight),
                'get designspace...',
                callback=self.getDesignspaceCallback,
                sizeStyle='small',
            )
        y += self.textHeight + p
        self.w.validateButton = Button(
                (x, y, -p, self.textHeight),
                '⚡ validate',
                callback=self.validateCallback,
                sizeStyle='small',
            )
        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    def getDesignspaceCallback(self, sender):
        self.designspacePath = GetFile(message='Get designspace…', title=self.title)

    def validateCallback(self, sender):
        D = DesignSpaceDocument()
        D.read(self.designspacePath)
        result = validateDesignspace(D)
        # write output to the console
        O = OutputWindow()
        O.clear()
        O.write(result)
        O.show()


if __name__ == '__main__':

    OpenWindow(DesignspaceValidator)
