#######################################
# Imports
#######################################
from flask import Flask
from flask import render_template
from flask import request
from flask import make_response
from operator import itemgetter
import json
import os

######################################
'''Compiler code'''
import time
import subprocess

class code(object):
    def __init__(self, syntax = 'python', tempDir = '', code = [], tempfile = '', executed_yet = False, output = []):
        self.syntax = syntax # Not used now, but specifies predefined language
        self.tempDir = tempDir # Specifies the temporary directory to store the temporary file in
        self.code = code # python code should be in a line-divided list
        self.tempfile = tempfile # Specifies the temporary file path
        self.executed_yet = executed_yet # Defines if the code has been executed, default = false, when code executed is set to True
        self.output = output # Output of the code through the sub-process module
    def createTemp(self): # Creates the temporary file
        self.tempfile = str(time.time()) # Generate file name based on current time (Epoch time)
        f = open(self.tempDir + self.tempfile, 'w+') # Creates the temporary file
        f.close() # Close the temporary file
    def writeTemp(self): # Writes code to the temporary file
        f = open(self.tempDir + self.tempfile, 'w') # Opens the temporary file
        f.writelines(self.code) # Writes all lines of the code to the file
        f.close() # Closes the file
    def execute(self):
            p = subprocess.Popen(['python', self.tempDir + self.tempfile], stdout = subprocess.PIPE, stderr = subprocess.PIPE) # Executes the actual code stored in the temporary file
            out, err = p.communicate() # Gets output & errors
            os.remove(self.tempDir + self.tempfile) # Removes the temporary file
            output = str(out) # Converts the output into a string
            return output, err # Returns any errors or output

def executor(code_data):
    c = code(tempDir='./', code=code_data)
    c.createTemp() # Generate temporary file for execution
    c.writeTemp() # Write to the temporary file
    output, err = c.execute() # Execute the code and delete the temporary file
    return output, err
######################################
# App initialization
#####################################
app = Flask("YACSS")

####################################
# Room Related Stuff
####################################
rooms = [] # Global array that will store all active rooms

class Room:
    def __init__(self, name):
        self.name = name
        self.code = ""
        self.users = []
        self.lastupdater = ""

###################################
# Routes
###################################

# Index: index is where it describes what to do to get to a room
@app.route('/', defaults={'path': ''})
def home(path):
    return render_template("index.html")

# Room: the RoomHandler is where it searches if the room exists, if so set room = to that existing room, then adds to global rooms array for later use
@app.route('/<path:path>')
def roomHandler(path):
    roomExists = False
    room = Room(path)

    for x in rooms:
        if x.name == path:
            roomExists = True
            room = x

    rooms.append(room)
    print(rooms)
    return render_template("room.html", roomObject=room)

# Upload: the uploadHandler is where the latest code is uploaded to server-side and the lastEditor is assigned
@app.route('/<path:path>/upload', methods=["POST"])
def uploadHandler(path):
    found = False
    room = Room("")

    for x in rooms:
        if x.name == path:
            found = True
            room = x
    if found == False:
        print(rooms)
        return json.dumps(True)
    else:
        print(request.json["newCode"])
        room.code = request.json["newCode"]
        room.lastupdater = request.json["username"]
        return json.dumps(True)

# Hello: the HelloHandler is where the client sends the server the client username and the server registers into an array
@app.route('/<path:path>/hello', methods=["POST"])
def helloHandler(path):
    found = False
    room = Room("")

    for x in rooms:
        if x.name == path:
            found = True
            room = x
    if found == False:
        return json.dumps({"status": "Room not found."})
    else:
        room.users.append(request.json["username"])
        return json.dumps({"status": "OK"})

# Request: the RequestHandler is where the server returns the current content of the respective room and the last editor
@app.route('/<path:path>/request')
def requestHandler(path):
    found = False
    room = Room("")

    for x in rooms:
        if x.name == path:
            found = True
            room = x
    if found == False:
        return json.dumps({"status": "Room not found."})
    else:
        return json.dumps({"status": "OK", "code": room.code, "lastUpdater": room.lastupdater})

# Compile: the CompileHandler takes care of the compilation of python from a JSON post parameter
@app.route('/<path:path>/compile', methods=["POST"])
def compileHandler(path):
    found = False # This variable will tell us later if the room was found
    room = Room("") # Generate temporary room

    for x in rooms: # For every room in the global array rooms
        if x.name == path: # If the name of the room is equal to the room the compilation is attempting to start in
            found = True
            room = x

    if found == False:
        return json.dumps({"status": "Room not found."}) # If a room wasn't found, tell the client
    else:
        code_data = request.json["code"] # Assign a variable for the input Python code
        code_data = [str(line + '\n') for line in code_data.splitlines()] # Split lines
        results, err = executor(code_data) # Go through the executor function and execute the actual code, return as the results and as any errors
        if err == "": # If there were no errors
            return json.dumps({"status": "OK", "response": results}) # Tell the client everything was fine and return what the program outputted
        else: # If there were errors
            return json.dumps({"status": "ERROR", "response": err}) # Tell the client that something went wrong :(


if __name__ == "__main__":
    app.run(host='127.0.0.1', debug=1) # Host = your current IP you are hosting on
