# GPIB_FSA

## Trace dump tool
A small python program to read/decode/plot/save the trace dump from the Rohde-Schwarz FSA Spectrum Analyzer that uses the GPIB bus to communicate with the PC. If you don't have an expensive GPIB interface like me, you might be interested in bulding a super easy one with just an Arduino Nano, a mutilated Centronics connector (yeah, you should have one in some closet from the days printers were connected by thick cables...) and a few interconnecting wires. The Arduino runs a slightly modified version of this code: https://github.com/JacekGreniger/gpib-conv-arduino-nano

In my home lab I have two R&S instruments: the FSAS spectrum analyzer and the SPMC signal generator. I have a GPIB cable connecting them and the Arduino interface piggybacks on one, then the USB cable goes to the PC via a 115kbps serial connection.

In the python source you may customize your equipment addresses, serial interface and commands to send for analysis.
To use the program, just run on a terminal:

`python fsas.py`

it will then print instructions on how to use: direct capture from instrument or existing tracedump (re-)processing.

## General processing tool (under heavy development)
The second tool I am currently developing (so it is a bit bug ridden...) is `gpib.py`. With this you can create a different text file for each analysis operating over all your GPIB connected instruments.
At the moment I implemented a very basic (but intuitive) scripting language that can help you modularize sequences of commands, create local variables, calling metafunctions defined in the Python source code for dealing with complex IN/OUT like the trace dump of the basic tool `fsas.py`.
I included an example script called `commands.txt` that should be processed in this way:
`python gpib.py -p commands.txt`

Notice that at the moment the trace dump metafunction is not working correctly due to a dirty buffer. Should fix this soon.
Please study the `commands.txt` to understand the basic scripting rules.


Have fun!

marco / IS0KYB

![Original FSAS image](https://github.com/mcogoni/GPIB_FSA/blob/master/FSAS_AM_signal.jpg)
![Image generated by the script](https://github.com/mcogoni/GPIB_FSA/blob/master/GPIB_tracedump.2018-04-13_13:40:29.png)
![The ugly adapter](https://github.com/mcogoni/GPIB_FSA/blob/master/Arduino-GPIB-USB-interface.jpg)
