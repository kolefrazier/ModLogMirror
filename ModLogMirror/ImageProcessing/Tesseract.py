# Resources
# ImageMagick Error and Warning Codes: https://imagemagick.org/script/exception.php
#   Any non-zero code is either a warning, error, or fatal error.
#   Warnings: 300-399
#   Error: 400-499
#   Fatal Error: 700-799

import os
from pathlib import Path
import subprocess
from ImageProcessing import Utility, Exceptions as ImageProcessingExceptions
from Config import ImageProcessing as ImageConfig

def _getCurrentDirectory():
    return Path().absolute()

def _prependImagePath(path):
    return ImageConfig.IMAGE_SAVE_LOCATION + path

def ProcessFile(file):
    """ Process a given file (image, gif, etc) through Tesseract. 
        Hashes the file, generates the inverted version, and processes both versions through Tesseract."""

    fileFullPath = _prependImagePath(file)
    invertedFileName = Utility.InvertImage(fileFullPath)
    output = {
        "normal": "",
        "inverted": ""
    }

    completedProcess = Utility.GenerateFileHash(fileFullPath)
    fileHash = None

    if completedProcess.returncode != 0:
        raise ImageProcessingExceptions.ImageMagickNonZeroReturnCode(completedProcess.returncode, file)
    elif len(completedProcess.stderr) > 0:
        raise ImageProcessingExceptions.ImageMagickError(fileHash.stderr, file)
    else:
        fileHash = completedProcess.stdout

    # print(f"=== Tesseract results for: {file} ===")
    # Use run() instead of Popen() or call(). run() allows the capture of stdout while still waiting for the subproc to exit (like call())
    # From the subprocess docs: https://docs.python.org/3/library/subprocess.html#using-the-subprocess-module
    # > The recommended approach to invoking subprocesses is to use the run() function 
    # > for all use cases it can handle. For more advanced use cases, the underlying Popen interface can be used directly.
    try:
        output["normal"] = subprocess.run(f"tesseract {fileFullPath} stdout -l eng", capture_output=True).stdout
        output["inverted"] = subprocess.run(f"tesseract {invertedFileName} stdout -l eng", capture_output=True).stdout
    except Exception as e:
        raise ImageProcessingExceptions.TesseractError(str(e), file)

    output = _sanitizeOutput(output)

    return output, fileHash

def _sanitizeOutput(results):
    return {
        "normal": results["normal"].decode('utf-8').strip(),
        "inverted": results["inverted"].decode('utf-8').strip()
    }