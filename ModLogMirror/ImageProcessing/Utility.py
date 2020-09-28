import os
import requests
import subprocess
from PIL import Image, ImageOps
from Config import ImageProcessing as imgConfig

_domains = {
    "reddit": "i.redd.it", 
    #"imgur": "imgur.com"
}

SAVE_PATH = "imagedownloads/"
#IMAGE_MAGICK_PATH = "C:\\Users\\k-fra\\Desktop\\PSO2 AH spam samples\\ImageMagick\\magick.exe"
IMAGE_MAGICK_PATH = "C:/Users/k-fra/Desktop/PSO2 AH spam samples/ImageMagick/magick.exe"

def isImage(domain, url):
    if url is not None and (domain not in _domains.values()):
        if ".png" in url or ".jpg" in url or ".jpeg" in url:
            return True
    
    return False

def getImage(url, outFileName, outInvertedFileName):
    global SAVE_PATH

    img = Image.open(requests.get(url, stream=True).raw)
    img.save(f"{SAVE_PATH}{outFileName}")

    # PIL can't invert PNGs directly. So I'm going to try and move this to the parser and ImageMagick.
    #inverted = ImageOps.invert(img)
    #inverted.save(f"{SAVE_PATH}{outInvertedFileName}")

def generateFileNames(url, recordId):
    fileName = str(recordId)
    fileNameInverted = str(recordId)

    if ".png" in url:
        fileName += ".png"
        fileNameInverted += "_inverted.png"
    elif ".jpg" in url:
        fileName += ".jpg"
        fileNameInverted += "_inverted.jpg"
    elif ".jpeg" in url:
        fileName += ".jpeg"
        fileNameInverted += "_inverted.jpeg"

    return fileName, fileNameInverted

def generateInvertedFileName(file):
    nameSplit = file.split(".")
    return f"{nameSplit[0]}_inverted.{nameSplit[1]}"

def invertImage(file):
    global IMAGE_IMAGE_MAGICK_PATH

    outputFileName = generateInvertedFileName(file)
    command = f"{IMAGE_MAGICK_PATH} convert {file} -channel RGB -negate {outputFileName}"

    output = subprocess.call(command)
    print(f"invertImage output: {output}")

    return outputFileName
