# SPDX-FileCopyrightText: Copyright (c) 2024 Karl Fleischmann for FRC Team 7411 Cyber Soldiers
#
# SPDX-License-Identifier: MIT
"""
`frc_can.CANMessage`
====================================================
FRC CAN Bus CAN Message class.

* Author(s): Karl Fleischmann
"""
import sys
from .FRCConsts import FRCManufacturer

class RobotHeartbeat:
    """RobotHeartbeat Class"""

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
        ) = RobotHeartbeat.__parse_heartbeat(data)

        self.match_time = match_time
        self.match_number = match_number
        self.replay_number = replay_number
        self.system_watchdog_p = system_watchdog
        self.test_mode = test_mode
        self.auto_mode = auto_mode
        self.enabled = enabled
        self.red_alliance = red_alliance

    @staticmethod
    def __parse_heartbeat(bytes_in):  # pylint: disable=too-many-locals, line-too-long
        # Bit masks for spliting out a 64bit binary field for heartbeat
        # see https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html
        # for more details
        # bits 64-57 8 bits
        match_time_mask = (
            0b1111111100000000000000000000000000000000000000000000000000000000
        )
        # bits 56-47 10 bits
        match_number_mask = (
            0b0000000011111111110000000000000000000000000000000000000000000000
        )
        # bits 46-41 6 bits
        replay_number_mask = (
            0b0000000000000000001111110000000000000000000000000000000000000000
        )
        # bits 40-38 3 bits
        # tournament_type_mask = (
        #     0b0000000000000000000000001110000000000000000000000000000000000000
        # )
        # bits 37 1 bit
        system_watchdog_mask = (
            0b0000000000000000000000000001000000000000000000000000000000000000
        )
        # bits 36 1 bit
        test_mode_mask = (
            0b0000000000000000000000000000100000000000000000000000000000000000
        )
        # bits 35 1 bit
        auto_mode_mask = (
            0b0000000000000000000000000000010000000000000000000000000000000000
        )
        # bits 34 1 bit
        enabled_mask = (
            0b0000000000000000000000000000001000000000000000000000000000000000
        )
        # bits 33 1 bit
        red_alliance_mask = (
            0b0000000000000000000000000000000100000000000000000000000000000000
        )
        # 0b1111111100000000000000000001101111111100110100000100110010000110 Red Enabled Test
        #                              STAER
        # bits 32-27 6 bits
        # datetime_year_mask = 0b0000000000000000000000000000000011111100000000000000000000000000
        # bits 26-23 4 bits
        # datetime_month_mask = 0b0000000000000000000000000000000000000011110000000000000000000000
        # bits 22-18 5 bits
        # datetime_day_mask = 0b0000000000000000000000000000000000000000001111100000000000000000
        # bits 17-12 6 bits
        # datetime_sec_mask = 0b0000000000000000000000000000000000000000000000011111100000000000
        # bits 11-6 6 bits
        # datetime_min_mask = 0b0000000000000000000000000000000000000000000000000000011111100000
        # bits 5-0 5 bits
        # datetime_hour_mask = 0b0000000000000000000000000000000000000000000000000000000000011111

        # split the heartbeat id using bitwise AND with right shift
        msg = int.from_bytes(bytes_in, sys.byteorder)
        # print(bin(msg))
        match_time = (msg & match_time_mask) >> 56
        match_number = (msg & match_number_mask) >> 46
        replay_number = (msg & replay_number_mask) >> 40
        # tournament_type = (msg & tournament_type_mask) >> 37
        system_watchdog = (msg & system_watchdog_mask) >> 36
        test_mode = (msg & test_mode_mask) >> 35
        auto_mode = (msg & auto_mode_mask) >> 34
        enabled = (msg & enabled_mask) >> 33
        red_alliance = (msg & red_alliance_mask) >> 32
        # datetime_year = (msg & datetime_year_mask) >> 26
        # datetime_month = (msg & datetime_month_mask) >> 22
        # datetime_day = (msg & datetime_day_mask) >> 17
        # datetime_sec = (msg & datetime_sec_mask) >> 11
        # datetime_min = (msg & datetime_min_mask) >> 5
        # datetime_hour = msg & datetime_hour_mask
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
    def system_watchdog(self):
        """system_watchdog property"""
        return self.system_watchdog_p

    @property
    def is_test_mode(self):
        """is_test_mode property"""
        return self.test_mode

    @property
    def is_auto_mode(self):
        """is_auto_mode property"""
        return self.auto_mode

    @property
    def is_enabled(self):
        """is_enabled property"""
        return self.enabled

    @property
    def on_red_alliance(self):
        """on_red_alliance property"""
        return self.red_alliance

    # def __repr__(self) -> str:
    #     return f"RobotHeartbeat{self.raw_heartbeat}"


class CANMessageType:  # pylint: disable=too-few-public-methods
    """CANMessageType Class"""
    Broadcast = 0
    Heartbeat = 1
    Device = 2


class CANMessage:
    """CANMessage Class"""
    def __init__(
        self,
        api_id: int = 0x00,
        msg_type: CANMessageType = CANMessageType.Broadcast,
        raw_msg_id: bytes = None,
        raw_msg_data: bytes = None,
    ) -> None:
        self.msg_type = msg_type
        self.msg_data = raw_msg_data
        self.api_class_id = 0
        self.api_index_id = 0

        if raw_msg_id is None:
            self.api_id_p = api_id
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
            except Exception as ex:
                raise ValueError("Unparseable raw_msg_id: ", raw_msg_id) from ex

            self.device_type = device_type
            self.device_number = device_number

            if mfg_code == FRCManufacturer.NationalInstruments:
                self.api_id_p = 0x01
                self.msg_type = CANMessageType.Heartbeat
                self.heartbeat_p = RobotHeartbeat(self.msg_data)
            elif mfg_code == FRCManufacturer.Broadcast:
                self.api_id_p = 0x0
                self.msg_type = CANMessageType.Broadcast
            else:
                self.msg_type = CANMessageType.Device

            self.api_id_p = api_id
            self.api_class_id = api_class
            self.api_index_id = api_index

    @staticmethod
    def __parse_raw_msg_id(bytes_in):
        """__parse_raw_msg_id function"""
        # Bit masks for spliting out a 32bit binary field
        # see https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html
        # for more details
        device_type = 0b1111100000000000000000000000  # bits 28-24
        mfg_code = 0b0000011111111000000000000000  # bits 23-16
        api = 0b0000000000000111111111100000  # bits 15-6
        api_class = 0b0000000000000111111000000000  # bits 15-10
        api_index = 0b0000000000000000000111100000  # bits 9-6
        device_number = 0b0000000000000000000000011111  # bits 5-0

        # split the message id using bitwise AND with right shift
        device_type = (bytes_in & device_type) >> 24
        mfg_code = (bytes_in & mfg_code) >> 16
        api_class = (bytes_in & api_class) >> 10
        api_index = (bytes_in & api_index) >> 6
        api_id = (bytes_in & api) >> 6
        device_number = bytes_in & device_number

        # print (bin(api_class), bin(api_index), bin(api_id), api_id)
        # print(bin(device_type), bin(mfg_code), bin(api), bin(device_number))
        # print(device_type, mfg_code, api, device_number)

        return device_type, mfg_code, api_class, api_index, api_id, device_number

    @property
    def api_id(self):
        """api_id property"""
        return self.api_id_p

    @property
    def api_class(self):
        """api_class property"""
        return self.api_class_id

    @property
    def api_index(self):
        """api_index property"""
        return self.api_index_id

    @property
    def data(self):
        """data property"""
        return self.msg_data

    @property
    def heartbeat(self) -> RobotHeartbeat:
        """heartbeat property"""
        return self.heartbeat_p

    def __hash__(self) -> int:
        """__hash__ function"""
        return hash(self.api_id_p) ^ hash(self.msg_type)

    def __eq__(self, other: "CANMessage") -> bool:
        """__eq__ function"""
        return self.api_id_p == other.api_id_p and self.msg_type == other.msg_type

    def __repr__(self) -> str:
        """__repr__ function"""
        return f"CANMessage(api_id={repr(self.api_id_p)}, msg_type={repr(self.msg_type)})"

    # Static Methods
    @staticmethod
    def assemble_message_id(dev_type, dev_mfg, api_class, api_index, dev_num):
        """assemble_message_id function"""
        # combine the device info with the api id using bitwise AND with left shift
        device_bits = dev_type << 24
        mfg_code_bits = dev_mfg << 16
        api_class_bits = api_class << 10
        api_index_bits = api_index << 6
        # api_id = (api_class_bits | api_index_bits) >> 6

        # print (bin(api_class), bin(api_index), bin(api_id), api_id)
        # print(bin(device_type), bin(mfg_code), bin(api), bin(device_number))
        # print(device_type, mfg_code, api, device_number)

        msg_id = device_bits | mfg_code_bits | api_class_bits | api_index_bits | dev_num
        return msg_id

    @staticmethod
    def assemble_message_id_short(dev_type, dev_mfg, api_id, dev_num):
        """assemble_message_id_short function"""
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
            device_bits
            | mfg_code_bits
            | api_id_bits
            | dev_num
        )
        return msg_id
