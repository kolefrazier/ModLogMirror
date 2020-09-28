BLACKLIST = ["PSO2", "AH", "%", "COM", "PSOAH", "MESETA", "5%"]

def checkText(input):
    global BLACKLIST
    inputSplit = str(input).replace("\\r", "").replace("\\n", " ").split(" ")

    for word in inputSplit:
        if word in BLACKLIST:
            return True, word

    return False, None