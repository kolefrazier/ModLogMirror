from Config import ImageProcessing as ImageConfig

def CheckText(input):
    """ Checks whether any content in the given input is in Imageconfig.WORD_BLACKLIST. 
        Returns a joined string of the matched words.
    """

    inputSplit = str(input).replace("\\r", "").replace("\\n", " ").split(" ")
    matchedWords = []

    for word in inputSplit:
        if word.lower() in ImageConfig.WORD_BLACKLIST:
            matchedWords.append(word)

    return [str(word) for word in set(matchedWords)]