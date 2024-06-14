from importlib import reload

import os, shutil, pathlib
from mojo.extensions import ExtensionBundle
from hTools3.modules.sys import pycClear, pyCacheClear, removeGitFiles

# --------
# settings
# --------

version          = '0.2.0'
baseFolder       = os.path.dirname(__file__)
libFolder        = os.path.join(baseFolder, 'code', 'Lib')
licensePath      = os.path.join(baseFolder, 'LICENSE')
resourcesFolder  = None
imagePath        = None

outputFolder     = baseFolder 
extensionPath    = os.path.join(outputFolder, 'VariableValues.roboFontExt')
docsFolder       = None

# ---------------
# build extension
# ---------------

def buildExtension():

    pycOnly = False

    B = ExtensionBundle()
    B.name                 = "VariableValues"
    B.developer            = 'Gustavo Ferreira'
    B.developerURL         = 'http://hipertipo.com/'
    B.icon                 = imagePath
    B.version              = version
    B.expireDate           = ''
    B.launchAtStartUp      = True
    B.html                 = False
    B.mainScript           = 'start.py'
    # B.uninstallScript      = ''
    B.requiresVersionMajor = '3'
    B.requiresVersionMinor = '4'
    B.addToMenu = [
        {
            'path'          : 'variableValues/dialogs/VarFontAssistant.py',
            'preferredName' : 'VarFont Assistant',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/VarGlyphAssistant.py',
            'preferredName' : 'VarGlyph Assistant',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/Measurements.py',
            'preferredName' : 'Measurements',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/GlyphValidator.py',
            'preferredName' : 'GlyphValidator',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/SourceValidator.py',
            'preferredName' : 'SourceValidator',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/GlyphSetProofer.py',
            'preferredName' : 'GlyphSetProofer',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/TempEdit.py',
            'preferredName' : 'TempEdit',
            'shortKey'      : '',
        },
        {
            'path'          : 'variableValues/dialogs/TempGlyphs.py',
            'preferredName' : 'TempGlyphs',
            'shortKey'      : '',
        },
    ]
    with open(licensePath) as license:
        B.license = license.read()

    if os.path.exists(extensionPath):
        print('\tdeleting existing .roboFontExt package...')
        shutil.rmtree(extensionPath)

    print('\tbuilding .roboFontExt package...')
    B.save(extensionPath,
        libPath=libFolder,
        resourcesPath=resourcesFolder,
        pycOnly=pycOnly)

    errors = B.validationErrors()
    if len(errors):
        print('ERRORS:')
        print(errors)

# ---------------
# build extension
# ---------------

pycClear(baseFolder)
pyCacheClear(baseFolder)
print(f'building VariableValues extension {version}...\n')
buildExtension()
print('\n...done!\n')
