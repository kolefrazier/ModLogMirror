import os
from pathlib import Path
import subprocess
from ImageProcessing import Utility as ImgProcUtil

def _getCurrentDirectory():
    return Path().absolute()

def _prependImagePath(path):
    return ImgProcUtil.SAVE_PATH + path

def runTesseract(file):
    fileFullPath = _prependImagePath(file)
    invertedFileName = ImgProcUtil.invertImage(fileFullPath)
    output = {
        "normal": "",
        "inverted": ""
    }

    print(f"=== Tesseract results for: {file} ===")
    # Use run() instead of Popen() or call(). run() allows the capture of stdout while still waiting for the subproc to exit (like call())
    output["normal"] = subprocess.run(f"tesseract {fileFullPath} stdout -l eng", capture_output=True).stdout
    print(f"invertImage output: {output['normal']}")

    print(f"=== Tesseract results for: {invertedFileName} ===")
    output["inverted"] = subprocess.run(f"tesseract {invertedFileName} stdout -l eng", capture_output=True).stdout
    print(f"invertImage output: {output['inverted']}")

    return output
