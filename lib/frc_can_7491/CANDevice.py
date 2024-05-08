import board
import sys
from digitalio import DigitalInOut

try:
    from typing import Callable
except ImportError:
    pass

from adafruit_mcp2515 import MCP2515 as CAN
from adafruit_mcp2515.canio import Message, RemoteTransmissionRequest, Match, BusState

from frc_can_7491 import CANMessage
from frc_can_7491 import FRCAppId, FRCFilter, FRCMask

# CAN Device Class
class CANDevice:
    def __init__(
        self,
        dev_type: int,
        dev_manufacturer: int,
        dev_number: int,
        baud_rate=1_000_000,
        spi=board.SPI(),
        cs=board.CAN_CS,
        debug=False,
    ) -> None:

        print("******************************************************")
        print("***  FRC CAN Device Initialization")
        print("******************************************************")
        print(f"***  Type:         {int(dev_type)}")
        print(f"***  Manufacturer: {int(dev_manufacturer)}")
        print(f"***  Number:       {int(dev_number)}")
        print("******************************************************")
        print("")

        # setup the CAN Bus
        self.cs = DigitalInOut(cs)
        self.cs.switch_to_output()
        self.can_bus = CAN(spi, self.cs, baudrate=baud_rate, debug=debug)

        self.handlers = {}

        self.dev_mfg = dev_manufacturer
        self.dev_type = dev_type
        self.dev_num = dev_number

        self.debug = debug
        self.enabled = False

        self.device_filter = self.build_device_filter(
            dev_manufacturer, dev_type, dev_number
        )

    # create a device filter (type, mfg and number)to use when listening for packets
    # this will ignore the API_ID portion of the extended CAN id used by FRC
    # see https://docs.wpilib.org/en/stable/docs/software/can-devices/can-addressing.html for more details
    def build_device_filter(self, dev_manufacturer, dev_type, dev_number):
        return (dev_type << 24) | (dev_manufacturer << 16) | (0x00 << 6) | (dev_number)

    def get_device_filter_bin(self):
        return bin(self.device_filter)

    def route(
        self,
        api_id: int = FRCAppId.heartbeat,
        msg_type: CANMessage.Type = CANMessage.Type.Device,
    ):
        """Decorator used to add a route to handle incoming CAN Messages.

        Parameters::
        :param int               api_id: API Class and API Index that this route will handle
        :param CANMessage.Type   method: Type of CAN message to handle for (i.e. Heartbeat, Device or Broadcast)

        Example::

            @server.route(path, method)
            def route_func(message):
                # route body handling message
        """

        if msg_type == CANMessage.Type.Broadcast:
            api_id = FRCAppId.broadcast

        def route_decorator(func: Callable) -> Callable:
            self.handlers[CANMessage(api_id, msg_type)] = func
            return func

        return route_decorator

    def send_message(self, apiClass: int, apiIndex: int, message: bytes):
        send_success = False

        msg_id = CANMessage.assemble_message_id(
            self.dev_type, self.dev_mfg, int(apiClass), int(apiIndex), self.dev_num
        )

        return self.__send_can_message(msg_id, message)

    def send_message(self, apiId: int, message: bytes):
        send_success = False

        msg_id = CANMessage.assemble_message_id(
            self.dev_type, self.dev_mfg, int(apiId), self.dev_num
        )

        return self.__send_can_message(msg_id, message)

    def __send_can_message(self, msg_id, message):
        # construct MCP2515 message
        canMessage = Message(id=msg_id, data=message, extended=True)

        # depending on the can bus state, send the message
        if self.can_bus.state in (BusState.ERROR_ACTIVE, BusState.ERROR_WARNING):
            try:
                send_success = self.can_bus.send(canMessage)
            except RuntimeError as ex:
                print("Unexpected error:", ex)
        else:
            print("CAN Bus is not active. Bus State:", self.can_bus.state)

        return send_success

    def start_listener(self):
        """
        Setup the listener on the CAN bus using the MCP2515 library.

        The MCP2515 has slots for 2 masks and 6 filters.
        Mask-0 has 2 filter slots, Mask-1 has 4 filter slots.
        You can use up to 6 matches (match = mask & filter).
        The order of the match objects below matter.
        The first mask used in the array can only have 2 filters.
        The second mask used can have up to 4 filters.
        Not passing in a mask will use an 'exact match' mask of all 1's

        Read the MCP2515 datasheet for more details on masks and filters.
        """
        self.listener = self.can_bus.listen(
            matches=[
                # Match FRC RoboRIO Heartbeat using default mask (exact match)
                Match(
                    FRCFilter.heartbeat,
                    extended=True,
                ),
                # FRC Broadcast messages use the API_Index bits to indicate the broadcast message
                # the remaining bits are set to 0.  Therefore this match can use the same mask as the 
                # device speficic one which only looks at only the type, manufacturer and number.
                Match(
                    FRCFilter.broadcast,
                    mask=FRCMask.type_mfg_num,
                    extended=True,
                ),
                # The remaining messages we're concerned with are the device specific messages.
                # This match will use device mask to match on only the type, manufacture and number of 
                # this device
                Match(
                    self.device_filter,
                    mask=FRCMask.type_mfg_num,
                    extended=True,
                ),
            ],
            timeout=0.9,
        )
        print("***  Listening for Broadcast, Heartbeat and Device specific messages")
        print()

    def receive_messages(self):
        # receive CAN messages and split out the device, api and data values
        message_count = self.listener.in_waiting()
        # print(message_count, "messages received")

        for _i in range(message_count):
            msg = self.listener.receive()

            # Regular CAN Messages...
            if isinstance(msg, Message):
                message = CANMessage(raw_msg_id=msg.id, raw_msg_data=msg.data)

                # Does a routes exists for this message...
                route = self.handlers.get(message)
                if route:
                    # call it
                    route(message)
                else:
                    # If not log an error.
                    if message.api_id == FRCAppId.heartbeat:
                        print("Handler Not Defined for FRC Heartbeat messages")
                        print(bin(msg.id), bin(int.from_bytes(msg.data, sys.byteorder)))
                    elif message.api_class == FRCAppId.broadcast:
                        print("Handler Not Defined for FRC Broadcast messages")
                        print(bin(msg.id), bin(int.from_bytes(msg.data, sys.byteorder)))
                    else:
                        print(
                            "Handler Not Defined. API ID:",
                            hex(message.api_id),
                            "Message Type:",
                            message.msg_type,
                            bin(msg.id),
                        )

            # Remote Transmission Requests (these don't have can data?)
            if isinstance(msg, RemoteTransmissionRequest):
                print("RTR length:", msg.length)
