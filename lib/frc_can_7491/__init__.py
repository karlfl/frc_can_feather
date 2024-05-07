# SPDX-FileCopyrightText: Copyright (c) 2024 Karl Fleischmann for Team 7491 Cyber Soldiers
#
# SPDX-License-Identifier: MIT
"""
`frc_can_7491`
================================================================================

Circuit Python Library for managing devices using the FIRST Robotics Competition (FRC) CAN Bus communications.  
Written by the programming team from 7491 Cyber Soldiers in Burton, MI


* Author(s): Karl Fleischmann

Implementation Notes
--------------------

**Hardware:**

.. todo:: Add links to any specific hardware product page(s), or category page(s).
  Use unordered list & hyperlink rST inline format: "* `Link Text <url>`_"

**Software and Dependencies:**

* Adafruit CircuitPython firmware for the supported boards:
  https://circuitpython.org/downloads

.. todo:: Uncomment or remove the Bus Device and/or the Register library dependencies
  based on the library's use of either.

# * Adafruit's Bus Device library: https://github.com/adafruit/Adafruit_CircuitPython_BusDevice
# * Adafruit's Register library: https://github.com/adafruit/Adafruit_CircuitPython_Register
"""

# enumerations
class FRCAppId:
    broadcast: int = 0x0
    heartbeat: int = 0x61

class FRCDeviceType:
    BroadcastMessages = 0
    RobotController = 1
    MotorController = 2
    RelayController = 3
    GyroSensor = 4
    Accelerometer = 5
    UltrasonicSensor = 6
    GearToothSensor = 7
    PowerDistributionModule = 8
    PneumaticsController = 9
    Miscellaneous = 10
    IOBreakout = 11
    FirmwareUpdate = 31

class FRCManufacturer:
    Broadcast = 0
    NI = 1
    LuminaryMicro = 2
    DEKA = 3
    CTRElectronics = 4
    REVRobotics = 5
    Grapple = 6
    MindSensors = 7
    TeamUse = 8
    KauaiLabs = 9
    Copperforge = 10
    PlayingWithFusion = 11
    Studica = 12
    TheThriftyBot = 13
    ReduxRobotics = 14
    AndyMark = 15
    VividHosting = 16

class FRCBroadcast:
    Disable = 0
    SystemHalt = 1
    SystemReset = 2
    DeviceAssign = 3
    DeviceQuery = 4
    Heartbeat = 5
    Sync = 6
    Update = 7
    FirmwareVersion = 8
    Enumerate = 9
    SystemResume = 10

class FRCMask:
    # when using match masks in CAN a bit value of ...
    #   1 = must match filter on this bit
    #   0 = ignore this bit
    type_mfg_num    = 0b1111111111110000000000111111  # match everything but Class and Index
    num_mask        = 0b0000000000000000000000111111  # match only device number
    api_class       = 0b0000000000001111110000000000  # match only Class
    # exact_match      = 0b1111111111111111111111111111 # match everything exactly

class FRCFilter:
    # Periodic Heartbeat CAN ID filter
    # Type= 1 (Robot Controller)
    # Manufacturer = 1 (NI)
    # API Class = 6 (Heartbeat)
    # API Index = 1 (Message)
    # Device Number = 0
    heartbeat = 0b0001000000010001100001000000
    # Broadcast CAN ID filter
    # Type= 0 (Robot Controller)
    # Manufacturer = 0 (NI)
    # API Class = 0 (Heartbeat)
    # API Index = contains broadcast message
    # Device Number = 0
    broadcast = 0b0000000000000000000000000000


# imports
from frc_can_7491.CANMessage import CANMessage, RobotHeartbeat
from frc_can_7491.CANDevice import CANDevice

__version__ = "0.0.0-auto.0"
__repo__ = "https://github.com/karlfl/7491_CircuitPython_FRCCAN.git"
