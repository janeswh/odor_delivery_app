########################################################
# Written by Beichen Liu for Doctor Claire Cheetham's Lab at the University of Pittsburgh
########################################################

# Intended for use with the OlfactometerCode_Millis Arduino code
# Aim: To create a GUI interface with better timing
###Main update: updates new file with timings as they occur

"""Instructions: 
1. Ctrl+SHIFT+E to launch the GUI window
    a. Terminate the code if this code crashed before
    b. If com error occurs, check that the arduino variable contains the correct
        com number, which can be found in the Tools tab on the Arduino IDE, 
        under the board number
        
2. This will bring user to the input data page--be sure to type in number of 
   solenoids, number of trials you want, and related times (if you only want 
   the odors to run for a set time, set min and max odor times to the same value
    a. If desired, type in the odor names, but this is not necessary
    
3. Click "Update" to update the input data--ensure that the status time reflects
   that it has been updated
   
4. Navigate to the desired tab

I. Randomize tab: Aim is to create a randomized order of odors given the number
   of trials specified in the Input tab
    a. Click the Randomize button and the odor order along with the times for
      each odor release
    b. Click Execute and ensure that the odors are being released correctly
   
II. Single Trials tab: Aim is to allow user to run a single trial of an odor
    a. Follow instructions in the window
    
III. DIY tab: Aim is to allow user to create their own sequence of odors

"""

### How the Arduino-Python Interaction Works:
""" 

When the Python code is executed, it will start up the Arduino and set up
Serial communication. Then, it will wait until the user hits "Execute". When
this occurs, Python will send data to the Arduino in batches of 3, [x,y,z],
where x is the odor number, y is how long to have the odor on for, and z
represents the delay between odors. Once it sends those numbers over, it will
wait for the Arduino to send numbers back. A '9' represents when a trigger to
the microscope was sent, '1' means that an odor is just starting, '2' means that
the odor was stopped, and '3' means that the delay was finished.

Before the first odor is released, the Arduino will trigger the microscope and
wait for 4s 

"""

########################################################
# Import Modules
########################################################

import serial
import tkinter
from tkinter import *
import time
import datetime
import random
import math
import decimal
from pathlib import Path

########################################################
# Helper Functions
########################################################


# Get RGB values for various colors
def rgbString(red, green, blue):
    # From CMU 15112: http://www.kosbie.net/cmu/spring-17/15-112/notes/notes-graphics.html
    return "#%02x%02x%02x" % (red, green, blue)


# Get a random number within a certain range
def getRandomNumber(i, j):
    val1 = i // 1  # find the non-decimal values for each i and j
    val2 = j // 1
    if (i < 1) or (j < 1):
        diffBWval = j - i
        incrementBy = random.randint(0, 10)
        newNum = i + diffBWval / incrementBy
        print("less than:")
        print(newNum)
        return newNum
    elif (i % val1 == 0.0) and (j % val2 == 0.0):
        return random.randint(i, j)
    else:
        # find the difference between the two values, then get a random increment to add to i
        diffBWval = j - i
        incrementBy = random.randint(0, 10)
        newNum = i + diffBWval / incrementBy
        print("else:")
        print(newNum)
        return newNum


# Receives serial data from arduino and decodes it, returning the value that was decoded
def getArduinoMessage(data):
    if arduino.in_waiting:
        sentInfo = arduino.readline().strip()
        decodeInfo = sentInfo.decode("utf-8")
        return decodeInfo


def resetRunPy(data):
    data.actSolenoid = []
    data.endSolenoid = []
    data.solValveCount = data.numSolenoids * [0]
    data.sent = 0  # if sent = 1, then that means a string has been sent to the arduino and we need to wait for it to be done
    data.timeTTL = []
    data.trigSignal = "no"
    data.finishedOrder = "No"


### Write initial text file
def checkTime(data):
    if (
        data.iniMilliSec >= 1000
    ):  # check if too many milliseconds -- convert to sec
        data.iniSec += 1
        data.iniMilliSec = data.iniMilliSec % 1000
    if data.iniSec >= 60:  # check if too many seconds -- convert to minutes
        data.iniMinute += 1
        data.iniSec = data.iniSec % 60
    if data.iniMinute >= 60:
        data.iniHour += 1
        data.iniMinute = data.iniMinute % 60
    return data.iniHour, data.iniMinute, data.iniSec, data.iniMilliSec


def writeToInitialText(name, data):
    fileToWrite = open(name, "w+")
    fileToWrite.write(
        "Solenoid Order: " + str(data.solenoidOrder)
    )  # write solenoid order
    fileToWrite.write("\r\n" + "\n")
    data.iniStart = datetime.datetime.now()
    data.iniHour = (data.iniStart).hour
    data.iniMinute = (data.iniStart).minute
    data.iniSec = (data.iniStart).second
    data.iniMicroSec = (data.iniStart).microsecond
    data.iniMilliSec = (
        data.iniMicroSec
    ) / 1000  # only has microseconds, which is 1/1000 milliseconds
    for odor in range(0, len(data.solenoidOrder)):
        newTime = checkTime(data)

        triggerStart = "%s/%s %s:%s:%s:%s" % (
            (data.iniStart).month,
            (data.iniStart).day,
            newTime[0],
            newTime[1],
            newTime[2],
            newTime[3],
        )
        data.iniMilliSec += data.trigger
        newTime = checkTime(data)
        odorStart = "%s/%s %s:%s:%s:%s" % (
            (data.iniStart).month,
            (data.iniStart).day,
            newTime[0],
            newTime[1],
            newTime[2],
            newTime[3],
        )

        newSec = data.odorTime[odor]
        data.iniSec += newSec
        newTime = checkTime(data)
        odorEnd = "%s/%s %s:%s:%s:%s" % (
            (data.iniStart).month,
            (data.iniStart).day,
            newTime[0],
            newTime[1],
            newTime[2],
            newTime[3],
        )

        newSec = data.delayTime
        data.iniSec += newSec
        newTime = checkTime(data)

        fileToWrite.write(
            "* "
            + str(data.solenoidOrder[odor])
            + " triggered at: "
            + triggerStart
        )
        fileToWrite.write("\r\n" + "\n")
        fileToWrite.write(
            "* " + str(data.solenoidOrder[odor]) + " released at: " + odorStart
        )
        fileToWrite.write("\r\n")
        fileToWrite.write(
            "* "
            + str(data.solenoidOrder[odor])
            + " was stopped at: "
            + odorEnd
            + "\r\n"
        )
        fileToWrite.write("\n")

    fileToWrite.close()


def createAndWriteInitialText(data):
    if len(data.fileNameWrite) != 0:
        checkText(data)  # check to make sure text does not already exist
        writeToInitialText(data.fileNameWrite + "(InitialGuess).txt", data)
    else:
        newTime = datetime.datetime.now()
        newFileName = "%s-%s-%s-%s-%s" % (
            newTime.month,
            newTime.day,
            newTime.year,
            newTime.hour,
            newTime.minute,
        )
        data.fileNameWrite = newFileName
        writeToInitialText(data.fileNameWrite + "(InitialGuess).txt", data)


def readText(
    name,
):  # opens the initial guess file and updates with actual times
    readFile = open(name)
    lineFiles = readFile.readlines()
    return lineFiles


def removeNewLines(readLines):
    newLines = readLines  # get array of lines
    for line in range(0, len(newLines)):  # iterate through each line
        currLine = newLines[line]
        if currLine == "\n":
            pass
        else:
            if currLine[0] == "*":
                removedNewLine = currLine[:-1]  # keep everything but the
                newLines[line] = removedNewLine  # change each of the lines
            else:
                pass
    return newLines


###Update this section
def changeText(name, data):
    readLines = readText(name)
    print(readLines)
    print("here is how long the doc is")
    print(len(readLines))
    for odor in range(1, len(data.timeTTL) + 1):
        triggerIndex = (
            8 * odor - 5
        )  # calculate position of the trigger time statement
        print(triggerIndex)
        startIndex = 8 * odor - 2  # position of start time statement
        print(startIndex)
        endIndex = 8 * odor  # position of end time statement
        print(endIndex)

        # change timing statements
        readLines[triggerIndex] = (
            str(data.solenoidOrder[odor - 1])
            + " triggered at: "
            + str(data.timeTTL[odor - 1])
        )
        print("here are the lengths of the lines and the startindex")
        print(len(readLines))
        print(startIndex)
        readLines[startIndex] = (
            str(data.solenoidOrder[odor - 1])
            + " released at: "
            + str(data.actSolenoid[odor - 1])
        )
        readLines[endIndex] = (
            str(data.solenoidOrder[odor - 1])
            + " was stopped at: "
            + str(data.endSolenoid[odor - 1])
        )

    # removedLines = removeNewLines(readLines)
    fileToWrite = open(name, "w+")
    fileToWrite.writelines(readLines)
    fileToWrite.close()
    print(readText(name))


### Actual File Text
def checkText(data):  # check if the file already exists in the folder
    pathName = Path(data.fileNameWrite + ".txt")

    if pathName.is_file():
        # If already a file, do not overwrite--add on increments
        indParenth = (data.fileNameWrite).find(
            "("
        )  # find the ( in name--means that we've indexed
        # print(indParenth)
        if indParenth == -1:  # have not added (1) to name yet
            for i in range(1, 20):
                newName = Path(data.fileNameWrite + "(" + str(i) + ").txt")
                if not newName.is_file():
                    data.fileNameWrite = (
                        data.fileNameWrite + "(" + str(i) + ")"
                    )
                    data.fileName[1] = data.fileNameWrite
                    break
                else:
                    pass
        else:  # the text file has already been incremented at least once
            numString = (data.fileNameWrite)[indParenth:]  # get (#)
            lenNumString = len(numString)
            newNumString = numString[
                1 : lenNumString - 1
            ]  # get just the number
            numIncrement = int(newNumString) + 1  # increment by 1
            data.fileNameWrite = (
                data.fileNameWrite[:indParenth] + "(" + str(numIncrement) + ")"
            )
            data.fileName[1] = data.fileNameWrite
        print(data.fileNameWrite)
    else:  # if the file is not already there, don't do anything
        print(data.fileNameWrite)


def createTextFile(data):
    if len(data.fileNameWrite) != 0:
        checkText(data)  # check to make sure text does not already exist
    else:
        newTime = datetime.datetime.now()
        newFileName = "%s-%s-%s-%s-%s" % (
            newTime.month,
            newTime.day,
            newTime.year,
            newTime.hour,
            newTime.minute,
        )
        data.fileNameWrite = newFileName


###Update File Name
def updateFileName(data):
    corrLabel = data.fileName[1]
    lengthLabel = len(corrLabel)
    if data.newInput == "BackSpace":
        newLabel = corrLabel[0 : lengthLabel - 1]
        data.fileName[1] = newLabel
    else:
        corrLabel += data.inputFileText
        data.fileName[1] = corrLabel


def resetSingleTrialOdors(data):
    data.singleBoxesInput = data.numSolenoids * ["white"]


def resetDIYTrialOdors(data):
    data.diyBoxesInput = data.numSolenoids * ["white"]
    data.diyOdorDurationColor = data.boxUnselected
    data.diyOdorDelayColor = data.boxUnselected
    data.diyMode = ""


########################################################
# Initiate the Arduino
########################################################
arduino = serial.Serial()
arduino.port = "COM7"  # Change COM PORT if COMPort error occurs
arduino.baudrate = 9600
arduino.timeout = 2
arduino.setRTS(FALSE)

arduino.open()
#


########################################################


def writeTextPerOdor(num, data):  # takes in which step is being used
    fileToWrite = open(
        data.fileNameWrite + ".txt", "w+"
    )  # open up the file to run
    fileToWrite.write("Solenoid Order: " + str(data.solenoidOrder) + "\r\n")

    for odor in range(0, len(data.timeTTL)):
        solenoid = data.solenoidOrder[odor] - 1

        odorName = data.totOdorNames[solenoid]
        odorLen = str(data.odorTime[odor])
        beganOdor = data.actSolenoid[odor]
        endOdor = data.endSolenoid[odor]
        TTLtime = data.timeTTL[odor]
        TTLname = "%s/%s %s:%s:%s:%s" % (
            TTLtime.month,
            TTLtime.day,
            TTLtime.hour,
            TTLtime.minute,
            TTLtime.second,
            TTLtime.microsecond,
        )
        beganTime = "%s/%s %s:%s:%s:%s" % (
            beganOdor.month,
            beganOdor.day,
            beganOdor.hour,
            beganOdor.minute,
            beganOdor.second,
            beganOdor.microsecond,
        )
        endTime = "%s/%s %s:%s:%s:%s" % (
            endOdor.month,
            endOdor.day,
            endOdor.hour,
            endOdor.minute,
            endOdor.second,
            endOdor.microsecond,
        )

        fileToWrite.write(
            "\n" + odorName + " triggered at: " + TTLname + "\r\n"
        )
        fileToWrite.write(
            "\n" + odorName + " released at: " + beganTime + "\r\n"
        )
        fileToWrite.write(odorName + " was stopped at: " + endTime + "\r\n")
    fileToWrite.close()


# Communicate with the Arduino
def runPyInfo(data):
    # Sends the information over to the arduino
    if data.mode == "Execute":
        if data.trigSignal == "yes":
            createTextFile(data)  # Update: check file name
            # fileToWrite = open(data.fileNameWrite+".txt","w+") #open up the file to run
            # fileToWrite.write("Solenoid Order: "+str(data.solenoidOrder)+"\r\n")

            print("Please wait as odor sequence is executed")
            createAndWriteInitialText(
                data
            )  ##Update: generate predicted timings
            for i in range(
                0, len(data.solenoidOrder)
            ):  # compile a string to be sent to Arduino to execute
                timeToSend = data.delayTime
                toBeSent = (
                    str(data.solenoidOrder[i])
                    + ","
                    + str(data.odorTime[i])
                    + ","
                    + str(timeToSend)
                )
                print(toBeSent)
                data.sent = 1
                arduino.write(toBeSent.encode())
                # Send the information to arduino and wait for something to come back
                while data.sent == 1:
                    messageReceived = getArduinoMessage(data)
                    # print("message: ")
                    # print(messageReceived)
                    if (
                        messageReceived == None
                    ):  ##update: check if y is anywhere in the messageReceived in case arduino sends too many at once
                        pass
                    elif "y" in messageReceived:
                        pass
                    else:
                        # print(messageReceived)
                        if (
                            "9" in messageReceived
                        ):  # time that the ttl signal was sent #Update: check if the string contains a 9
                            timeTTL = datetime.datetime.now()
                            data.timeTTL.append(timeTTL)
                        elif (
                            "1" in messageReceived
                        ):  # solenoid had been activated
                            timeSolenoid = datetime.datetime.now()
                            print(
                                str(data.solenoidOrder[i])
                                + " at "
                                + str(timeSolenoid)
                            )
                            data.actSolenoid.append(timeSolenoid)
                        elif "2" in messageReceived:  # solenoid had ended
                            timeOver = datetime.datetime.now()
                            print(
                                str(data.solenoidOrder[i])
                                + " done "
                                + str(timeOver)
                            )
                            data.endSolenoid.append(timeOver)
                        elif "3" in messageReceived:
                            writeTextPerOdor(i, data)
                            # changeText(data.fileNameWrite+"(InitialGuess).txt", data)
                            data.sent = (
                                0  # This signifies that the arduino is done
                            )
                            # and to send the next solenoid combo
            # reset the times
            data.actSolenoid = []
            data.endSolenoid = []
            data.timeTTL = []
            print("Completed odor sequence successfully")
            # toBeSent = "0,0,0" #This signals the end of the procedure #update: might not need these parts -- Arduino isn't doing anything with it anyway
            # arduino.write(toBeSent.encode())
            data.trigSignal = "no"
            data.mode = "Input Data"
            data.finishedOrder = "Yes"
        else:
            print("Complete")
    else:
        pass


## Main code is declared here to be run:
def runOrder(data):
    if data.trigSignal == "no":
        while (data.trigSignal == "no") and (data.finishedOrder == "No"):
            # createAndWriteInitialText(data) ##Update: generate predicted timings
            newMessage = getArduinoMessage(data)
            if (
                "y" in newMessage
            ):  ##Update: check to see if any of the string has a "y"
                print("Received trigger from Arduino")
                data.trigSignal = "yes"
                runPyInfo(data)
                # createTextFile(data)
                data.trigSignal = "no"
            else:
                pass


########################################################


def processInput(data):
    if data.mode == "Single Trial":
        corrLabel = (
            data.singleRepeatValue
        )  # get the current value of the label
        lengthLabel = len(corrLabel)
        if data.newInput == "BackSpace":  # alter the label as fit
            newLabel = corrLabel[0 : lengthLabel - 1]
            data.singleRepeatValue = newLabel
        else:
            corrLabel += data.inputFileText
            data.singleRepeatValue = corrLabel

    if data.mode == "DIY":
        if data.diyMode == "Odor Duration":
            corrLabel = data.diyOdorDuration
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.diyOdorDuration = newLabel
            else:
                corrLabel += data.inputFileText
                data.diyOdorDuration = corrLabel
        if data.diyMode == "Odor Delay":
            corrLabel = data.diyOdorDelay
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.diyOdorDelay = newLabel
            else:
                corrLabel += data.inputFileText
                data.diyOdorDelay = corrLabel

    if data.mode == "Input Data":
        if data.boxMode == "Num Odors":
            corrLabel = data.labelsValues[0]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.labelsValues[0] = newLabel
            else:
                corrLabel += data.inputFileText
                data.labelsValues[0] = corrLabel
        elif data.boxMode == "Num Trials":
            corrLabel = data.labelsValues[1]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.labelsValues[1] = newLabel
            else:
                corrLabel += data.inputFileText
                data.labelsValues[1] = corrLabel
        elif data.boxMode == "Min Odor Time":
            corrLabel = data.labelsValues[2]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.labelsValues[2] = newLabel
            else:
                corrLabel += data.inputFileText
                data.labelsValues[2] = corrLabel
        elif data.boxMode == "Max Odor Time":
            corrLabel = data.labelsValues[3]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.labelsValues[3] = newLabel
            else:
                corrLabel += data.inputFileText
                data.labelsValues[3] = corrLabel
        elif data.boxMode == "Odor Delay Time":
            corrLabel = data.labelsValues[4]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.labelsValues[4] = newLabel
            else:
                corrLabel += data.inputFileText
                data.labelsValues[4] = corrLabel

        elif data.boxMode == "Odor 1 Name":
            corrLabel = data.odorNames[0]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[0] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[0] = corrLabel
        elif data.boxMode == "Odor 2 Name":
            corrLabel = data.odorNames[1]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[1] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[1] = corrLabel
        elif data.boxMode == "Odor 3 Name":
            corrLabel = data.odorNames[2]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[2] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[2] = corrLabel
        elif data.boxMode == "Odor 4 Name":
            corrLabel = data.odorNames[3]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[3] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[3] = corrLabel
        elif data.boxMode == "Odor 5 Name":
            corrLabel = data.odorNames[4]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[4] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[4] = corrLabel
        elif data.boxMode == "Odor 6 Name":
            corrLabel = data.odorNames[5]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[5] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[5] = corrLabel
        elif data.boxMode == "Odor 7 Name":
            corrLabel = data.odorNames[6]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[6] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[6] = corrLabel
        elif data.boxMode == "Odor 8 Name":
            corrLabel = data.odorNames[7]
            lengthLabel = len(corrLabel)
            if data.newInput == "BackSpace":
                newLabel = corrLabel[0 : lengthLabel - 1]
                data.odorNames[7] = newLabel
            else:
                corrLabel += data.inputFileText
                data.odorNames[7] = corrLabel
        elif data.boxMode == "Input File Name":
            updateFileName(data)


def assignOdorNames(data):
    # just checks to make sure that there was something that input
    if data.refreshedSingle == "No":
        data.singleBoxesInput = data.numSolenoids * ["white"]
        data.singleLabelsValues = data.numSolenoids * [""]
        data.diyBoxesInput = data.numSolenoids * ["white"]
        data.refreshedSingle = "Yes"
    for count in range(0, len(data.singleLabelsValues)):
        newName = data.odorNames[count]
        if data.odorNames[count] != "":
            data.singleLabelsValues[count] = newName
        else:
            data.singleLabelsValues[count] = data.odorLabels[count]
    data.totOdorNames = data.singleLabelsValues


def updateInputInfo(data):
    if data.labelsValues[0] == "":
        data.status[1] = "Not enough information for Odors"
    else:
        # convert strings into ints
        if data.labelsValues[0] != "":
            data.numSolenoids = int(data.labelsValues[0])
            data.singleBoxesInput = data.numSolenoids * ["white"]
            data.singleLabelsValues = data.numSolenoids * [""]
            data.diyBoxesInput = data.numSolenoids * ["white"]
        if data.labelsValues[1] != "":
            data.numTrials = int(
                data.labelsValues[1]
            )  # convert text values to integers
        if data.labelsValues[2] != "":
            data.minOdorTime = float(data.labelsValues[2])
        if data.labelsValues[3] != "":
            data.maxOdorTime = float(data.labelsValues[3])
        if data.labelsValues[4] != "":
            data.delayTime = int(data.labelsValues[4])
            data.refreshedSingle = "No"
            assignOdorNames(data)

        if (
            data.fileName[1] != ""
        ):  # Use this to create a new file for the data
            data.fileNameWrite = data.fileName[1]


def updateSingleMode(data):
    # takes the number of repeats and updates the solenoid order
    if data.singleRepeatValue == "":
        data.singleStatus[1] = "Please indicate # of repeats"
    else:
        data.chosenSingleOdorRepeats = int(data.singleRepeatValue)
        data.solenoidOrder = []
        data.odorTime = []
        for order in range(0, data.chosenSingleOdorRepeats):
            data.solenoidOrder.append(data.chosenSingleOdor)
            odorTime = getRandomNumber(data.minOdorTime, data.maxOdorTime)
            data.odorTime.append(odorTime)
        print(data.solenoidOrder)
        print(data.odorTime)


def updateDIYMode(data):
    # Check if DIY duration or odor is equal to 0
    # if not: update, like how updateSingleMode works
    # set the solenoid order, odor time=0, add
    data.solenoidOrder = []
    # reset the odor order
    data.odorTime = []
    # reset odor time
    if (data.diyOdorDuration == "") or (data.diyOdorDelay == ""):
        data.diyStatus[1] = "Please input odor duration and delay"
    else:
        data.delayTime = int(data.diyOdorDelay)
        totalOdors = len(data.diyOdorOrder)
        newOdorTime = int(data.diyOdorDuration)  # Duration for each odor
        data.solValveCount = data.numSolenoids * [0]
        for odor in range(0, totalOdors):
            newOdor = int((data.diyOdorOrder)[odor])
            (data.solenoidOrder).append(newOdor)
            (data.odorTime).append(newOdorTime)
        print(data.solenoidOrder)
        print(data.odorTime)


def resetBoxColor(data):
    data.boxesInput = ["white", "white", "white", "white", "white"]
    data.odorsBoxesInput = len(data.odorLabels) * ["white"]
    data.fileNameBoxColor = "white"
    data.updateFill = rgbString(160, 210, 219)


#########################################################
# For the user interface:
def init(data):
    # load data.xyz as appropriate
    ###Declare Constants Here
    data.numTrials = 0
    data.numSolenoids = 0
    data.maxOdorTime = 0  # seconds
    data.minOdorTime = 0  # seconds
    data.solValveCount = data.numSolenoids * [
        0
    ]  # keeps track of which ones have been used

    ###Keep track of the input
    data.trigSignal = "no"
    data.delayTime = 0

    data.finishedOrder = "No"

    data.solenoidOrder = []
    data.odorTime = []  # How long each solenoid will be running for
    data.count = 0  # counts which step of the way we are in

    ###For predicted timings:
    data.trigger = 100  # in milliseconds
    data.iniStart = datetime.datetime.now()
    data.iniHour = (data.iniStart).hour
    data.iniMinute = (data.iniStart).minute
    data.iniSec = (data.iniStart).second
    data.iniMicroSec = (data.iniStart).microsecond
    data.iniMilliSec = (
        data.iniMicroSec
    ) / 1000  # only has microseconds, which is 1/1000 milliseconds

    ###Keep track of when the solenoids were activated
    data.actSolenoid = []
    data.endSolenoid = []
    data.sent = 0  # if sent = 1, then that means a string has been sent to the arduino and we need to wait for it to be done
    data.timeTTLName = "TTL to microscope sent at: "
    data.timeTTL = []

    ################################################
    ###For the GUI
    ################################################

    data.mode = "Input Data"
    data.tabWidths = data.width / 6
    data.tabHeight = data.height / 10
    data.tabNames = ["Input Data", "DIY", "Random Trials", "Single Trial"]
    # Colors for the tabs and select color scheme
    data.tabColSelected = [
        rgbString(110, 107, 123),
        rgbString(255, 107, 108),
        rgbString(91, 95, 151),
        rgbString(127, 194, 155),
    ]
    data.tabColUnselected = [
        rgbString(220, 214, 247),
        rgbString(255, 225, 225),
        rgbString(156, 159, 192),
        rgbString(178, 218, 195),
    ]
    data.tabSpecs = "Helvetica 12 bold"  # font and font size for tabs

    ###For Input Data Mode:
    data.labels = [
        "# Odors:",
        "# Trials:",
        "min. Odor Time (s):",
        "max. Odor Time (s)",
        "Time Between Odors (s):",
    ]
    data.labelsValues = len(data.labels) * [""]

    data.fileNameWrite = ""

    data.odorLabels = [
        "Odor 1",
        "Odor 2",
        "Odor 3",
        "Odor 4",
        "Odor 5",
        "Odor 6",
        "Odor 7",
        "Odor 8",
    ]
    data.odorLabelWPos = [data.width / 3, 5 * data.width / 6]
    data.odorLabelH = data.height / 20
    data.indentLabel = data.height / 40

    data.odorNames = ["", "", "", "", "", "", "", ""]
    data.inputSpecs = "Helvetica 12"
    data.boxSelected = rgbString(255, 246, 143)  # Color box turns if selected
    data.boxUnselected = "white"
    data.boxesInput = [
        "white",
        "white",
        "white",
        "white",
        "white",
    ]  # specs box colors
    data.odorsBoxesInput = len(data.odorLabels) * ["white"]  # Odor box colors

    # Input labels
    data.boxesInputText = len(data.boxesInput) * [""]

    # keep track of which key was just pressed
    data.newInput = ""

    data.boxMode = (
        "None"  # Change box mode to send the input to the correct places
    )

    data.fileName = ["File name: ", ""]
    data.inputFileText = ""
    data.fileNameBoxColor = "white"

    data.updateName = "Update"
    data.updateFill = rgbString(160, 210, 219)

    data.status = ["Status: ", "Not Updated"]

    ## DIY Screen:
    data.diyUndoFill = rgbString(255, 107, 108)
    data.DIYupdateFill = rgbString(160, 210, 219)
    data.DIYupdateName = "Update"
    data.diyChooseOdorsLabels = [
        "Choose Odor Order: ",
        "Odor Duration (s): ",
        "Delay After Odor (s): ",
    ]
    data.diyOdorLists = [
        "Odor Order: ",
        "Odor Duration (for all odors): ",
        "Delay After Odor (for all odors): ",
    ]
    data.diyStatus = ["Status: ", "Please Update the Odor List"]
    data.diyMode = ""
    data.diyOdorOrder = []
    data.diyOdorDuration = ""
    data.diyOdorDelay = ""
    data.diyOdorOrderColors = len(data.odorLabels) * ["white"]
    data.diyBoxesInput = data.numSolenoids * ["white"]
    data.diyBoxChosen = data.boxSelected
    data.updateDIYMode = "No"

    data.diyOdorDurationColor = data.boxUnselected
    data.diyOdorDelayColor = data.boxUnselected

    ## Random Screen:
    data.randomMode = "No"
    data.randomizeName = "Randomize"
    data.randomizeStatus = ["Status: ", "Please click 'Randomize'"]
    data.randomizeFill = rgbString(240, 101, 67)
    data.randomizeTrialLabels = [
        "Odor Order: ",
        "Time for Each Odor: ",
        "Time Between Odors: ",
    ]

    ##Execute Button--executes the sequence
    data.executeFill = rgbString(179, 216, 156)
    data.executeName = "Execute Sequence"

    # While Running:
    data.executeStatus = ["Status: ", "Executing Sequence"]

    ##Single Odor Repeated:
    data.refreshedSingle = "No"
    data.singleLabels = [
        "Please Choose an Odor: ",
        "How many times should it repeat: ",
    ]

    data.updateSingleName = "Update Single Trials"
    data.updateSingleMode = "No"

    data.singleBoxesInput = data.numSolenoids * ["white"]
    data.singleLabelsValues = data.numSolenoids * [""]
    data.singleBoxChosen = data.boxSelected

    data.singleRepeatValue = ""
    data.chosenSingleOdorRepeats = 0

    data.singleRepeatInput = "white"

    data.chosenSingleOdor = 0

    data.singleStatus = ["Status: ", "Please Choose an Odor and # of Repeats"]


def randomize(data):
    # takes in the first odor and second odor number and creates random list of odor order and time
    if data.numTrials == 0:
        data.randomizeStatus[1] = "Cannot perform 0 trials"
    else:
        data.solValveCount = data.numSolenoids * [0]
        data.solenoidOrder = []  # reset the count and the order+odor time
        data.odorTime = []
        while len(data.solenoidOrder) < data.numTrials:
            newOdor = getRandomNumber(
                1, data.numSolenoids
            )  # randint is inclusive
            newOdorTime = getRandomNumber(data.minOdorTime, data.maxOdorTime)

            count = (data.solValveCount)[
                newOdor - 1
            ]  # check how many times this valve has turned on
            if count < (math.ceil(data.numTrials / data.numSolenoids)):
                (data.solenoidOrder).append(newOdor)
                (data.odorTime).append(newOdorTime)
                (data.solValveCount)[newOdor - 1] += 1
            else:
                pass
        print(data.solenoidOrder)
        print(data.odorTime)


###############################
def mousePressed(event, data):
    ###############################
    if data.mode == "Input Data":
        ##For switching between tabs
        if (data.tabWidths <= event.x < 2 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "DIY"
        elif (2 * data.tabWidths <= event.x < 3 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "Random Trials"
        elif (3 * data.tabWidths <= event.x < 4 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "Single Trial"
        elif (2 * data.width / 12 < event.x <= 5 * data.width / 12) and (
            data.tabHeight + 10
            < event.y
            <= data.tabHeight + data.odorLabelH + 10
        ):
            if data.boxesInput[0] == "white":
                data.boxMode = "Num Odors"
                # Select the box and deselect the box
                data.boxesInput = len(data.boxesInput) * [data.boxUnselected]

                data.boxesInput[0] = data.boxSelected
        elif (8 * data.width / 12 < event.x < 11 * data.width / 12) and (
            data.tabHeight + 10
            < event.y
            <= data.tabHeight + data.odorLabelH + 10
        ):
            if data.boxesInput[1] == "white":
                data.boxMode = "Num Trials"
                # Select the box and deselect the box
                resetBoxColor(data)
                data.boxesInput[1] = data.boxSelected

        elif (2 * data.width / 12 < event.x <= 3 * data.width / 12) and (
            data.tabHeight + 10 + 2 * data.odorLabelH
            < event.y
            <= data.tabHeight + 3 * data.odorLabelH + 10
        ):
            if data.boxesInput[2] == "white":
                data.boxMode = "Min Odor Time"
                resetBoxColor(data)

                data.boxesInput[2] = data.boxSelected

        elif (5 * data.width / 12 < event.x <= 6 * data.width / 12) and (
            data.tabHeight + 10 + 2 * data.odorLabelH
            < event.y
            <= data.tabHeight + 3 * data.odorLabelH + 10
        ):
            if (data.boxesInput[3]) == "white":
                data.boxMode = "Max Odor Time"
                resetBoxColor(data)

                data.boxesInput[3] = data.boxSelected

        elif (9 * data.width / 12 < event.x <= 10 * data.width / 12) and (
            data.tabHeight + 10 + 2 * data.odorLabelH
            < event.y
            <= data.tabHeight + 3 * data.odorLabelH + 10
        ):
            if (data.boxesInput[4]) == "white":
                data.boxMode = "Odor Delay Time"
                resetBoxColor(data)

                data.boxesInput[4] = data.boxSelected

        elif (2 * data.width / 12 < event.x <= 5 * data.width / 12) and (
            7 * data.height / 24 < event.y <= 8 * data.height / 24
        ):
            if data.odorsBoxesInput[0] == "white":
                data.boxMode = "Odor 1 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[0] = data.boxSelected
        elif (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            7 * data.height / 24 < event.y <= 8 * data.height / 24
        ):
            if data.odorsBoxesInput[1] == "white":
                data.boxMode = "Odor 2 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[1] = data.boxSelected

        elif (2 * data.width / 12 < event.x <= 5 * data.width / 12) and (
            9 * data.height / 24 < event.y <= 10 * data.height / 24
        ):
            if data.odorsBoxesInput[2] == "white":
                data.boxMode = "Odor 3 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[2] = data.boxSelected

        elif (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            9 * data.height / 24 < event.y <= 10 * data.height / 24
        ):
            if data.odorsBoxesInput[3] == "white":
                data.boxMode = "Odor 4 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[3] = data.boxSelected

        elif (2 * data.width / 12 < event.x <= 5 * data.width / 12) and (
            11 * data.height / 24 < event.y <= 12 * data.height / 24
        ):
            if data.odorsBoxesInput[4] == "white":
                data.boxMode = "Odor 5 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[4] = data.boxSelected

        elif (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            11 * data.height / 24 < event.y <= 12 * data.height / 24
        ):
            if data.odorsBoxesInput[5] == "white":
                data.boxMode = "Odor 6 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[5] = data.boxSelected

        elif (2 * data.width / 12 < event.x <= 5 * data.width / 12) and (
            13 * data.height / 24 < event.y <= 14 * data.height / 24
        ):
            if data.odorsBoxesInput[6] == "white":
                data.boxMode = "Odor 7 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[6] = data.boxSelected

        elif (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            13 * data.height / 24 < event.y <= 14 * data.height / 24
        ):
            if data.odorsBoxesInput[7] == "white":
                data.boxMode = "Odor 8 Name"
                resetBoxColor(data)

                data.odorsBoxesInput[7] = data.boxSelected

        elif (2 * data.width / 12 < event.x <= 5 * data.width / 12) and (
            15 * data.height / 24 < event.y <= 16 * data.height / 24
        ):
            if data.fileNameBoxColor == "white":
                data.boxMode = "Input File Name"
                resetBoxColor(data)

                data.fileNameBoxColor = data.boxSelected

        elif (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            20 * data.height / 24 < event.y <= 22 * data.height / 24
        ):
            if data.updateFill == rgbString(160, 210, 219):
                currentTime = time.asctime(time.localtime(time.time()))
                data.status[1] = "Updated on " + str(currentTime)
                data.updateFill = rgbString(236, 246, 247)
                updateInputInfo(data)

    #### DIY MODE
    elif data.mode == "DIY":
        if (0 <= event.x < data.tabWidths) and (0 < event.y < data.tabHeight):
            resetBoxColor(data)
            data.mode = "Input Data"
        elif (2 * data.tabWidths <= event.x < 3 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "Random Trials"
        elif (3 * data.tabWidths <= event.x < 4 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "Single Trial"

        elif (5 * data.width / 12 < event.x <= 7 * data.width / 12) and (
            11 * data.height / 48 < event.y <= 13 * data.height / 48
        ):
            resetDIYTrialOdors(data)
            data.diyOdorDurationColor = data.boxSelected
            data.diyMode = "Odor Duration"
            ##Odor Duration

        elif (5 * data.width / 12 < event.x <= 7 * data.width / 12) and (
            18 * data.height / 48 < event.y < 20 * data.height / 48
        ):
            resetDIYTrialOdors(data)
            data.diyOdorDelayColor = data.boxSelected
            data.diyMode = "Odor Delay"
            ##Odor Delay Set

        elif (
            data.diyBoxesInput[0] == "white"
            or data.diyBoxesInput[0] == data.diyBoxChosen
        ):
            if (20 * data.width / 24 < event.x < 24 * data.width / 24) and (
                3 * data.height / 24 < event.y < 5 * data.height / 24
            ):
                if data.diyOdorOrder != []:
                    (
                        data.diyOdorOrder
                    ).pop()  # Removes the last element from the diyOdorOrder List
            if (data.width / 24 < event.x <= 3 * data.width / 24) and (
                16 * data.height / 32 < event.y <= 18 * data.height / 32
            ):
                resetDIYTrialOdors(data)
                data.diyBoxesInput[0] = data.diyBoxChosen
                data.diyOdorOrder.append(1)
                data.updateDIYMode = "No"

            if 1 < len(data.diyBoxesInput):
                if (
                    7 * data.width / 48 < event.x <= 11 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[1] = data.diyBoxChosen
                    data.diyOdorOrder.append(2)
                    data.updateDIYMode = "No"

            if 2 < len(data.diyBoxesInput):
                if (
                    12 * data.width / 48 < event.x <= 16 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[2] = data.diyBoxChosen
                    data.diyOdorOrder.append(3)
                    data.updateDIYMode = "No"

            if 3 < len(data.singleBoxesInput):
                if (
                    17 * data.width / 48 < event.x <= 21 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[3] = data.diyBoxChosen
                    data.diyOdorOrder.append(4)
                    data.updateDIYMode = "No"

            if 4 < len(data.singleBoxesInput):
                if (
                    22 * data.width / 48 < event.x <= 26 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[4] = data.diyBoxChosen
                    data.diyOdorOrder.append(5)
                    data.updateDIYMode = "No"

            if 5 < len(data.singleBoxesInput):
                if (
                    27 * data.width / 48 < event.x <= 31 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[5] = data.diyBoxChosen
                    data.diyOdorOrder.append(6)
                    data.updateDIYMode = "No"

            if 6 < len(data.singleBoxesInput):
                if (
                    32 * data.width / 48 < event.x <= 36 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[6] = data.diyBoxChosen
                    data.diyOdorOrder.append(7)
                    data.updateDIYMode = "No"

            if 7 < len(data.singleBoxesInput):
                if (
                    37 * data.width / 48 < event.x <= 41 * data.width / 48
                ) and (
                    16 * data.height / 32 < event.y <= 18 * data.height / 32
                ):
                    resetDIYTrialOdors(data)
                    data.diyBoxesInput[7] = data.diyBoxChosen
                    data.diyOdorOrder.append(8)
                    data.updateDIYMode = "No"

            if (14 * data.width / 24 < event.x <= 19 * data.width / 24) and (
                3 * data.height / 16 < event.y <= 4 * data.height / 16
            ):
                data.mode = "Single Trial"
                data.singleRepeatInput = data.singleBoxChosen

            if (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
                20 * data.height / 24 < event.y <= 22 * data.height / 24
            ):
                data.updateDIYMode = "Yes"
                currentTime = time.asctime(time.localtime(time.time()))
                data.diyStatus[1] = "Updated on " + str(currentTime)
                updateDIYMode(data)
        if (
            (data.updateDIYMode == "Yes")
            and (8 * data.width / 12 < event.x <= 11 * data.width / 12)
            and (17 * data.height / 24 < event.y <= 19 * data.height / 24)
        ):
            data.mode = "Execute"
            data.finishedOrder = "No"
            data.trigSignal = "no"

            runOrder(data)
            data.diyStatus[1] = "Finished Running Trials"
            data.updateDIYMode = "No"

            ##reset everything
            resetRunPy(data)
            resetBoxColor(data)
            data.mode = "Input Data"

    #### Randomize MODE

    elif data.mode == "Random Trials":
        if (0 <= event.x < data.tabWidths) and (0 < event.y < data.tabHeight):
            resetBoxColor(data)
            data.mode = "Input Data"
        elif (data.tabWidths <= event.x < 2 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "DIY"
        elif (3 * data.tabWidths <= event.x < 4 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "Single Trial"
        elif (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            20 * data.height / 24 < event.y <= 22 * data.height / 24
        ):
            randomize(data)
            data.randomMode = "Yes"
        elif (
            (data.randomMode == "Yes")
            and (8 * data.width / 12 < event.x <= 11 * data.width / 12)
            and (17 * data.height / 24 < event.y <= 19 * data.height / 24)
        ):
            data.mode = "Execute"
            data.finishedOrder = "No"
            data.trigSignal = "no"

            runOrder(data)
            data.executeStatus[1] = "Finished Running Trials"

            ##reset everything
            resetRunPy(data)
            resetBoxColor(data)
            data.mode = "Input Data"

    elif data.mode == "Single Trial":
        if (0 <= event.x < data.tabWidths) and (0 < event.y < data.tabHeight):
            resetBoxColor(data)
            data.mode = "Input Data"
        elif (data.tabWidths <= event.x < 2 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "DIY"
        elif (2 * data.tabWidths <= event.x < 3 * data.tabWidths) and (
            0 < event.y < data.tabHeight
        ):
            data.mode = "Random Trials"

        ##must do the same with this as with the other one
        elif (
            data.singleBoxesInput[0] == "white"
            or data.singleBoxesInput[0] == data.singleBoxChosen
        ):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                3 * data.height / 16 < event.y <= 4 * data.height / 16
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[0] = data.singleBoxChosen
                data.chosenSingleOdor = 1

        if 1 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                9 * data.height / 32 < event.y <= 11 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[1] = data.singleBoxChosen
                data.chosenSingleOdor = 2

        if 2 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                12 * data.height / 32 < event.y <= 14 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[2] = data.singleBoxChosen
                data.chosenSingleOdor = 3

        if 3 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                15 * data.height / 32 < event.y <= 17 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[3] = data.singleBoxChosen
                data.chosenSingleOdor = 4

        if 4 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                18 * data.height / 32 < event.y <= 20 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[4] = data.singleBoxChosen
                data.chosenSingleOdor = 5

        if 5 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                21 * data.height / 32 < event.y <= 23 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[5] = data.singleBoxChosen
                data.chosenSingleOdor = 6

        if 6 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                24 * data.height / 32 < event.y <= 26 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[6] = data.singleBoxChosen
                data.chosenSingleOdor = 7

        if 7 < len(data.singleBoxesInput):
            if (data.width / 24 < event.x <= 10 * data.width / 24) and (
                27 * data.height / 32 < event.y <= 29 * data.height / 32
            ):
                resetSingleTrialOdors(data)
                data.singleBoxesInput[7] = data.singleBoxChosen
                data.chosenSingleOdor = 8

        if (14 * data.width / 24 < event.x <= 19 * data.width / 24) and (
            3 * data.height / 16 < event.y <= 4 * data.height / 16
        ):
            data.mode = "Single Trial"
            data.singleRepeatInput = data.singleBoxChosen
        if (8 * data.width / 12 < event.x <= 11 * data.width / 12) and (
            20 * data.height / 24 < event.y <= 22 * data.height / 24
        ):
            data.updateSingleMode = "Yes"
            currentTime = time.asctime(time.localtime(time.time()))
            data.singleStatus[1] = "Updated on " + str(currentTime)
            updateSingleMode(data)
        if (
            (data.updateSingleMode == "Yes")
            and (8 * data.width / 12 < event.x <= 11 * data.width / 12)
            and (17 * data.height / 24 < event.y <= 19 * data.height / 24)
        ):
            data.mode = "Execute"
            data.finishedOrder = "No"
            data.trigSignal = "no"

            runOrder(data)
            data.singleStatus[1] = "Finished Running Trials"
            data.updateSingleMode = "No"

            ##reset everything
            resetRunPy(data)
            resetBoxColor(data)
            data.mode = "Input Data"


#############################
def keyPressed(event, data):
    #############################
    # use event.char, NOT event.keysym
    data.inputFileText = event.char
    data.newInput = event.keysym
    processInput(data)


##############################
# Draw Background
def drawBackground(canvas, data):
    if data.mode == "Input Data":
        # Set the background color
        canvas.create_rectangle(
            0,
            data.tabHeight,
            data.width,
            data.height,
            fill=data.tabColUnselected[0],
        )

        # create the tabs in order
        canvas.create_rectangle(
            0, 0, data.tabWidths, data.tabHeight, fill=data.tabColSelected[0]
        )
        canvas.create_text(
            data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[0],
            font=data.tabSpecs,
            fill="white",
        )

        canvas.create_rectangle(
            data.tabWidths,
            0,
            2 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[1],
        )
        canvas.create_text(
            3 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[1],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            2 * data.tabWidths,
            0,
            3 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[2],
        )
        canvas.create_text(
            5 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[2],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            3 * data.tabWidths,
            0,
            4 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[3],
        )
        canvas.create_text(
            7 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[3],
            font=data.tabSpecs,
        )

    ##DIY MODE
    elif data.mode == "DIY":
        canvas.create_rectangle(
            0,
            data.tabHeight,
            data.width,
            data.height,
            fill=data.tabColUnselected[1],
        )

        canvas.create_rectangle(
            0, 0, data.tabWidths, data.tabHeight, fill=data.tabColUnselected[0]
        )
        canvas.create_text(
            data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[0],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            data.tabWidths,
            0,
            2 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColSelected[1],
        )
        canvas.create_text(
            3 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[1],
            font=data.tabSpecs,
            fill="white",
        )

        canvas.create_rectangle(
            2 * data.tabWidths,
            0,
            3 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[2],
        )
        canvas.create_text(
            5 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[2],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            3 * data.tabWidths,
            0,
            4 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[3],
        )
        canvas.create_text(
            7 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[3],
            font=data.tabSpecs,
        )

    ##RANDOMIZE MODE
    elif data.mode == "Random Trials":
        canvas.create_rectangle(
            0,
            data.tabHeight,
            data.width,
            data.height,
            fill=data.tabColUnselected[2],
        )
        canvas.create_rectangle(
            0, 0, data.tabWidths, data.tabHeight, fill=data.tabColUnselected[0]
        )
        canvas.create_text(
            data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[0],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            data.tabWidths,
            0,
            2 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[1],
        )
        canvas.create_text(
            3 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[1],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            2 * data.tabWidths,
            0,
            3 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColSelected[2],
        )
        canvas.create_text(
            5 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[2],
            font=data.tabSpecs,
            fill="white",
        )

        canvas.create_rectangle(
            3 * data.tabWidths,
            0,
            4 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[3],
        )
        canvas.create_text(
            7 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[3],
            font=data.tabSpecs,
        )

    ##SINGLE TRIAL MODE
    elif data.mode == "Single Trial":
        canvas.create_rectangle(
            0,
            data.tabHeight,
            data.width,
            data.height,
            fill=data.tabColUnselected[3],
        )
        canvas.create_rectangle(
            0, 0, data.tabWidths, data.tabHeight, fill=data.tabColUnselected[0]
        )
        canvas.create_text(
            data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[0],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            data.tabWidths,
            0,
            2 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[1],
        )
        canvas.create_text(
            3 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[1],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            2 * data.tabWidths,
            0,
            3 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColUnselected[2],
        )
        canvas.create_text(
            5 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[2],
            font=data.tabSpecs,
        )

        canvas.create_rectangle(
            3 * data.tabWidths,
            0,
            4 * data.tabWidths,
            data.tabHeight,
            fill=data.tabColSelected[3],
        )
        canvas.create_text(
            7 * data.tabWidths / 2,
            data.tabHeight / 2,
            text=data.tabNames[3],
            font=data.tabSpecs,
            fill="white",
        )


############################
def drawInputTab(canvas, data):
    # #odors box:
    canvas.create_text(
        data.width / 12,
        3 * data.tabHeight / 2,
        text=data.labels[0],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        data.tabHeight + 10,
        5 * data.width / 12,
        data.tabHeight + data.odorLabelH + 10,
        fill=data.boxesInput[0],
    )
    canvas.create_text(
        7 * data.width / 24,
        data.tabHeight + data.odorLabelH,
        text=data.labelsValues[0],
        font=data.inputSpecs,
    )

    # #Trials box:
    canvas.create_text(
        7 * data.width / 12,
        3 * data.tabHeight / 2,
        text=data.labels[1],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        8 * data.width / 12,
        data.tabHeight + 10,
        11 * data.width / 12,
        data.tabHeight + data.odorLabelH + 10,
        fill=data.boxesInput[1],
    )
    canvas.create_text(
        19 * data.width / 24,
        data.tabHeight + data.odorLabelH,
        text=data.labelsValues[1],
        font=data.inputSpecs,
    )

    # Min Odor Time:
    canvas.create_text(
        data.width / 12,
        3 * data.tabHeight / 2 + 2 * data.odorLabelH,
        text=data.labels[2],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        data.tabHeight + 10 + 2 * data.odorLabelH,
        3 * data.width / 12,
        data.tabHeight + 3 * data.odorLabelH + 10,
        fill=data.boxesInput[2],
    )
    canvas.create_text(
        5 * data.width / 24,
        3 * data.tabHeight / 2 + 2 * data.odorLabelH,
        text=data.labelsValues[2],
        font=data.inputSpecs,
    )

    # Max Odor Time:
    canvas.create_text(
        4 * data.width / 12,
        3 * data.tabHeight / 2 + 2 * data.odorLabelH,
        text=data.labels[3],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        5 * data.width / 12,
        data.tabHeight + 10 + 2 * data.odorLabelH,
        6 * data.width / 12,
        data.tabHeight + 3 * data.odorLabelH + 10,
        fill=data.boxesInput[3],
    )
    canvas.create_text(
        11 * data.width / 24,
        3 * data.tabHeight / 2 + 2 * data.odorLabelH,
        text=data.labelsValues[3],
        font=data.inputSpecs,
    )

    # Delay Between Odors:
    canvas.create_text(
        15 * data.width / 24,
        3 * data.tabHeight / 2 + 2 * data.odorLabelH,
        text=data.labels[4],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        9 * data.width / 12,
        data.tabHeight + 10 + 2 * data.odorLabelH,
        10 * data.width / 12,
        data.tabHeight + 3 * data.odorLabelH + 10,
        fill=data.boxesInput[4],
    )
    canvas.create_text(
        19 * data.width / 24,
        3 * data.tabHeight / 2 + 2 * data.odorLabelH,
        text=data.labelsValues[4],
        font=data.inputSpecs,
    )

    # Odor 1
    canvas.create_text(
        data.width / 12,
        15 * data.height / 48,
        text=data.odorLabels[0],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        7 * data.height / 24,
        5 * data.width / 12,
        8 * data.height / 24,
        fill=data.odorsBoxesInput[0],
    )
    canvas.create_text(
        7 * data.width / 24,
        15 * data.height / 48,
        text=data.odorNames[0],
        font=data.inputSpecs,
    )

    # Odor 2
    canvas.create_text(
        7 * data.width / 12,
        15 * data.height / 48,
        text=data.odorLabels[1],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        8 * data.width / 12,
        7 * data.height / 24,
        11 * data.width / 12,
        8 * data.height / 24,
        fill=data.odorsBoxesInput[1],
    )
    canvas.create_text(
        19 * data.width / 24,
        15 * data.height / 48,
        text=data.odorNames[1],
        font=data.inputSpecs,
    )

    # Odor 3
    canvas.create_text(
        data.width / 12,
        19 * data.height / 48,
        text=data.odorLabels[2],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        9 * data.height / 24,
        5 * data.width / 12,
        10 * data.height / 24,
        fill=data.odorsBoxesInput[2],
    )
    canvas.create_text(
        7 * data.width / 24,
        19 * data.height / 48,
        text=data.odorNames[2],
        font=data.inputSpecs,
    )

    # Odor 4
    canvas.create_text(
        7 * data.width / 12,
        19 * data.height / 48,
        text=data.odorLabels[3],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        8 * data.width / 12,
        9 * data.height / 24,
        11 * data.width / 12,
        10 * data.height / 24,
        fill=data.odorsBoxesInput[3],
    )
    canvas.create_text(
        19 * data.width / 24,
        19 * data.height / 48,
        text=data.odorNames[3],
        font=data.inputSpecs,
    )

    # Odor 5
    canvas.create_text(
        data.width / 12,
        23 * data.height / 48,
        text=data.odorLabels[4],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        11 * data.height / 24,
        5 * data.width / 12,
        12 * data.height / 24,
        fill=data.odorsBoxesInput[4],
    )
    canvas.create_text(
        7 * data.width / 24,
        23 * data.height / 48,
        text=data.odorNames[4],
        font=data.inputSpecs,
    )

    # Odor 6
    canvas.create_text(
        7 * data.width / 12,
        23 * data.height / 48,
        text=data.odorLabels[5],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        8 * data.width / 12,
        11 * data.height / 24,
        11 * data.width / 12,
        12 * data.height / 24,
        fill=data.odorsBoxesInput[5],
    )
    canvas.create_text(
        19 * data.width / 24,
        23 * data.height / 48,
        text=data.odorNames[5],
        font=data.inputSpecs,
    )

    # Odor 7
    canvas.create_text(
        data.width / 12,
        27 * data.height / 48,
        text=data.odorLabels[6],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        13 * data.height / 24,
        5 * data.width / 12,
        14 * data.height / 24,
        fill=data.odorsBoxesInput[6],
    )
    canvas.create_text(
        7 * data.width / 24,
        27 * data.height / 48,
        text=data.odorNames[6],
        font=data.inputSpecs,
    )

    # Odor 8
    canvas.create_text(
        7 * data.width / 12,
        27 * data.height / 48,
        text=data.odorLabels[7],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        8 * data.width / 12,
        13 * data.height / 24,
        11 * data.width / 12,
        14 * data.height / 24,
        fill=data.odorsBoxesInput[7],
    )
    canvas.create_text(
        19 * data.width / 24,
        27 * data.height / 48,
        text=data.odorNames[7],
        font=data.inputSpecs,
    )

    # File Name
    canvas.create_text(
        data.width / 12,
        31 * data.height / 48,
        text=data.fileName[0],
        font=data.inputSpecs,
    )
    canvas.create_rectangle(
        2 * data.width / 12,
        15 * data.height / 24,
        5 * data.width / 12,
        16 * data.height / 24,
        fill=data.fileNameBoxColor,
    )
    canvas.create_text(
        7 * data.width / 24,
        31 * data.height / 48,
        text=data.fileName[1],
        font=data.inputSpecs,
    )

    # Update Box
    canvas.create_rectangle(
        8 * data.width / 12,
        20 * data.height / 24,
        11 * data.width / 12,
        22 * data.height / 24,
        fill=data.updateFill,
    )
    canvas.create_text(
        19 * data.width / 24,
        42 * data.height / 48,
        text=data.updateName,
        font="Helvetica 16 bold",
    )

    # Status Update
    canvas.create_text(
        7 * data.width / 24,
        42 * data.height / 48,
        text=(data.status[0] + data.status[1]),
        font="Helvetica 16 bold",
    )


def drawDIYOdorOrder(canvas, data):
    assignOdorNames(data)
    if (
        data.diyBoxesInput[0] == "white"
        or data.diyBoxesInput[0] == data.diyBoxChosen
    ):
        canvas.create_rectangle(
            data.width / 24,
            16 * data.height / 32,
            3 * data.width / 24,
            18 * data.height / 32,
            fill=data.diyBoxesInput[0],
        )
        canvas.create_text(
            2 * data.width / 24,
            17 * data.height / 32,
            text=data.singleLabelsValues[0],
            font=data.inputSpecs,
        )

    if 1 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            7 * data.width / 48,
            16 * data.height / 32,
            11 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[1],
        )
        canvas.create_text(
            9 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[1],
            font=data.inputSpecs,
        )

    if 2 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            12 * data.width / 48,
            16 * data.height / 32,
            16 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[2],
        )
        canvas.create_text(
            14 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[2],
            font=data.inputSpecs,
        )

    if 3 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            17 * data.width / 48,
            16 * data.height / 32,
            21 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[3],
        )
        canvas.create_text(
            19 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[3],
            font=data.inputSpecs,
        )

    if 4 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            22 * data.width / 48,
            16 * data.height / 32,
            26 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[4],
        )
        canvas.create_text(
            24 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[4],
            font=data.inputSpecs,
        )

    if 5 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            27 * data.width / 48,
            16 * data.height / 32,
            31 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[5],
        )
        canvas.create_text(
            29 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[5],
            font=data.inputSpecs,
        )

    if 6 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            32 * data.width / 48,
            16 * data.height / 32,
            36 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[6],
        )
        canvas.create_text(
            34 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[6],
            font=data.inputSpecs,
        )

    if 7 < len(data.diyBoxesInput):
        canvas.create_rectangle(
            37 * data.width / 48,
            16 * data.height / 32,
            41 * data.width / 48,
            18 * data.height / 32,
            fill=data.diyBoxesInput[7],
        )
        canvas.create_text(
            39 * data.width / 48,
            17 * data.height / 32,
            text=data.singleLabelsValues[7],
            font=data.inputSpecs,
        )


def drawDIYOdorDuration(canvas, data):
    canvas.create_rectangle(
        5 * data.width / 12,
        11 * data.height / 48,
        7 * data.width / 12,
        13 * data.height / 48,
        fill=data.diyOdorDurationColor,
    )
    canvas.create_text(
        data.width / 2,
        12 * data.height / 48,
        text=data.diyOdorDuration,
        font="Helvetica 14",
    )


def drawDIYOdorDelay(canvas, data):
    canvas.create_rectangle(
        5 * data.width / 12,
        18 * data.height / 48,
        7 * data.width / 12,
        20 * data.height / 48,
        fill=data.diyOdorDelayColor,
    )
    canvas.create_text(
        data.width / 2,
        19 * data.height / 48,
        text=data.diyOdorDelay,
        font="Helvetica 14",
    )


def drawDIYBoxes(canvas, data):
    # Choose Odor Text
    canvas.create_text(
        3 * data.width / 24,
        23 * data.height / 48,
        text=data.diyChooseOdorsLabels[0],
        font="Helvetica 16 bold",
    )

    canvas.create_text(
        3 * data.width / 24,
        9 * data.height / 48,
        text=data.diyChooseOdorsLabels[1],
        font="Helvetica 16 bold",
    )

    canvas.create_text(
        3 * data.width / 24,
        16 * data.height / 48,
        text=data.diyChooseOdorsLabels[2],
        font="Helvetica 16 bold",
    )

    # Draw updates for DIY screen
    canvas.create_text(
        3 * data.width / 24,
        30 * data.height / 48,
        text=data.diyOdorLists[0],
        font="Helvetica 16 bold",
    )
    canvas.create_text(
        12 * data.width / 24,
        32 * data.height / 48,
        text=data.diyOdorOrder,
        font="Helvetica 14 bold",
    )

    canvas.create_text(
        3 * data.width / 24,
        44 * data.height / 48,
        text=data.diyStatus[0],
        font="Helvetica 14 bold",
    )
    canvas.create_text(
        10 * data.width / 24,
        44 * data.height / 48,
        text=data.diyStatus[1],
        font="Helvetica 14 bold",
    )


def drawDIYTab(canvas, data):
    if data.numSolenoids == 0:
        canvas.create_text(
            data.width / 2,
            data.height / 2,
            text="Please input your data in the Input Data Tab",
            font="Helvetica 16 bold",
        )
    else:
        # Draw Undo button
        canvas.create_rectangle(
            20 * data.width / 24,
            3 * data.height / 24,
            24 * data.width / 24,
            5 * data.height / 24,
            fill=data.diyUndoFill,
        )
        canvas.create_text(
            22 * data.width / 24,
            8 * data.height / 48,
            text="Undo Selection",
            font="Helvetica 16 bold",
        )

        # Draw Update button
        canvas.create_rectangle(
            8 * data.width / 12,
            20 * data.height / 24,
            11 * data.width / 12,
            22 * data.height / 24,
            fill=data.DIYupdateFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            42 * data.height / 48,
            text=data.DIYupdateName,
            font="Helvetica 16 bold",
        )

        # Draw Execute button
        canvas.create_rectangle(
            8 * data.width / 12,
            17 * data.height / 24,
            11 * data.width / 12,
            19 * data.height / 24,
            fill=data.executeFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            36 * data.height / 48,
            text=data.executeName,
            font="Helvetica 16 bold",
        )

        # Draw "Choose Odor" Options
        drawDIYBoxes(canvas, data)
        drawDIYOdorOrder(canvas, data)
        drawDIYOdorDuration(canvas, data)
        drawDIYOdorDelay(canvas, data)


def drawRandomizeTab(canvas, data):
    if data.randomMode == "No":
        canvas.create_rectangle(
            8 * data.width / 12,
            20 * data.height / 24,
            11 * data.width / 12,
            22 * data.height / 24,
            fill=data.randomizeFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            42 * data.height / 48,
            text=data.randomizeName,
            font="Helvetica 16 bold",
        )
        canvas.create_text(
            data.width / 2,
            data.height / 2,
            text=data.randomizeStatus[0] + data.randomizeStatus[1],
            font="Helvetica 14 bold",
        )

    elif data.randomMode == "Yes":
        canvas.create_rectangle(
            8 * data.width / 12,
            20 * data.height / 24,
            11 * data.width / 12,
            22 * data.height / 24,
            fill=data.randomizeFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            42 * data.height / 48,
            text=data.randomizeName,
            font="Helvetica 16 bold",
        )

        # Create solenoid order section
        canvas.create_text(
            data.width / 4,
            2 * data.height / 10,
            text=data.randomizeTrialLabels[0],
            font="Helvetica 14 bold",
        )
        canvas.create_text(
            data.width / 2,
            3 * data.height / 10,
            text=str(data.solenoidOrder),
            font="Helvetica 14",
        )

        canvas.create_text(
            data.width / 4,
            4 * data.height / 10,
            text=data.randomizeTrialLabels[1],
            font="Helvetica 14 bold",
        )

        canvas.create_text(
            data.width / 2,
            5 * data.height / 10,
            text=str(data.odorTime),
            font="Helvetica 14",
        )

        canvas.create_text(
            data.width / 4,
            6 * data.height / 10,
            text=data.randomizeTrialLabels[2],
            font="Helvetica 14 bold",
        )

        canvas.create_text(
            data.width / 2,
            7 * data.height / 10,
            text=str(data.delayTime),
            font="Helvetica 14",
        )

        canvas.create_rectangle(
            8 * data.width / 12,
            17 * data.height / 24,
            11 * data.width / 12,
            19 * data.height / 24,
            fill=data.executeFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            35 * data.height / 48,
            text=data.executeName,
            font="Helvetica 16 bold",
        )


def drawExecuteTab(canvas, data):
    canvas.create_rectangle(
        0, data.tabHeight, data.width, data.height, fill=data.executeFill
    )
    canvas.create_text(
        data.width / 2,
        data.height / 2,
        text=data.executeStatus[0] + data.executeStatus[1],
        font="Helvetica 16 bold",
    )


def drawSingleTab(canvas, data):
    if data.numSolenoids == 0:
        canvas.create_text(
            data.width / 2,
            data.height / 2,
            text="Please input your data in the Input Data Tab",
            font="Helvetica 16 bold",
        )
    else:
        assignOdorNames(data)
        # For the execute button
        canvas.create_rectangle(
            8 * data.width / 12,
            17 * data.height / 24,
            11 * data.width / 12,
            19 * data.height / 24,
            fill=data.executeFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            35 * data.height / 48,
            text=data.executeName,
            font="Helvetica 16 bold",
        )
        canvas.create_text(
            2 * data.width / 12,
            3 * data.tabHeight / 2,
            text=data.singleLabels[0],
            font=data.inputSpecs,
        )

        # For the number of repeats box
        canvas.create_text(
            8 * data.width / 12,
            3 * data.tabHeight / 2,
            text=data.singleLabels[1],
            font=data.inputSpecs,
        )
        canvas.create_rectangle(
            14 * data.width / 24,
            3 * data.height / 16,
            19 * data.width / 24,
            4 * data.height / 16,
            fill=data.singleRepeatInput,
        )
        canvas.create_text(
            33 * data.width / 48,
            7 * data.height / 32,
            text=data.singleRepeatValue,
            font=data.inputSpecs,
        )

        # For the status
        canvas.create_text(
            6 * data.width / 12,
            16 * data.height / 24,
            text=data.singleStatus[0],
            font="Helvetica 14 bold",
        )
        canvas.create_text(
            9 * data.width / 12,
            16 * data.height / 24,
            text=data.singleStatus[1],
            font="Helvetica 14 bold",
        )

        # For the solenoid order and times:
        canvas.create_text(
            6 * data.width / 12,
            9 * data.height / 32,
            text="Odor Order",
            font="Helvetica 12 bold",
        )
        canvas.create_text(
            9 * data.width / 12,
            10 * data.height / 32,
            text=str(data.solenoidOrder),
            font="Helvetica 12",
        )

        canvas.create_text(
            6 * data.width / 12,
            11 * data.height / 32,
            text="Odor Duration",
            font="Helvetica 12 bold",
        )
        canvas.create_text(
            9 * data.width / 12,
            12 * data.height / 32,
            text=str(data.odorTime),
            font="Helvetica 12",
        )

        canvas.create_text(
            7 * data.width / 12,
            13 * data.height / 32,
            text="Delay Between Trials",
            font="Helvetica 12 bold",
        )
        canvas.create_text(
            9 * data.width / 12,
            14 * data.height / 32,
            text=str(data.delayTime),
            font="Helvetica 12",
        )

        # For the update button
        canvas.create_rectangle(
            8 * data.width / 12,
            20 * data.height / 24,
            11 * data.width / 12,
            22 * data.height / 24,
            fill=data.randomizeFill,
        )
        canvas.create_text(
            19 * data.width / 24,
            42 * data.height / 48,
            text=data.updateSingleName,
            font="Helvetica 16 bold",
        )

        if (
            data.singleBoxesInput[0] == "white"
            or data.singleBoxesInput[0] == data.singleBoxChosen
        ):
            canvas.create_rectangle(
                data.width / 24,
                3 * data.height / 16,
                10 * data.width / 24,
                4 * data.height / 16,
                fill=data.singleBoxesInput[0],
            )
            canvas.create_text(
                5 * data.width / 24,
                7 * data.height / 32,
                text=data.singleLabelsValues[0],
                font=data.inputSpecs,
            )

        if 1 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                9 * data.height / 32,
                10 * data.width / 24,
                11 * data.height / 32,
                fill=data.singleBoxesInput[1],
            )
            canvas.create_text(
                5 * data.width / 24,
                10 * data.height / 32,
                text=data.singleLabelsValues[1],
                font=data.inputSpecs,
            )

        if 2 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                12 * data.height / 32,
                10 * data.width / 24,
                14 * data.height / 32,
                fill=data.singleBoxesInput[2],
            )
            canvas.create_text(
                5 * data.width / 24,
                13 * data.height / 32,
                text=data.singleLabelsValues[2],
                font=data.inputSpecs,
            )

        if 3 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                15 * data.height / 32,
                10 * data.width / 24,
                17 * data.height / 32,
                fill=data.singleBoxesInput[3],
            )
            canvas.create_text(
                5 * data.width / 24,
                16 * data.height / 32,
                text=data.singleLabelsValues[3],
                font=data.inputSpecs,
            )

        if 4 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                18 * data.height / 32,
                10 * data.width / 24,
                20 * data.height / 32,
                fill=data.singleBoxesInput[4],
            )
            canvas.create_text(
                5 * data.width / 24,
                19 * data.height / 32,
                text=data.singleLabelsValues[4],
                font=data.inputSpecs,
            )

        if 5 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                21 * data.height / 32,
                10 * data.width / 24,
                23 * data.height / 32,
                fill=data.singleBoxesInput[5],
            )
            canvas.create_text(
                5 * data.width / 24,
                22 * data.height / 32,
                text=data.singleLabelsValues[5],
                font=data.inputSpecs,
            )

        if 6 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                24 * data.height / 32,
                10 * data.width / 24,
                26 * data.height / 32,
                fill=data.singleBoxesInput[6],
            )
            canvas.create_text(
                5 * data.width / 24,
                25 * data.height / 32,
                text=data.singleLabelsValues[6],
                font=data.inputSpecs,
            )

        if 7 < len(data.singleBoxesInput):
            canvas.create_rectangle(
                data.width / 24,
                27 * data.height / 32,
                10 * data.width / 24,
                29 * data.height / 32,
                fill=data.singleBoxesInput[7],
            )
            canvas.create_text(
                5 * data.width / 24,
                28 * data.height / 32,
                text=data.singleLabelsValues[7],
                font=data.inputSpecs,
            )


############################
def redrawAll(canvas, data):
    ############################
    drawBackground(canvas, data)
    if data.mode == "Input Data":
        drawInputTab(canvas, data)
    elif data.mode == "Random Trials":
        drawRandomizeTab(canvas, data)
    elif data.mode == "Execute":
        drawExecuteTab(canvas, data)
    elif data.mode == "Single Trial":
        drawSingleTab(canvas, data)
    elif data.mode == "DIY":
        drawDIYTab(canvas, data)


####################################
# use the run function as-is
####################################


def run(width=300, height=300):
    def redrawAllWrapper(canvas, data):
        canvas.delete(ALL)
        canvas.create_rectangle(
            0, 0, data.width, data.height, fill="white", width=0
        )
        redrawAll(canvas, data)
        canvas.update()

    def mousePressedWrapper(event, canvas, data):
        mousePressed(event, data)
        redrawAllWrapper(canvas, data)

    def keyPressedWrapper(event, canvas, data):
        keyPressed(event, data)
        redrawAllWrapper(canvas, data)

    # Set up data and call init
    class Struct(object):
        pass

    data = Struct()
    data.width = width
    data.height = height
    root = Tk()
    init(data)
    # create the root and the canvas
    canvas = Canvas(root, width=data.width, height=data.height)
    canvas.pack()
    # set up events
    root.bind(
        "<Button-1>", lambda event: mousePressedWrapper(event, canvas, data)
    )
    root.bind("<Key>", lambda event: keyPressedWrapper(event, canvas, data))
    redrawAll(canvas, data)
    # and launch the app
    root.mainloop()  # blocks until window is closed
    print("bye!")


run(900, 600)
