class TesseractError(Exception):
    """ Exception raised for unknown errors raised during Tesseract processing.
    
        Attributes:
            message: explanation of the error
    """

    def __init__(self, message, file):
        super().__init__(f"Error processing file {file} through Tesseract. {message}")

class ImageMagickError(Exception):
    """ Exception raised for unknown errors raised during ImageMagick processing.
    
        Attributes:
            message: explanation of the error
    """

    def __init__(self, message, file):
        super().__init__(f"Error processing file {file} through ImageMagick. {message}")

class ImageMagickNonZeroReturnCode(Exception):
    """ Exception raised when Tesseract returns a non-zero return code.
    
        Attributes:
            message: explanation of the error
    """

    def __init__(self, returnCode, file):
        super().__init__(f"ImageMagick's Identify returned a non-zero code {returnCode} for file {file}")
