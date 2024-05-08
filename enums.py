class API_ID:
    StatusRequest: int = 0x00
    StatusReply: int = 0x01
    SetDeviceNumber: int = 0x10
    InitPixelArray: int = 0x11

    PatternChaos:int = 0x20
    PatternRainbow:int = 0x21
    PatternSolid:int = 0x22
    PatternBlink:int = 0x23
    PatternIntensity:int = 0x24
    PatternScanner:int = 0x25
    PatternAlternating:int = 0x26
    PatternChase:int = 0x27

    ButtonPress:int = 0x30
