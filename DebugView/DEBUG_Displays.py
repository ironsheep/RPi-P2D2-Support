#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import _thread
from datetime import datetime
from time import time, sleep, localtime, strftime
import os
import subprocess
import sys
import os.path
import argparse
from collections import deque
from unidecode import unidecode
from colorama import init as colorama_init
from colorama import Fore, Back, Style
import serial
from time import sleep
import PySimpleGUI as sg

from signal import signal, SIGPIPE, SIG_DFL
signal(SIGPIPE,SIG_DFL)

script_version = "0.0.1"
script_name = 'vw_debug.py'
script_info = '{} v{}'.format(script_name, script_version)
project_name = 'DEBUG_'
project_url = 'https://github.com/ironsheep/RPi-P2D2-Support'

if False:
    # will be caught by python 2.7 to be illegal syntax
    print_line('Sorry, this script requires a python3 runtime environment.', file=sys.stderr)
    os._exit(1)

sg.theme('GreenMono')

# Logging function
def print_line(text, error=False, warning=False, info=False, verbose=False, debug=False, console=True):
    timestamp = strftime('%Y-%m-%d %H:%M:%S', localtime())
    if console:
        if error:
            print(Fore.RED + Style.BRIGHT + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL, file=sys.stderr)
        elif warning:
            print(Fore.YELLOW + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)
        elif info or verbose:
            if opt_verbose:
                # verbose...
                print(Fore.GREEN + '[{}] '.format(timestamp) + Fore.YELLOW  + '- ' + '{}'.format(text) + Style.RESET_ALL)
            else:
                # info...
                print(Fore.MAGENTA + '[{}] '.format(timestamp) + Fore.YELLOW  + '- ' + '{}'.format(text) + Style.RESET_ALL)
        elif debug:
            if opt_debug:
                print(Fore.CYAN + '[{}] '.format(timestamp) + '- (DBG): ' + '{}'.format(text) + Style.RESET_ALL)
        else:
            print(Fore.GREEN + '[{}] '.format(timestamp) + Style.RESET_ALL + '{}'.format(text) + Style.RESET_ALL)

# Argparse
opt_debug = False
opt_verbose = False
opt_useTestFile = False

# Argparse
parser = argparse.ArgumentParser(description=project_name, epilog='For further details see: ' + project_url)
parser.add_argument("-v", "--verbose", help="increase output verbosity", action="store_true")
parser.add_argument("-d", "--debug", help="show debug output", action="store_true")
parser.add_argument("-t", "--test", help="run from canned test file", action="store_true")
parse_args = parser.parse_args()

opt_debug = parse_args.debug
opt_verbose = parse_args.verbose
opt_useTestFile = parse_args.test

print_line(script_info, info=True)
if opt_verbose:
    print_line('Verbose enabled', info=True)
if opt_debug:
    print_line('Debug enabled', debug=True)
if opt_useTestFile:
    print_line('TEST: debug stream is test file', debug=True)


lineBuffer = deque()

def pushLine(newLine):
    lineBuffer.append(newLine)

def popLine():
    global lineBuffer
    oldestLine = ''
    if len(lineBuffer) > 0:
        oldestLine = lineBuffer.popleft()
    return oldestLine


def processInput():
    print_line('Thread: processInput() started', verbose=True)
    # process lies from serial or from test file
    if opt_useTestFile == True:
        test_file=open("charlie_rpi_debug.out", "r")
        lines = test_file.readlines()
        for currLine in lines:
            pushLine(currLine)
            sleep(0.25)
    else:
        ser = serial.Serial ("/dev/serial0", 2000000, timeout=1)    #Open port with baud rate & timeout
        while True:
            received_data = ser.readline()              #read serial port
            currLine = received_data.decode('utf-8').rstrip()
            if len(currLine) > 0:
                pushLine(currLine)

namedWindows = {}
debugViewsShowing = False


def addNamedWindow(name, window):
    global namedWindows
    if existsNamedWindow(name) == False:
        namedWindows[name] = window
    else:
        print_line('NAME {} already in windows list, SKIPPED!'.format(name), error=True)

def existsNamedWindow(name):
    foundStatus = True
    if getNamedWindow(name) == '':
        foundStatus = False
    return foundStatus

def getNamedWindow(name):
    return namedWindows.get(name, '')

kTypeString = 'string'
kTypeInteger = 'int'
kTypeColor = 'color'

valTableTerm = [
    ( 'TITLE', kTypeString ),
    ( 'POS', kTypeInteger, kTypeInteger ),
    ( 'SIZE', kTypeInteger, kTypeInteger ),
    ( 'TEXTSIZE', kTypeInteger ),
    ( 'TEXTCOLOR', kTypeColor, kTypeColor ),
    ( 'BACKCOLOR', kTypeColor ),
    ( 'UPDATE' ),
]

def getValidationTuple(table, parameterName):
    print_line('table=[{}], parameterName=[{}]'.format('tbl-??', parameterName), debug=True)
    desiredValTuple = ''
    validStatus = False
    searchTerm = parameterName.lower()
    for tupleIndex in range(len(table)):
        currTuple = table[tupleIndex]
        keyword = currTuple[0].lower()
        if keyword == searchTerm:
            desiredValTuple = currTuple
            validStatus = True
            break;

    print_line('-> tuple=[{}], valid={}'.format(desiredValTuple, validStatus), debug=True)
    return desiredValTuple, validStatus

def intForColorString(colorString):
    return

def interpretArgument(argument, validationType):
    print_line('argument=[{}], validationType=[{}]'.format(argument, validationType), debug=True)
    interpValue = ''
    validStatus = True
    if validationType == kTypeString:
        interpValue = argument
    elif validationType == kTypeInteger:
        interpValue = int(argument)
    elif validationType == kTypeColor:
        interpValue = intForColorString(argument)
    else:
        print_line('ERROR: Unknown validation Type=[{}]'.format(validationType), error=True)
        validStatus = False

    print_line('-> interpValue=[{}], valid={}'.format(interpValue, validStatus), debug=True)
    return interpValue, validStatus

def parseOptions(lineParts, valTable, skip=0):
    # process line parts into tuples
    #  returning (tuples, valid flag)
    optionTuples = []
    validStatus = True
    maxParts = len(lineParts)
    currIndex = skip
    while currIndex < maxParts:
        validationTuple, valid = getValidationTuple(valTable, lineParts[currIndex])
        fieldValues = []
        if valid == False:
            validStatus = False
            break
        else:
            # now gather needed values into list then into new tuple
            fieldValues.append(lineParts[currIndex])
            if len(validationTuple) > 1:
                for fieldIndex in range(len(validationTuple) - 1):
                    currIndex += 1
                    parsedValue, valid = interpretArgument(lineParts[currIndex], validationTuple[fieldIndex+1])
                    if valid == True:
                        fieldValues.append(parsedValue)
                    else:
                        validStatus = False
                        break;
                if validStatus == False:
                    break

            currIndex += 1  # point past only/final value
            optionTuples.append(tuple(fieldValues))

    print_line('-> tuples=[{}], valid={}'.format(optionTuples, validStatus), debug=True)
    return optionTuples, validStatus


def opCreateTermWindow(cmdString):
    """
    ---------------------------------------------------------------------------------------
    TERM config:	TITLE 'Title String'		'override default caption
                    POS screen_x screen_y		'default is 0 0
                    SIZE columns rows		'default is 80 25
                    TEXTSIZE text_size_6_to_200	'default is current text editor size
                    TEXTCOLOR text0 back0 ...	'define text and back colors for settings 0..3
                    BACKCOLOR color_rrggbb		'set background color
                    UPDATE				'set 'update' mode

		feed:	0 = Clear			'control characters
                1 = Home
                2 = Set colum, column follows
                3 = Set row, row follows
                4 = Set color 0
                5 = Set color 1
                6 = Set color 2
                7 = Set color 3
                8 = Backspace			'printable characters
                9 = Tab
                13 = New line
                >31 = chr
                'string'			'print string
                CLEAR				'clear display
                UPDATE				'update display (only needed in 'update' mode)
                SAVE 'filename'			'save display as filename.bmp
                CLOSE				'close display, frees name

    ---------------------------------------------------------------------------------------
    """
    print_line('opCreateWindow({})'.format(cmdString), debug=True)
    lineParts = cmdString.split()
    if len(lineParts) > 2 and lineParts[1] == '`term':
        newWindowName = lineParts[2]
        print_line('newWindowName=[{}]'.format(newWindowName), debug=True)
        # create the desired window
        # EXAMPLE:
        #   Cog0  `term temp size 80 16 textsize 10
        settingsTuples, valid = parseOptions(lineParts, valTableTerm, skip=3)
        if valid == True:
            # configure the window
            windowTitle = '{} TERM'.format(newWindowName)
            windowWidth = 80
            windowHeight = 25
            windowX = 0
            windowY = 0
            fontSize = 10
            for tupleIndex in range(len(settingsTuples)):
                currOption = settingsTuples[tupleIndex]
                if currOption[0].upper() == 'SIZE':
                    windowWidth = currOption[1]
                    windowHeight = currOption[2]
                elif currOption[0].upper() == 'TEXTSIZE':
                    fontSize = currOption[1]

            # create our TERM window
            layout = [ [sg.Multiline(size=(windowWidth, windowHeight), autoscroll=True, key=DEBUG_MULTILINE_KEY)] ]
            window = sg.Window(title=windowTitle, layout=layout, location=(windowX, windowY), finalize=True)

            # remember the window
            addNamedWindow(newWindowName, window)
        else:
            os._exit(1) # PARSE FAIL exit!!!

    else:
        print_line('BAD Window Create command [{}]'.format(cmdString), error=True)
        os._exit(1) # PARSE FAIL exit!!!

def opJustLogIt(cmdString):
    print_line('opJustLogIt({})'.format(cmdString), debug=True)

def filterThenWrite(rawValue, targetWindow):
    filteredValue = rawValue
    targetWindow[DEBUG_MULTILINE_KEY].update(filteredValue, append=True)

def opSendToWindow(cmdString):
    lineParts = cmdString.split()
    print_line('opSendToWindow(window=[{}], value=[{}])'.format(lineParts[1], cmdString), debug=True)
    # EXAMPLE:
    #   Cog0  `temp 'Xpin=24, Ypin=25' 13
    linePrefix = '{} {} '.format(lineParts[0], lineParts[1])
    lineWoPrefix = cmdString.replace(linePrefix,'')
    targetWindowName = lineParts[1].replace("`", '')
    if existsNamedWindow(targetWindowName):
        targetWindow = getNamedWindow(targetWindowName)
        filterThenWrite(lineWoPrefix, targetWindow)


def functionForCommand(opId):
    table = {
        "`term" : opCreateTermWindow,
        "INIT" : opJustLogIt,
    }
    # get() method of dictionary data type returns
    # value of passed argument if it is present
    # in dictionary otherwise second argument will
    # be assigned as default value of passed argument
    return table.get(opId, opSendToWindow)



DEBUG_MULTILINE_KEY = '-OUTPUT-'+sg.WRITE_ONLY_KEY
debugLogWindow = ''
defaultTextColor = 'green'

def debugLogClear():
    debugLogWindow[DEBUG_MULTILINE_KEY].update('')

def debugLogPrint(text, color=defaultTextColor, bgColor=''):
    if color == '' and bgColor == '':
        debugLogWindow[DEBUG_MULTILINE_KEY].update(text, append=True)
    elif color != '' and bgColor == '':
        debugLogWindow[DEBUG_MULTILINE_KEY].update(text, text_color_for_value=color, append=True)
    elif color == '' and bgColor != '':
        debugLogWindow[DEBUG_MULTILINE_KEY].update(text, background_color_for_value=bgColor, append=True)
    else:
        debugLogWindow[DEBUG_MULTILINE_KEY].update(text, text_color_for_value=color, background_color_for_value=bgColor, append=True)

def SetUpDebugLogWindow():
    global debugViewsShowing
    global debugLogWindow
    debugViewsShowing = True
    # create our default log display window
    layout = [ [sg.Multiline(size=(80,24), autoscroll=True, key=DEBUG_MULTILINE_KEY)],
               [sg.Button('Clear'), sg.Button('Exit')]  ]

    window = sg.Window('DEBUG Output', layout, finalize=True)
    debugLogWindow = window

def processDebugLine(debug_text):
    # if our debug output log window not showing show it
    if debugViewsShowing == False:
        SetUpDebugLogWindow()
        debugLogClear()

    #
    # EXAMPLES:
    # Cog0  INIT $0000_0000 $0000_0000 load
    # Cog0  INIT $0000_0D58 $0000_1248 jump
    # Cog0  `term temp size 80 16 textsize 10
    # Cog0  `temp 'Xpin=24, Ypin=25' 13
    lineParts = debug_text.split()

        #  process a line of P2 DEBUG output
    textColor = defaultTextColor
    if lineParts[1] == 'INIT':
        textColor = 'blue'
    debugLogPrint(debug_text, color=textColor)

    if len(lineParts) > 1:
        # [0] is cog ID
        # [1] is directive or routing ID (window name)
        operation = functionForCommand(lineParts[1])
        operation(debug_text)

kWindowReadTimeoutIn_mSec = 10
def mainLoop():
    while True:             # Event Loop
        if debugViewsShowing == True:
            event, values = debugLogWindow.read(timeout=kWindowReadTimeoutIn_mSec)
            print(event, values)
            if event in (sg.WIN_CLOSED, 'Exit'):
                break
            if event == 'Clear':
                debugLogWindow[DEBUG_MULTILINE_KEY].update('')
        # process an incoming line - creates our windows as needed
        currLine = popLine();
        if len(currLine) > 0:
            processDebugLine(currLine)

    debugLogWindow.close()
    print_line('Debug Window EXIT', debug=True)


_thread.start_new_thread(processInput, ( ))

try:
    mainLoop()

finally:
    # normal shutdown
    debugLogWindow.close()
    print_line('Done', info=True)