# enumerations
class FRCAppId:  # pylint: disable=too-few-public-methods
    """FRCAppId Class"""

    broadcast: int = 0x0
    heartbeat: int = 0x61


class FRCDeviceType:  # pylint: disable=too-few-public-methods
    """FRCDeviceType Class"""

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


class FRCManufacturer:  # pylint: disable=too-few-public-methods
    """FRCManufacturer Class"""

    Broadcast = 0
    NationalInstruments = 1
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


class FRCBroadcast:  # pylint: disable=too-few-public-methods
    """FRCBroadcast Class"""

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


class FRCMask:  # pylint: disable=too-few-public-methods
    """FRCMask Class"""

    # when using match masks in CAN a bit value of ...
    #   1 = must match filter on this bit
    #   0 = ignore this bit
    type_mfg_num = (
        0b1111111111110000000000111111  # match everything but Class and Index
    )
    num_mask = 0b0000000000000000000000111111  # match only device number
    api_class = 0b0000000000001111110000000000  # match only Class
    # exact_match      = 0b1111111111111111111111111111 # match everything exactly


class FRCFilter:  # pylint: disable=too-few-public-methods
    """FRCFilter Class"""

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
