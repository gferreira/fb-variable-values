import os

imgs = ['/Users/gferreira/hipertipo/tools/variable-values/docs/images/Screenshot 2024-01-22 at 09.18.13.png', '/Users/gferreira/hipertipo/tools/variable-values/docs/images/Screenshot 2024-01-22 at 09.18.16.png', '/Users/gferreira/hipertipo/tools/variable-values/docs/images/Screenshot 2024-01-22 at 09.18.19.png', '/Users/gferreira/hipertipo/tools/variable-values/docs/images/Screenshot 2024-01-22 at 09.18.21.png', '/Users/gferreira/hipertipo/tools/variable-values/docs/images/Screenshot 2024-01-22 at 09.18.24.png'
]

w, h = imageSize(imgs[0])
px, py = 21, 23

W = w + (len(imgs)-1) * px
H = h + (len(imgs)-1) * py

size(W, H)

x = 0
y = H - h

for imgPath in imgs:
    image(imgPath, (x, y))
    x += px
    y -= py


folder = os.path.dirname(os.getcwd())
imgsFolder = os.path.join(folder, 'images')
imgPath = os.path.join(imgsFolder, 'TempEdit_fonts.png')

saveImage(imgPath)

