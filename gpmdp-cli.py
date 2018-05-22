#!/usr/bin/env python3

import asyncio
import websockets
import json
import os
import argparse
import random
import sys

TIMEOUT = 2  # seconds
DEFAULT_TOKEN_FILE = "~/.config/Google Play Music Desktop Player/gpmdp-cli.token"
DEFAULT_SERVER_URL = "ws://localhost:5672"


async def sendCommand(websocket, payload):
    requestID = str(random.randrange(9999))
    payload["requestID"] = requestID

    try:
        await websocket.send(json.dumps(payload))
        response = await asyncio.wait_for(recvCommand(websocket, requestID), TIMEOUT)
        if "value" in response:
            print(response["value"])
    except asyncio.TimeoutError:
        print(f"No reponse from server; are you sure `{payload['namespace']} {payload['method']} {payload['arguments']}` is a valid command?", file=sys.stderr)
        sys.exit(1)

async def recvCommand(websocket, requestID):
    while True:
        response = json.loads(await websocket.recv())
        if "requestID" in response:
            if response["requestID"] == str(requestID):
                return response

async def recvUntil(websocket, channel):
    while True:
        response = json.loads(await websocket.recv())
        if "channel" in response:
            if response["channel"] == channel:
                return response

async def getAuthCode(websocket, tokenFile, payload):
    if os.path.exists(tokenFile):
        with open(tokenFile, "r") as f:
            return f.read()
    else:
        code = await collectAuthCode(websocket, tokenFile, payload)
        saveAuthCode(code, tokenFile)
        return code


async def collectAuthCode(websocket, tokenFile, payload):
    await websocket.send(json.dumps(payload))
    await recvUntil(websocket, "connect")

    print("A UI will popup in GPMDP containing a 4 digit code")
    code = input("Enter code here: ")
    payload["arguments"].append(code)

    await websocket.send(json.dumps(payload))
    authResponse = await recvUntil(websocket, "connect")
    return authResponse["payload"]


def saveAuthCode(code, tokenFile):
    if not os.path.exists(os.path.dirname(tokenFile)):
        os.mkdir(os.path.dirname(tokenFile))

    with open(tokenFile, "w+") as f:
        f.write(code)


async def connect(websocket, tokenFile):
    payload = {
            "namespace": "connect",
            "method": "connect",
            "arguments": ["gpmdp-cli"]
            }

    authCode = await getAuthCode(websocket, tokenFile, payload)
    payload["arguments"] = ["gpmdp-cli", authCode]
    await websocket.send(json.dumps(payload))


def parseCommands(args):
    payload = {
            "namespace": args.namespace,
            "method": args.method,
            "arguments": args.arguments
            }
    return payload


async def main(args):
    socketServer = args.socket_server
    tokenFile = os.path.abspath(os.path.expanduser(args.token_file))

    async with websockets.connect(socketServer) as websocket:
        await connect(websocket, tokenFile)
        await sendCommand(websocket, parseCommands(args))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Google Play Desktop Music Player CLI client",
            epilog=f"See https://github.com/gmusic-utils/gmusic.js#documentation for a full list of\
                    commands (where `playback.playPause()` from that page would be called with\
                    `{os.path.splitext(os.path.basename(__file__))[0]} playback playPause`)")
    parser.add_argument("namespace",
                        help="Command namespace, eg. playback, volume, rating")
    parser.add_argument("method",
                        help="Command method, eg. playPause, getVolume, setRating")
    parser.add_argument("arguments", nargs="*",
                        help="Arguments for method, eg. 3 in `rating setRating 3`")
    parser.add_argument("--token-file",
                        help="Path to token file",
                        default=DEFAULT_TOKEN_FILE)
    parser.add_argument("--socket-server",
                        help="URL to socket server",
                        default=DEFAULT_SERVER_URL)

    args = parser.parse_args()
    asyncio.get_event_loop().run_until_complete(main(args))
