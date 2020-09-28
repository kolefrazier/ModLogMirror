import sys
from time import sleep
import time as t
from Config import ImageProcessing as imageConfig
from ImageProcessing import Data as ImageData
from ImageProcessing import Tesseract
from ImageProcessing import TextProcessing

def main():
    print(Tesseract._getCurrentDirectory())

    while True:
        # Get unprocessed
        Unprocessed = ImageData.getUnprocessed()

        for img in Unprocessed:
            # img = (id, "file")
            output = Tesseract.runTesseract(img[1])
            resultNormal, matchNormal = TextProcessing.checkText(output["normal"])
            resultInverted, matchInverted = TextProcessing.checkText(output["inverted"])

            if(resultNormal):
                print(f"Found spam in Normal image: {matchNormal}")

            if(resultInverted):
                print(f"Found spam in Inverted image: {matchInverted}")

        sleep(180)

if __name__ == '__main__':
    main()
