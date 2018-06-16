EESchema Schematic File Version 2
LIBS:new-joy
LIBS:power
LIBS:device
LIBS:transistors
LIBS:conn
LIBS:linear
LIBS:regul
LIBS:74xx
LIBS:cmos4000
LIBS:adc-dac
LIBS:memory
LIBS:xilinx
LIBS:microcontrollers
LIBS:dsp
LIBS:microchip
LIBS:analog_switches
LIBS:motorola
LIBS:texas
LIBS:intel
LIBS:audio
LIBS:interface
LIBS:digital-audio
LIBS:philips
LIBS:display
LIBS:cypress
LIBS:siliconi
LIBS:opto
LIBS:atmel
LIBS:contrib
LIBS:valves
LIBS:new-joy-board-cache
EELAYER 25 0
EELAYER END
$Descr A4 11693 8268
encoding utf-8
Sheet 1 1
Title ""
Date ""
Rev ""
Comp ""
Comment1 ""
Comment2 ""
Comment3 ""
Comment4 ""
$EndDescr
$Comp
L AZReady_ESP32 U1
U 1 1 5B23C3C4
P 3650 3900
F 0 "U1" H 3650 4900 50  0000 C CNN
F 1 "AZReady_ESP32" H 3650 2850 50  0000 C CNN
F 2 "new-joy:AZReady_ESP32" H 3300 3900 50  0001 C CNN
F 3 "" H 3300 3900 50  0001 C CNN
	1    3650 3900
	1    0    0    -1  
$EndComp
$Comp
L GND #PWR01
U 1 1 5B23D7F0
P 3100 1500
F 0 "#PWR01" H 3100 1250 50  0001 C CNN
F 1 "GND" H 3100 1350 50  0000 C CNN
F 2 "" H 3100 1500 50  0001 C CNN
F 3 "" H 3100 1500 50  0001 C CNN
	1    3100 1500
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR02
U 1 1 5B23DA07
P 3100 1200
F 0 "#PWR02" H 3100 1050 50  0001 C CNN
F 1 "+5V" H 3100 1340 50  0000 C CNN
F 2 "" H 3100 1200 50  0001 C CNN
F 3 "" H 3100 1200 50  0001 C CNN
	1    3100 1200
	1    0    0    -1  
$EndComp
$Comp
L dc_dc_converter U2
U 1 1 5B23E028
P 2550 1350
F 0 "U2" H 2550 1650 60  0000 C CNN
F 1 "dc_dc_converter" H 2550 1000 60  0000 C CNN
F 2 "new-joy:dc_dc_converter" H 2550 1650 60  0001 C CNN
F 3 "" H 2550 1650 60  0001 C CNN
	1    2550 1350
	1    0    0    -1  
$EndComp
$Comp
L Screw_Terminal_01x02 J1
U 1 1 5B23E0D2
P 1100 1300
F 0 "J1" H 1100 1400 50  0000 C CNN
F 1 "Screw_Terminal_01x02" H 1100 1100 50  0000 C CNN
F 2 "Connectors_Terminal_Blocks:TerminalBlock_bornier-2_P5.08mm" H 1100 1300 50  0001 C CNN
F 3 "" H 1100 1300 50  0001 C CNN
	1    1100 1300
	1    0    0    -1  
$EndComp
$Comp
L +5V #PWR03
U 1 1 5B2501A9
P 2700 4800
F 0 "#PWR03" H 2700 4650 50  0001 C CNN
F 1 "+5V" H 2700 4940 50  0000 C CNN
F 2 "" H 2700 4800 50  0001 C CNN
F 3 "" H 2700 4800 50  0001 C CNN
	1    2700 4800
	1    0    0    -1  
$EndComp
Wire Wire Line
	900  1300 900  1050
Wire Wire Line
	900  1050 2000 1050
Wire Wire Line
	2000 1050 2000 1200
Wire Wire Line
	900  1400 900  1600
Wire Wire Line
	900  1600 2000 1600
Wire Wire Line
	2000 1600 2000 1500
$Comp
L GND #PWR04
U 1 1 5B2501EA
P 4750 3600
F 0 "#PWR04" H 4750 3350 50  0001 C CNN
F 1 "GND" H 4750 3450 50  0000 C CNN
F 2 "" H 4750 3600 50  0001 C CNN
F 3 "" H 4750 3600 50  0001 C CNN
	1    4750 3600
	1    0    0    -1  
$EndComp
Wire Wire Line
	4250 3600 4750 3600
Wire Wire Line
	4250 3000 4750 3000
Wire Wire Line
	4750 3000 4750 3600
$Comp
L +12V #PWR05
U 1 1 5B2502BB
P 900 1050
F 0 "#PWR05" H 900 900 50  0001 C CNN
F 1 "+12V" H 900 1190 50  0000 C CNN
F 2 "" H 900 1050 50  0001 C CNN
F 3 "" H 900 1050 50  0001 C CNN
	1    900  1050
	1    0    0    -1  
$EndComp
$Comp
L GNDPWR #PWR06
U 1 1 5B2502FE
P 900 1600
F 0 "#PWR06" H 900 1400 50  0001 C CNN
F 1 "GNDPWR" H 900 1470 50  0000 C CNN
F 2 "" H 900 1550 50  0001 C CNN
F 3 "" H 900 1550 50  0001 C CNN
	1    900  1600
	1    0    0    -1  
$EndComp
Wire Wire Line
	2700 4800 3100 4800
$EndSCHEMATC
