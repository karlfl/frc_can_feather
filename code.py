# SPDX-FileCopyrightText: Copyright (c) 2024 Karl Fleischmann for Team 7491 Cyber Soldiers
#
# SPDX-License-Identifier: MIT
import sys
import asyncio
import board
from digitalio import DigitalInOut, Direction
import json
import neopixel
import supervisor

from adafruit_led_animation.animation.blink import Blink
from adafruit_led_animation.animation.solid import Solid
from adafruit_led_animation.color import RED, GREEN

from frc_can_7491 import CANDevice, CANMessage

from enums import API_ID

is_enabled = False
last_heartbeat_msg_time: int = 0

device_status = "disabled"

led = DigitalInOut(board.LED)
led.direction = Direction.OUTPUT

statusPixel = neopixel.NeoPixel(board.NEOPIXEL, 1, brightness=0.03, auto_write=False)

neoPixelArray = None

# statusPixel.fill((255,0,0))
# statusPixel.show()

status_animation = Blink(statusPixel, speed=0.5, color=RED)

can_config = json.load(open("can_config.json", "r"))
canDevice = CANDevice(
    dev_type=can_config["frc_device_type"],
    dev_manufacturer=can_config["frc_manufacturer"],
    dev_number=can_config["device_number"],
)

# TODO add routes to handle device number changes

# 'Heartbeat' messages
@canDevice.route(msg_type=CANMessage.Type.Heartbeat)
def heartbeat(message: CANMessage):  # pylint: disable=unused-argument
    global is_enabled, last_heartbeat_msg_time

    if not is_enabled == message.Heartbeat.IsEnabled:
        is_enabled = message.Heartbeat.IsEnabled
        set_status(None)

    # capture the time of the last heartbeat message
    # used to ensure robot is talking to us
    last_heartbeat_msg_time: int = supervisor.ticks_ms()

    return


# 'Broadcast' messages
@canDevice.route(msg_type=CANMessage.Type.Broadcast)
def broadcast(message: CANMessage):  # pylint: disable=unused-argument
    global is_enabled
    print("Broadcast: ", message.api_index)
    if message.APIIndex == 0:  # broadcast index of 0 = disable immediately
        is_enabled = False
        set_status(None)
    return


# Status Request
@canDevice.route(api_id=0x00)
def status_request(message: CANMessage):  # pylint: disable=unused-argu4117
    # immediately send a reply with a status update
    statusMessage = "Team7491"
    canDevice.send_message(0, 1, message=bytes(statusMessage, "utf-8"))
    # print("Status Sent: ", statusMessage)
    # print('\t', message)
    return


# Set Device ID
@canDevice.route(api_id=0x10)
def set_device_number(message: CANMessage):  # pylint: disable=unused-argu4117
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Set Number of LEDs
@canDevice.route(API_ID.InitPixelArray)
def init_pixel_array(message: CANMessage):  # pylint: disable=unused-argument
    # pixel_num = int(CANMessage.Data)
    # pixels = AddressableLED(pixel_pin,pixel_num)

    # print("Device", hex(message.api_id))
    # print('\t', message)
    # Number of LEDs is found in the right most byte
    print("Brightness:", int(message.Data[6]))
    print("Number of LEDs:", int(message.Data[7]))
    return


# Pattern Chaos
@canDevice.route(api_id=0x20)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Rainbow
@canDevice.route(api_id=0x21)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Solid
@canDevice.route(api_id=0x22)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Blink
@canDevice.route(api_id=0x23)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Intensity
@canDevice.route(api_id=0x24)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Scanner
@canDevice.route(api_id=0x25)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Alternating
@canDevice.route(api_id=0x26)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


# Pattern Chase
@canDevice.route(api_id=0x27)
def base(message: CANMessage):  # pylint: disable=unused-argument
    # print("Device", hex(message.api_id))
    # print('\t', message)
    return


def set_status(status):
    global is_enabled, device_status, status_animation
    if not is_enabled:  # disabled take precedence
        status_animation = Blink(statusPixel, speed=0.5, color=RED)
        print("Set Status: Disabled")
    else:
        status_animation = Solid(statusPixel, color=GREEN)
        print("Set Status: Enabled")


canDevice.start_listener()


async def status_update():
    while True:
        status_animation.animate()

        # update the status every 20ms
        await asyncio.sleep(0.02)


async def message_update():
    global is_enabled, last_heartbeat_msg_time
    while True:
        # handle all messages since the last receive was called
        canDevice.receive_messages()

        led.value = not led.value

        # if it's been more than 100ms since the last heartbeat, immediately disable device
        heartbeat_elapsed_time = supervisor.ticks_ms() - last_heartbeat_msg_time
        if heartbeat_elapsed_time > 100 and is_enabled == True:
            print("No heartbeat in more than 100ms - Disabling Device")
            is_enabled = False
            set_status(None)

        # processes messages ever 20ms.
        await asyncio.sleep(0.02)


async def main():
    # setup the cooperative multitasking tasks
    status_task = asyncio.create_task(status_update())
    message_task = asyncio.create_task(message_update())
    await asyncio.gather(status_task, message_task)
    print("Done")


asyncio.run(main())


# while True:
#     # canDevice.send_message(
#     #     frc_api_class.Ack, frc_api_index.SetReference, message=b"Team7491"
#     # )

#     # Handle all imcoming messages using routes defined above
#     canDevice.receive_messages()

#     led.value = not led.value

#     # sleep(0.5)
#     # print("Free", gc.mem_free())
