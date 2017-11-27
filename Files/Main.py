import numpy as np
import matplotlib.pyplot as plt
import skimage
import math
from PIL import Image as im
from skimage.feature import match_template
from skimage import io, data, draw
from skimage.draw import circle_perimeter
import PIL.ImageStat as imageStat  # fajna clasa analizująca  imageStat.Stat(Image)._get[co chcę (mean, stddev ...)]
import matplotlib.pyplot as plt
from skimage.filters.edges import convolve
import skimage.morphology as morph
from skimage.morphology import square

MULTIPLE_STD_PARAM = 2.0
FILE_SUFIX = ""
MASK_EDGE_HORIZONTAL = np.array([[1, 2, 1],
                                 [0, 0, 0],
                                 [-1, -2, -1]])
MASK_EDGE_VERTICAL = np.array([[1, 0, -1],
                               [2, 0, -2],
                               [1, 0, -1]]) / 8
MASK_EDGE_LAPLACE = np.array([[-1, -1, -1],
                              [-1, 8, -1],
                              [-1, -1, -1]])
MASK_MEAN = np.array([[1, 1, 1],
                      [1, 2, 1],
                      [1, 1, 1]]) / 20
MASK_DILATATION = np.array([[0, 1, 0],
                            [1, 1, 1],
                            [0, 1, 0]])


def readBitmapFromFile(fileName):
    path = "Photos/" + fileName + ".jpg"
    image = im.open(path)
    image = image.resize((int(image.size[0] / np.sqrt(6)), int(image.size[1] / np.sqrt(6))))
    return np.asarray(image)


def writeBitmapToFile(bitmap, fileName):
    image = im.fromarray(np.uint8(bitmap))
    path = "Done/" + fileName + FILE_SUFIX + ".jpg"
    image.save(path)


def findElement(myImage, myElement, myCopy):
    result = match_template(myImage, myElement)
    y, x = np.unravel_index(np.argmax(result), result.shape)
    height, width = myElement.shape
    myImage[y:y + height, x:x + width] = 0
    print(y)
    print(x)
    rr, cc = circle_perimeter(math.ceil(y + height / 2), math.ceil(x + width / 2), min(height, width))
    myCopy[rr, cc] = 1
    return myImage, myCopy


def filterImage(image):
    image = np.abs(convolve(image, MASK_MEAN))
    image = skimage.filters.sobel(image)
    image = image > skimage.filters.threshold_li(image)
    image = morph.erosion(image)
    image = morph.dilation(image)
    blob = makeBlobs(image)
    starts, stops = detectStartsAndEndsBlobs(blob)
    imageParts = divideImageOnParts(image, starts, stops)
    for i in range(len(imageParts)):
        img = im.fromarray(np.uint8(imageParts[i]) * 255)
        img.save(str(i)+".jpg")

def makeBlobs(image):
    blob = morph.dilation(image, square(30))
    return blob


def rowContainWhite(row):
    for i in range(len(row)):
        if row[i] == 1:
            return True
    return False


def detectStartsAndEndsBlobs(image):
    starts = []
    ends = []
    isBlob = False
    counter = 0
    for row in image:
        whiteInRow = rowContainWhite(row)
        if not isBlob and whiteInRow:
            starts.append(counter)
            isBlob = True
        if isBlob and not whiteInRow:
            ends.append(counter)
            isBlob = False
        counter += 1
    return starts, ends


def divideImageOnParts(image, starts, stops):
    parts = []
    part = []
    rewrite = False
    for i in range(len(image)):
        if not rewrite and i in starts:
            rewrite = True
            part = []
        if rewrite and i in stops:
            rewrite = False
            parts.append(part)
        if rewrite:
            part.append(image[i] * 1)
    return parts


def main():
    '''fileName = ["GGC0", "GGC3", "GGO3", "GPN3", "GPN6", "GPO0", "JBO0", "JBO3", "JGC0", "JGC3", "JPC6",
    "JPN3", "JPO3", "NBO0", "NBO6", "NGC3", "NPN0", "PBO0", "PGC0", "PGO3", "PPC3", "PPO3"]

    for i in fileName:
        makeImage(i)'''

    # fileName = "JGC0"
    # makeImage(fileName)
    # fig = plt.figure(figsize=(15, 10))
    myImage = io.imread("Photos/JGC0.jpg", as_grey=True)
    myCopy = io.imread("Photos/JGC0.jpg", as_grey=True)

    filterImage(myImage)

    # myImage = skimage.filters.median(myImage)
    # myImage = skimage.filters.sobel(myImage)


    # myCopy = skimage.filters.laplace(myCopy)


    # io.imshow(myImage)
    # plt.show()

    # myElement = io.imread("Patterns/full_note.jpg", as_grey=True)
    # for i in range(0, 4):
    #     myImage, myCopy = findElement(myImage, myElement, myCopy)
    # io.imshow(myCopy)
    # plt.show()


if __name__ == '__main__':
    main()
