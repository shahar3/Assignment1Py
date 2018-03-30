import sys, csv, re


# Our main method. In charge of all the logic of the program
def main(args):
    # Check if there is the function name argument
    if (len(args) > 0):
        command = args[0].lower()
        runCommand(command, args)
    else:
        print 'Allowed commands are:\n' \
              'UNION <input file path> <input file path> <output file path>\n' \
              'SEPERATE <input file path> <output file path> <output file path>\n' \
              'DISTINCT <input file path> <column index> <output file path>\n' \
              'LIKE <input file path> <column index> [parameter]\n'


# Check which command to call
def runCommand(command, args):
    if command == "union":
        # prepare all the required parameters (input1, input2, output)
        try:
            inputFile1 = args[1]
            inputFile2 = args[2]
            outputFile = args[3]
            union(inputFile1, inputFile2, outputFile)
        except IndexError:
            print "Usage: UNION <input file path> <input file path> <output file path>\n"
    elif command == "seperate":
        try:
            inputFile = args[1]
            outputFile1 = args[2]
            outputFile2 = args[3]
            seperate(inputFile, outputFile1, outputFile2)
        except IndexError:
            print "Usage: SEPERATE <input file path> <output file path> <output file path>\n"
    elif command == "distinct":
        try:
            inputFile = args[1]
            columnIndex = args[2]
            outputFile = args[3]
            distinct(inputFile, columnIndex, outputFile)
        except IndexError:
            print "Usage: DISTINCT <input file path> <column index> <output file path>\n"
    elif command == "like":
        try:
            inputFile = args[1]
            columnIndex = args[2]
            if (len(args) > 3):
                parameter = args[3]
                like(inputFile, columnIndex, parameter)
            else:
                like(inputFile, columnIndex)
        except IndexError:
            print "Usage: LIKE <input file path> <column index> [parameter]\n"
    else:
        print command + " is not a legal command"


# The union function. unite two files into one file
def union(inputFile1, inputFile2, outputFile):
    # check if the paths are valid, if the input files exist
    # first check the extension of the file
    if (validateFileNames(inputFile1, inputFile2, outputFile) == 0):
        # open the file
        file1 = readFile(inputFile1, getFileExtension(inputFile1))
        file2 = readFile(inputFile2, getFileExtension(inputFile2))

        # check that the 2 files have the same structure (the same number of columns and types)
        if isTheSameStructure(file1, file2):
            # write the files content into the output file
            writeToFile(outputFile, file1, 'file1')
            writeToFile(outputFile, file2, 'file2')


# An helper method to check if the 2 input file have the same structure
def isTheSameStructure(file1, file2):
    if (len(file1[0]) == len(file2[0])):
        i = 0
        for word1 in file1[0]:
            # check if the types of the files match
            word1 = word1.rstrip()  # remove the \n from the end
            word2 = file2[0][i].rstrip()

            type1 = getType(word1)
            type2 = getType(word2)

            # if types aren't the same return false
            if type1 != type2:
                print "Error! The tables format does not match"
                return False

            i += 1
        # if we iterate through all the values return true
        return True
    else:
        print "Error! The tables don't have the same number of columns"
        return False


# return the type of the value
def getType(word):
    try:
        varType = type(int(word))
    except ValueError:
        try:
            varType = type(float(word))
        except ValueError:
            varType = type(word)
    return varType


# Seperate one file into two files
def seperate(inputFile, outputFile1, outputFile2):
    # read inputFile
    if validateFileNames(inputFile) == 0:  # file extension is ok
        file = readFile(inputFile, getFileExtension(inputFile))
        # seperate the file into two files
        # filter all the file1 into a list and all file2 into another list
        file1 = list(map(lambda line: line[:-1], filter(lambda line: line[len(line) - 1] == 'file1', file)))
        file2 = list(filter(lambda line: line[len(line) - 1] == 'file2', file))
        print file1

        # write the list to different files
        writeToFile(outputFile1, file1)
        writeToFile(outputFile2, file2)
    pass


# Get all the unique values of a certain column
def distinct(inputFile, columnIndex, outputFile):
    if validateFileNames(inputFile) == 0:
        file = readFile(inputFile, getFileExtension(inputFile))
        # Check if the column index is in the structure range
        if (int(columnIndex) < len(file[0])):
            # get only unique values using set
            columnVals = sorted(set(map(lambda line: line.pop(int(columnIndex)), file)))
            writeToFile(outputFile, columnVals, distinct=True)
        else:
            print "Error! Column does not exist in table"
    pass


# Get all the records that equals to a certain parameter
def like(inputFile, columnIndex, parameter='*'):
    if validateFileNames(inputFile) == 0:
        file = readFile(inputFile, getFileExtension(inputFile))
        # Check if the column index is in the structure range
        if (int(columnIndex) < len(file[0])):
            # now look for the regular expression in the file
            columnVals = list(map(lambda line: line.pop(int(columnIndex)), file))
            # Ternary condition
            #r = re.compile(".*") if parameter == '*' else r = re.compile(parameter)
            filteredColumn = list(filter(r.match, columnVals))
            print filteredColumn
        else:
            print "Error! Column does not exist in table"
    pass


# An helper method that returns the file extension. if there is no file extensions
# specified return null
def getFileExtension(filePath):
    if (filePath.find(".") != -1):
        return filePath[filePath.find(".") + 1:]
    else:
        return None


# an helper method to check if the file extensions are ok
def validateFileNames(*files):
    for file in files:
        # extract the file extension
        fileExt = getFileExtension(file)
        if (fileExt != "txt" and fileExt != "csv"):
            print file + " is not a valid file name"
            return -1  # there is a problem
    return 0  # all the files are ok


# An helper method that return the file content
def readFile(file, extension):
    if (extension == "csv"):
        # read csv file
        fileObject = open(file)
        print fileObject.read()
        pass
    else:
        try:
            # read txt file
            with open(file) as fileObject:
                return extractFileContent(fileObject)
        except IOError:
            print 'The file ' + file + " doesn't exist"


# An helper method to extract the content of a txt file.
# it returns the casted text as a list of lists
def extractFileContent(fileObject):
    fileContent = []
    for line in fileObject:
        # split each line by the seperator
        # Check if the seperator is : or ::
        if (line.find("::") == -1):
            parts = line.rstrip().split(":")
        else:
            parts = line.rstrip().split("::")
        # now cast each part to his type
        fixedParts = castToType(parts)
        fileContent.append(fixedParts)
    return fileContent


# An helper method that get a line of parts from our text and cast them to their appropriate type
def castToType(parts):
    fixedParts = []
    for part in parts:
        partType = getType(part)
        if partType == int:
            part = int(part)
        elif partType == float:
            part = float(part)
        else:
            part = str(part)
        # add the casted part to the new list
        fixedParts.append(part)
    return fixedParts


# Write the lines to a specific file
def writeToFile(file, lines, origin=None, distinct=False):
    try:
        with open(file, 'a') as fileObj:
            for line in lines:
                # check if the function was called from the distinct function
                if (distinct):
                    fileObj.write(str(line) + '\n')
                else:
                    if (origin != None):
                        fileObj.write('::'.join(str(word) for word in line) + "::" + origin + "\n")
                    else:
                        fileObj.write('::'.join(str(word) for word in line) + "\n")
    except IOError:
        print "Error! Problem writing to file"


# Check if we run the program as our main program, if so call the main function with our arguments array
if __name__ == "__main__":
    main(sys.argv[1:])
