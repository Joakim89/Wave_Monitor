import bge
import serial
import io
#import mathutils
import math


def main():
    # get info about the Brick
    cont = bge.logic.getCurrentController()
    own = cont.owner

    # Get sensor info, so we can run this script in loop
    mainloop = cont.sensors["MainLoop"]

    # initialization, run this only in the first loop
    if not 'init' in own:
        own['init'] = 1  # create own['init'], so we know that we have done initialization and we do not run it again

        # initialize serial port
        own['serial_port'] = serial.Serial()
        own['serial_port'].baudrate = 115200
        own['serial_port'].port = 'COM8'  # adjust to your port
        own[
            'serial_port'].timeout = 0.1  # you may want to play with this value, lower is, higher value e.g. 1 will slow down everything

        # needed for readline command (if you decide to use it)
        own['serial_io'] = io.TextIOWrapper(io.BufferedRWPair(own['serial_port'], own['serial_port']))

        # open the serial port
        own['serial_port'].close()  # sometimes the port is stucked if not closed properly, force it to close
        own['serial_port'].open()
        print("Serial port Open = ", own['serial_port'].is_open)

        # start the loop
        mainloop.usePosPulseMode = True

        # Main loop
    answer = ""
    while answer.count(';') < 4:  # wait in this while until we have at least one full valid data
        if own['serial_port'].in_waiting > 0:
            byte_in = own['serial_io'].read(own['serial_port'].in_waiting)
            answer = answer + byte_in

    print("OpenRex buffer:", answer)
    print("OpenRex waiting:", own['serial_port'].in_waiting)

    # Update
    print("Update")
    if ';' in answer:  # new command was received

        # the string will look simple ASNNNNN; 5
        # where A is axis, S is sign, NNNNN is number, ; is used to separate the strings/segments

        answers = answer.split(';')  # break the answer into pieces
        answer = answers[-2]  # get the last fully valid segment

        # if we are going to adjust rotation around z
        if 'z' in answer:
            answer = answer.replace('z', '')  # remove info about axis
            print("Updating Z rotation to: ", answer)

            # rotate the brick based on incomming data
            ownOrient = own.worldOrientation.to_euler()  # convert the orientation to a euler so we can easily set it

            # prepare the new orientation
            print("Old z = ", math.degrees(ownOrient[2]))
            ownOrient[2] = math.radians(float(answer) * (-1))  # I used -1 as the brick was rotating the other way round
            print("New z = ", math.degrees(ownOrient[2]))

        ownMatrix = ownOrient.to_matrix()  # build our new matrix so it can be applied to the object#
        own.worldOrientation = ownMatrix  # set the new orientation

    # exit the script when board will send q character
    if 'q' in answer:
        mainloop.usePosPulseMode = False  # switch off the main loop

        own['serial_port'].close()  # close serial port
        print("Serial port Open = ", own['serial_port'].is_open)

        gameactu = cont.actuators['Game']
        cont.activate(gameactu)  # Exit game


main()