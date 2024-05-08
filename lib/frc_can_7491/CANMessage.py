# SPDX-FileCopyrightText: Copyright (c) 2024 Karl Fleischmann for FRC Team 7411 Cyber Soldiers
#
# SPDX-License-Identifier: MIT
"""
`frc_can.CANRequest`
====================================================
FRC CAN Bus CAN Message class.

* Author(s): Karl Fleischmann
"""
import sys
from frc_can_7491 import FRCManufacturer

class RobotHeartbeat:
    def __init__(self, data):
        self.raw_data = data
        (
            match_time,
            match_number,
            replay_number,
            system_watchdog,
            test_mode,
            auto_mode,
            enabled,
            red_alliance,
        ) = self.__parse_heartbeat(data)

        self.system_watchdog = system_watchdog
        self.test_mode = test_mode
        self.auto_mode = auto_mode
        self.enabled = enabled
        self.red_alliance = red_alliance

    def __parse_heartbeat(self, bytes):
        # Bit masks for spliting out a 64bit binary field for heartbeat
        # see https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html for more details
        match_time = 0b1111111100000000000000000000000000000000000000000000000000000000  # bits 64-57 8 bits
        match_number = 0b0000000011111111110000000000000000000000000000000000000000000000  # bits 56-47 10 bits
        replay_number = 0b0000000000000000001111110000000000000000000000000000000000000000  # bits 46-41 6 bits
        tournament_type = 0b0000000000000000000000001110000000000000000000000000000000000000  # bits 40-38 3 bits

        system_watchdog = 0b0000000000000000000000000001000000000000000000000000000000000000  # bits 37 1 bit
        test_mode = 0b0000000000000000000000000000100000000000000000000000000000000000  # bits 36 1 bit
        auto_mode = 0b0000000000000000000000000000010000000000000000000000000000000000  # bits 35 1 bit
        enabled = 0b0000000000000000000000000000001000000000000000000000000000000000  # bits 34 1 bit
        red_alliance = 0b0000000000000000000000000000000100000000000000000000000000000000  # bits 33 1 bit
        # 0b1111111100000000000000000001101111111100110100000100110010000110 Red Enabled Test
        #                              STAER
        datetime_year = 0b0000000000000000000000000000000011111100000000000000000000000000  # bits 32-27 6 bits
        datetime_month = 0b0000000000000000000000000000000000000011110000000000000000000000  # bits 26-23 4 bits
        datetime_day = 0b0000000000000000000000000000000000000000001111100000000000000000  # bits 22-18 5 bits
        datetime_sec = 0b0000000000000000000000000000000000000000000000011111100000000000  # bits 17-12 6 bits
        datetime_min = 0b0000000000000000000000000000000000000000000000000000011111100000  # bits 11-6 6 bits
        datetime_hour = 0b0000000000000000000000000000000000000000000000000000000000011111  # bits 5-0 5 bits

        # split the heartbeat id using bitwise AND with right shift
        msg = int.from_bytes(bytes, sys.byteorder)
        # print(bin(msg))
        match_time = (msg & match_time) >> 56
        match_number = (msg & match_number) >> 46
        replay_number = (msg & replay_number) >> 40
        tournament_type = (msg & tournament_type) >> 37
        system_watchdog = (msg & system_watchdog) >> 36
        test_mode = (msg & test_mode) >> 35
        auto_mode = (msg & auto_mode) >> 34
        enabled = (msg & enabled) >> 33
        red_alliance = (msg & red_alliance) >> 32
        datetime_year = (msg & datetime_year) >> 26
        datetime_month = (msg & datetime_month) >> 22
        datetime_day = (msg & datetime_day) >> 17
        datetime_sec = (msg & datetime_sec) >> 11
        datetime_min = (msg & datetime_min) >> 5
        datetime_hour = msg & datetime_hour
        # print (bin(api_class), bin(api_index), bin(api_id), api_id)
        # print(bin(device_type), bin(mfg_code), bin(api), bin(device_number))
        # print(device_type, mfg_code, api, device_number)

        return (
            match_time,
            match_number,
            replay_number,
            system_watchdog,
            test_mode,
            auto_mode,
            enabled,
            red_alliance,
            # tournament_type,
            # datetime_year, datetime_month, datetime_day,
            # datetime_sec, datetime_min, datetime_hour
        )

    @property
    def SystemWatchdog(self):
        return self.system_watchdog

    @property
    def IsTestMode(self):
        return self.test_mode

    @property
    def IsAutoMode(self):
        return self.auto_mode

    @property
    def IsEnabled(self):
        return self.enabled

    @property
    def OnRedAlliance(self):
        return self.red_alliance

    def __repr__(self) -> str:
        return f"RobotHeartbeat{self.raw_heartbeat}"


class CANMessage:

    class Type:
        Broadcast = 0
        Heartbeat = 1
        Device = 2

    def __init__(
        self,
        api_id: int = 0x00,
        msg_type: Type = Type.Broadcast,
        raw_msg_id: bytes = None,
        raw_msg_data: bytes = None,
    ) -> None:
        self.msg_type = msg_type
        self.msg_data = raw_msg_data
        self.api_class = 0
        self.api_index = 0

        if raw_msg_id is None:
            self.api_id = api_id
            self.msg_type = msg_type
        else:
            # Parse message details from raw message id
            try:
                (
                    device_type,
                    mfg_code,
                    api_class,
                    api_index,
                    api_id,
                    device_number,
                ) = self.__parse_raw_msg_id(raw_msg_id)
            except:
                raise ValueError("Unparseable raw_msg_id: ", raw_msg_id)

            if mfg_code == FRCManufacturer.NI:
                self.api_id = 0x01
                self.msg_type = CANMessage.Type.Heartbeat
                self.heartbeat = RobotHeartbeat(self.msg_data)
            elif mfg_code == FRCManufacturer.Broadcast:
                self.api_id = 0x0
                self.msg_type = CANMessage.Type.Broadcast
            else:
                self.msg_type = CANMessage.Type.Device

            self.api_id = api_id
            self.api_class = api_class
            self.api_index = api_index

    def __parse_raw_msg_id(self, bytes):
        # Bit masks for spliting out a 32bit binary field
        # see https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html for more details
        device_type    = 0b1111100000000000000000000000  # bits 28-24
        mfg_code       = 0b0000011111111000000000000000  # bits 23-16
        api            = 0b0000000000000111111111100000  # bits 15-6
        api_class      = 0b0000000000000111111000000000  # bits 15-10
        api_index      = 0b0000000000000000000111100000  # bits 9-6
        device_number  = 0b0000000000000000000000011111  # bits 5-0

        # split the message id using bitwise AND with right shift
        device_type     = (bytes & device_type) >> 24
        mfg_code        = (bytes & mfg_code) >> 16
        api_class       = (bytes & api_class) >> 10
        api_index       = (bytes & api_index) >> 6
        api_id          = (bytes & api) >> 6
        device_number =    bytes & device_number

        # print (bin(api_class), bin(api_index), bin(api_id), api_id)
        # print(bin(device_type), bin(mfg_code), bin(api), bin(device_number))
        # print(device_type, mfg_code, api, device_number)

        return device_type, mfg_code, api_class, api_index, api_id, device_number

    @property
    def APIId(self):
        return self.api_id

    @property
    def APIClass(self):
        return self.api_class

    @property
    def APIIndex(self):
        return self.api_index

    @property
    def Data(self):
        return self.msg_data

    @property
    def Heartbeat(self) -> RobotHeartbeat:
        return self.heartbeat

    def __hash__(self) -> int:
        return hash(self.api_id) ^ hash(self.msg_type)

    def __eq__(self, other: "CANMessage") -> bool:
        return self.api_id == other.api_id and self.msg_type == other.msg_type

    def __repr__(self) -> str:
        return f"CANMessage(api_id={repr(self.api_id)}, msg_type={repr(self.msg_type)})"
    
    #Static Methods
    def assemble_message_id(dev_type, dev_mfg, api_class, api_index, dev_num):
        # combine the device info with the api id using bitwise AND with left shift
        device_bits = dev_type << 24
        mfg_code_bits = dev_mfg << 16
        api_class_bits = api_class << 10
        api_index_bits = api_index << 6
        api_id = (api_class_bits | api_index_bits) >> 6

        # print (bin(api_class), bin(api_index), bin(api_id), api_id)
        # print(bin(device_type), bin(mfg_code), bin(api), bin(device_number))
        # print(device_type, mfg_code, api, device_number)

        msg_id = (
            device_bits | mfg_code_bits | api_class_bits | api_index_bits | dev_num
        )
        return msg_id
        
    def assemble_message_id(dev_type, dev_mfg, api_id, dev_num):
        # combine the device info with the api id using bitwise AND with left shift
        device_bits = dev_type << 24
        mfg_code_bits = dev_mfg << 16
        # api_class_bits = api_class << 10
        # api_index_bits = api_index << 6
        api_id_bits = api_id << 6 
        # api_id = (api_class_bits | api_index_bits) >> 6

        # print (bin(api_class), bin(api_index), bin(api_id), api_id)
        # print(bin(device_type), bin(mfg_code), bin(api), bin(device_number))
        # print(device_type, mfg_code, api, device_number)

        msg_id = (
            # device_bits | mfg_code_bits | api_class_bits | api_index_bits | dev_num
            device_bits | mfg_code_bits | api_id_bits | dev_num
        )
        return msg_id
        

