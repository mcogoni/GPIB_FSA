# GPIB_FSA
A small python program to read/decode/plot/save the trace dump from the Rohde-Schwarz FSA Spectrum Analyzer that uses the GPIB bus to communicate with the PC. If you don't have an expensive GPIB interface like me, you might be interested in bulding a super easy one with just an Arduino Nano, a mutilated Centronics connector (yeah, you should have one in some closet from the days printers were connected by thick cables...) and a few interconnecting wires. The Arduino runs a slightly modified version of this code: https://github.com/JacekGreniger/gpib-conv-arduino-nano

In my home lab I have two R&S instruments: the FSAS spectrum analyzer and the SPMC signal generator. I have a GPIB cable connecting them and the Arduino interface piggybacks on one, then the USB cable goes to the PC via a 115kbps serial connection.

In the python source you may customize your equipment addresses, serial interface (you don't always get the /dev/ttyUSB0...) and commands to send for analysis.

I'm currently working on making an automated system to get the trace data from the FSAS to continuously monitor a wide frequency band and to be able to create a waterfall from 0 to 2 GHz with various bandwidths.

To use the program, just run on a terminal:

`python fsas.py`

it will then print instructions on how to use: direct capture from instrument or existing tracedump (re-)processing.

Have fun!

marco / IS0KYB

![Original FSAS image](https://github.com/mcogoni/GPIB_FSA/blob/master/FSAS_AM_signal.jpg)
![Image generated by the script](https://github.com/mcogoni/GPIB_FSA/blob/master/GPIB_tracedump.2018-04-13_13:40:29.png)
