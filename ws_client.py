import asyncio
import json

import aiohttp
from aiohttp import ClientSession


async def main():
    session = ClientSession()
    async with session.ws_connect("ws://localhost:8000/radar/data/", autoclose=True) as ws:
        # msg = True
        while msg := input():
            print(f"I am going to tell {msg}")
            await ws.send_str(msg)
            msg = await ws.receive()
            if msg.type == aiohttp.WSMsgType.TEXT:
                print(msg.data)
                # await ws.send_str(msg.data + '/client_answer')
            else:
                print ('error', msg)
                ws.exception()
                pass
                # break
        try:
            await asyncio.wait_for(ws.close(), 2)
        except asyncio.TimeoutError:
            print('TimeoutError')


if __name__ == '__main__':
    asyncio.run(main())
