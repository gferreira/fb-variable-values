import os, glob, csv

csvFolder = '/Users/sergiogonzalez/Desktop/hipertipo/tools/VariableValues/example/relationships'
csvFiles  = glob.glob(f'{csvFolder}/*.csv')

csvData = {}

for csvPath in sorted(csvFiles):
    baseName = os.path.splitext(os.path.split(csvPath)[-1])[0]
    csvData[baseName] = []
    with open(csvPath, 'r', newline='') as csvFile:
        reader = csv.reader(csvFile, delimiter=',', quotechar='"')
        for row in reader:
            csvData[baseName].append(row)

# print(csvData.keys())

glyphs = {}

for baseName in csvData.keys():
    relations = csvData[baseName]
    for R in relations:
        glyphName = R[0]
        if glyphName == baseName:
            continue
        if glyphName not in glyphs:
            glyphs[glyphName] = {}
        if R[1] == '1':
            glyphs[glyphName]['width'] = baseName
        if R[2] == '1':
            glyphs[glyphName]['left'] = baseName
        if R[3] == '1':
            glyphs[glyphName]['right'] = baseName

for glyphName in glyphs.keys():
    print(glyphName, glyphs[glyphName].get('width'), glyphs[glyphName].get('left'), glyphs[glyphName].get('right'))
