from importlib import reload
import variableValues.validation
reload(variableValues.validation)

import os
import AppKit
from vanilla import *
from mojo.UI import OutputWindow
from mojo.roboFont import OpenFont, OpenWindow
from variableValues.validation import validateFonts


### DEPRECATED : use FontValidator ###


class BatchValidator:

    # TO-DO: add validation of font-level data

    title       = 'BatchValidator'
    padding     = 10
    lineHeight  = 22
    buttonWidth = 100
    verbose     = True

    _sources    = {}
    _targets    = {}

    def __init__(self):
        self.w = FloatingWindow(
                (600, 400), title=self.title,
                minSize=(200, 300))

        _groupSources = Group((0, 0, -0, -0))
        x = y = p = 0
        _groupSources.sourcesLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'source fonts')
        y += self.lineHeight + p/2
        _groupSources.sources = List(
                (x, y, -p, -p),
                [],
                allowsMultipleSelection=False,
                allowsEmptySelection=False,
                enableDelete=True,
                otherApplicationDropSettings=dict(
                    type=AppKit.NSFilenamesPboardType,
                    operation=AppKit.NSDragOperationCopy,
                    callback=self.dropSourcesCallback),
                )

        _groupTargets = Group((0, 0, -0, -0))
        x = y = p = 0
        _groupTargets.targetsLabel = TextBox(
                (x, y, -p, self.lineHeight),
                'target fonts')
        y += self.lineHeight + p/2
        _groupTargets.targets = List(
                (x, y, -p, -p),
                [],
                allowsMultipleSelection=True,
                allowsEmptySelection=False,
                enableDelete=True,
                otherApplicationDropSettings=dict(
                    type=AppKit.NSFilenamesPboardType,
                    operation=AppKit.NSDragOperationCopy,
                    callback=self.dropTargetsCallback),
                )

        self.w._splitDescriptors = [
            dict(view=_groupSources, identifier="sources"),
            dict(view=_groupTargets, identifier="targets"),
        ]
        x = y = p = self.padding
        self.w.splitView = SplitView(
                (x, y, -p, -(self.lineHeight + p*2)),
                self.w._splitDescriptors,
                isVertical=False,
                dividerStyle='thick',
            )

        y = -(self.lineHeight + p)

        # self.w.spinner = ProgressSpinner(
        #         (x, y+4, 16, 16),
        #         sizeStyle='small',
        #         displayWhenStopped=False)

        self.w.validateButton = Button(
                (-(self.buttonWidth+p), y, self.buttonWidth, self.lineHeight),
                'validate',
                callback=self.batchValidateFontsCallback,
                sizeStyle='small')

        self.w.getNSWindow().setTitlebarAppearsTransparent_(True)
        self.w.open()

    # -------------
    # dynamic attrs
    # -------------

    @property
    def sourcesList(self):
        return self.w._splitDescriptors[0]['view'].sources

    @property
    def sourceFont(self):
        sourceSelection = self.sourcesList.getSelection()
        if not sourceSelection:
            return 
        sourceItems = self.sourcesList.get()
        return sourceItems[sourceSelection[0]]

    @property
    def sourceFontPath(self):
        return self._sources[self.sourceFont]

    @property
    def targetsList(self):
        return self.w._splitDescriptors[1]['view'].targets

    @property
    def targetFonts(self):
        targetSelection = self.targetsList.getSelection()
        targetItems = self.targetsList.get()
        targetFonts = []
        for i, targetFont in enumerate(targetItems):
            if i not in targetSelection:
                continue
            if targetFont == self.sourceFont:
                continue
            targetFonts.append(targetFont)
        return targetFonts

    @property
    def targetFontPaths(self):
        return [self._targets[targetFont] for targetFont in self.targetFonts]

    # ---------
    # callbacks
    # ---------

    def dropSourcesCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingSources = sender.get()

        sources = dropInfo["data"]
        sources = [source for source in sources if source not in existingSources]
        sources = [source for source in sources if os.path.splitext(source)[-1].lower() == '.ufo']

        if not sources:
            return False

        if not isProposal:
            for source in sources:
                sourceName = os.path.splitext(os.path.split(source)[-1])[0]
                self._sources[sourceName] = source
                self.sourcesList.append(sourceName)
                self.sourcesList.setSelection([0])

        return True

    def dropTargetsCallback(self, sender, dropInfo):
        isProposal = dropInfo["isProposal"]
        existingTargets = sender.get()

        targets = dropInfo["data"]
        targets = [target for target in targets if target not in existingTargets]
        targets = [target for target in targets if os.path.splitext(target)[-1].lower() == '.ufo']

        if not targets:
            return False

        if not isProposal:
            for target in targets:
                targetName = os.path.splitext(os.path.split(target)[-1])[0]
                self._targets[targetName] = target
                self.targetsList.append(targetName)
                self.targetsList.setSelection([0])

        return True

    def batchValidateFontsCallback(self, sender):

        #-------------------
        # assert conditions
        #-------------------

        # no source font
        if not self.sourceFont:
            print('no source font selected.\n')
            return

        # no target fonts selected
        targetFonts = self.targetFonts
        if not len(targetFonts):
            print('no target fonts selected.\n')

        #---------------
        # batch validate
        #---------------

        print('batch validating fonts...\n')

        # get source font
        sourceFont = OpenFont(self.sourceFontPath, showInterface=False)
        print(f'\tsource font: {self.sourceFont}\n')

        # get target fonts
        targetFonts = [OpenFont(targetFontPath, showInterface=False) for targetFontPath in self.targetFontPaths]
        result = validateFonts(targetFonts, sourceFont)

        # write output to the console
        O = OutputWindow()
        O.clear()
        O.write(result)
        O.show()

        # done
        print('...done.\n')


# ----
# test
# ----

if __name__ == '__main__':

    OpenWindow(BatchValidator)
