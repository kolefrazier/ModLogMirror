import sys
from time import sleep
import time as t
import logging
import traceback
import requests.exceptions as RequestExceptions

from Config import ImageProcessing as ImageConfig, Environment as EnvironmentConfig
from ImageProcessing import Data as ImageData, Tesseract, TextProcessing, Utility as ImageUtility, Exceptions as ImageExceptions

logger = logging.getLogger("imageocr-modlogmirror")
logger.setLevel(logging.INFO)
handler = logging.FileHandler(filename="imageocr.log", encoding="utf-8", mode="a")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

def main():
    if EnvironmentConfig.Environment == "dev":
        print(f"Processing files in: {Tesseract._getCurrentDirectory()}\\{ImageConfig.IMAGE_SAVE_LOCATION}")
        logger.setLevel(logging.DEBUG)

    NetworkErrorCounter = 0

    while True:
        # Get unprocessed images
        # Each record is a tuple: (id, submission_id, 'url', 'id.jpg')
        Unprocessed = ImageData.GetUnprocessed()

        for img in Unprocessed:
            try:
                # Create file names
                fileName, fileNameInverted = ImageUtility.GenerateFileNames(img[2], img[1])

                # Retrieve image. Exceptions handled below rather than in its own try/catch.
                ImageUtility.GetImage(img[2], fileName)

                # Process the image through Tesseract
                tesseractOutput, imageHash = Tesseract.ProcessFile(img[3])

                # checkText returns (bool, string)
                # bool - indicates if a match was found
                # string - the found text
                matchNormal = TextProcessing.CheckText(tesseractOutput["normal"])
                matchInverted = TextProcessing.CheckText(tesseractOutput["inverted"])

                #if EnvironmentConfig.Environment == "dev":
                #    if(len(matchNormal) > 0):
                #        print(f"Found spam in Normal image: {matchNormal}")
                #    if(len(matchInverted) > 0):
                #        print(f"Found spam in Inverted image: {matchInverted}")

                matches = None # Default to none so empty results go into the db as null
                if len(matchNormal) > 0 or len(matchInverted) > 0:
                    matches = {
                        "normal": matchNormal,
                        "inverted": matchInverted
                    }
            
                # Final tasks - update & cleanup
                # Note: Image deletion happens in a finally block below so that it's always ran on each image.
                ImageData.UpdateResults(img[0], matches, tesseractOutput, imageHash)
                NetworkErrorCounter = 0 # Reset the error counter

            # Errors are handled here, in one big block of exception handling.
            # Mostly to prevent wrapping individual parts and the ugly flow-control logic that would cause.
            except RequestExceptions.HTTPError as he:
                # This error is above ConnectionError, as ConnectionError seems to be more general.
                print(f"[HTTPError] Unsuccessful status code returned: {he.response}")
                logger.error(f"[HTTPError] str(he)")
                ImageData.UpdateError(img[0], str(he))
            except RequestExceptions.ConnectionError as ce:
                print(f"[ConnectionError] ConnectionError Thrown, sleeping 30s * {ServerErrorCounter}: str(e)")
                logger.error(f"[ConnectionError] Sleeping 30s * {ServerErrorCounter}: str(ce)")
                NetworkErrorCounter += 1
                sleep(30 * NetworkErrorCounter)
            except ImageExceptions.TesseractError as te:
                logger.error(f"[TesseractError] str(te)")
                ImageData.UpdateError(img[0], str(te))
            except ImageExceptions.ImageMagickError as ime:
                logger.error(f"[ImageMagickError] str(ime)")
                ImageData.UpdateError(img[0], str(ime))
            except ImageExceptions.ImageMagickNonZeroReturnCode as im:
                logger.error(f"[ImageMagickNonZeroReturnCode] str(im)")
                ImageData.UpdateError(img[0], str(im))
            except Exception as e:
                logger.error(f"[Exception] Unknown error occurred: {str(e)}\nFull traceback:\n{traceback.print_exc()}")
                ImageData.UpdateError(img[1], f"[Exception] Unknown error occurred: {str(e)}")
            finally:
                try:
                    ImageUtility.PurgeImageByFileName(fileName, fileNameInverted)
                except Exception as e:
                    logger.error(f"Error occurred while purging image: {str(e)}\nFull traceback:\n{traceback.print_exc()}")

        sleep(60)

if __name__ == '__main__':
    main()
