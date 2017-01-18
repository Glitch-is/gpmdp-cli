#!/usr/bin/python3

import asyncio
import websockets
import json
import os
import argparse


async def sendCommand(websocket, payload):
    namespace = payload["namespace"]
    method = payload["method"]
    arguments = payload["arguments"]

    payload = '{"namespace":"'+namespace+'","method":"'+method+'"'+(', "arguments":'+arguments if arguments else '')+'}'
    print("Sending payload:")
    print(payload)
    await websocket.send(payload)


async def recvUntil(websocket, channel):
    while True:
        response = json.loads(await websocket.recv())
        if "channel" in response:
            if response["channel"] == channel:
                return response

def saveAuthCode(code, tokenFile):
    with open(tokenFile, "w+") as f:
        f.write(code)


def loadAuthCode(tokenFile):
    if os.path.exists(tokenFile):
        with open(tokenFile, "r") as f:
            return f.read()
    else:
        return ""


async def connect(websocket, tokenFile):
    payload = {}
    payload["namespace"] = "connect"
    payload["method"] = "connect"
    payload["arguments"] = ["gpmdp-cli"]

    code = loadAuthCode(tokenFile)
    if code == "":

        await websocket.send(json.dumps(payload))
        await recvUntil(websocket, "connect")

        print("A UI will popup in GPMDP containing a 4 digit code")
        code = input("Enter code here: ")
        payload["arguments"].append(code)

        await websocket.send(json.dumps(payload))

        authResponse = await recvUntil(websocket, "connect")
        code = authResponse["payload"]
        saveAuthCode(code, tokenFile)

    payload["arguments"] = ["gpmdp-cli", code]
    await websocket.send(json.dumps(payload))

    print("Connected to client!")


def parseCommands(commands):
    c = commands.split()
    payload = {}
    payload["namespace"] = c[0]
    payload["method"] = c[1]
    payload["arguments"] = ' '.join(c[2:])
    return payload


async def main(args):
    socketServer = args.socket_server
    tokenFile = os.path.abspath(os.path.expanduser(args.token_file))
    commands = args.commands

    async with websockets.connect(socketServer) as websocket:
        await connect(websocket, tokenFile)
        await sendCommand(websocket, parseCommands(commands))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Google Play Desktop Music Player CLI client')
    parser.add_argument('commands',
                        help='API commands that will be sent to the socket server')
    parser.add_argument('--token-file',
                        help='Path to token file',
                        default="~/.config/Google Play Music Desktop Player/gpmdp-cli.token")
    parser.add_argument('--socket-server',
                        help='URL to socket server',
                        default='ws://localhost:5672')

    args = parser.parse_args()
    asyncio.get_event_loop().run_until_complete(main(args))
