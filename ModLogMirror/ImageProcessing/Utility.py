from pathlib import Path
import requests
import subprocess
from PIL import Image, ImageOps
from Config import ImageProcessing as ImgConfig

_domains = {
    "reddit_single_image": "i.redd.it",
    "gyazo": "i.gyazo.com"
    # "reddit_image_gallery": "reddit.com"
    # "imgur": "imgur.com"
}
_extensions = [".png", ".jpg", ".jpeg"]

#SAVE_PATH = "imagedownloads/"
#IMAGE_MAGICK_PATH = "C:\\Users\\k-fra\\Desktop\\PSO2 AH spam samples\\ImageMagick\\magick.exe"

def IsImage(domain, url):
    if url is not None and (domain in _domains.values()):
        if ".png" in url or ".jpg" in url or ".jpeg" in url:
            return True
    
    return False

def GetImage(url, outFileName):
    """ Get and save the original image. Does not generate any derivative images (eg inverted). """
    fileRelativePath = f"{ImgConfig.IMAGE_SAVE_LOCATION}{outFileName}"
    if _checkFileExists(fileRelativePath) == False:
        img = Image.open(requests.get(url, stream=True).raw)
        img.save(fileRelativePath)

def EmptyImageSaveDirectory():
    dir = Path(ImgConfig.IMAGE_SAVE_LOCATION).iterdir()
    fileCount = 0
    for file in dir:
        fileCount += 1
        file.unlink() # Unlink is the PathLib way of deleting files and symbolic links.

    print(f"Deleted {fileCount} files from {ImgConfig.IMAGE_SAVE_LOCATION}")

def GenerateFileNames(url, submissionId):
    """ Generate a file name based on the image URL/path and the submission ID.
        Note: Use the submission ID instead of another ID. That way, the image stays linked to the submission.
        (Easily linked for mental-linking, that is.) """

    fileName = str(submissionId)
    fileNameInverted = str(submissionId)

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

def GenerateInvertedFileName(file):
    nameSplit = file.split(".")
    return f"{nameSplit[0]}_inverted.{nameSplit[1]}"

def GenerateFileHash(file):
    """ Generate a hash of the given file. Uses ImageMagick's identify function to generate the hash. """
    command = f"{ImgConfig.IMAGE_MAGICK_PATH} identify -format '%#' {file}"
    output = subprocess.run(command, capture_output=True)

    return output

def InvertImage(file):
    """ Generate a copy of the given image with inverted colors. Uses ImageMagick's convert function to invert the image. """
    outputFileName = GenerateInvertedFileName(file)
    command = f"{ImgConfig.IMAGE_MAGICK_PATH} convert {file} -channel RGB -negate {outputFileName}"

    output = subprocess.run(command, capture_output=True)

    return outputFileName

def PurgeImage(redditId, fileName):
    invertedFileName = GenerateInvertedFileName(fileName)
    Path(f"{ImgConfig.IMAGE_SAVE_LOCATION}{fileName}").unlink(missing_ok=True)
    Path(f"{ImgConfig.IMAGE_SAVE_LOCATION}{invertedFileName}").unlink(missing_ok=True)

def PurgeImageByFileName(fileName, fileNameInverted=None):
    if fileNameInverted == None:
        fileNameInverted = GenerateInvertedFileName(fileName)
    Path(f"{ImgConfig.IMAGE_SAVE_LOCATION}{fileName}").unlink(missing_ok=True)
    Path(f"{ImgConfig.IMAGE_SAVE_LOCATION}{fileNameInverted}").unlink(missing_ok=True)

def _checkFileExists(fileRelativePath):
    return Path(fileRelativePath).is_file()

def _checkUrl(url):
    return url is not None and any(ext in _extensions for ext in _extensions)