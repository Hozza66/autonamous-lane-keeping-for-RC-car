# Autonamous Lane Keeping for Remote Controlled Cars

This repository contains the codes for a autonamous lane keeping system developed for RC cars.

Car_Control.ino contains the Arduino microcontroller unit (MCU) codes which controls the drive/steering of an RC car. The MCU is connected directly to the RC cars's reciever.

Lane_Keeping.py contains the codes for the lane keeping system. The system uses OpenCV 2 for computer vision. For testing, this program was ran on a Raspberry Pi 3 which was attached to the RC car. The output is connected to the MCU for car control instructions. The Raspberry Pi uses a external camera to capture the lane information in front of the car.
