import asyncio
import json
import logging
import os

import aiohttp
#import zmq
#import zmq.asyncio
from aiohttp import web
from datetime import datetime

from db import get_connection
from downloader import get_price_info

logger = logging.getLogger(__name__)

routes = web.RouteTableDef()


@routes.get('/')
async def form(request):
    with open(
            os.path.join(request.config_dict['PROJECT_DIR'],
                         'templates/table_radar.html'), 'rb') as fi:
        body = fi.read()
    return web.Response(body=body, content_type='text/html')

@routes.post('/')
async def form(request):
    sexes = {'f': 'm', 'm': 'f'}
    data = await request.post()
    sex = data['sex']
    if not request.app['friends'].get(sexes[sex]):
        request.app['friends'].setdefault(sex, []).append(data)
        print(request.app['friends'])
    return web.HTTPFound('/')


@routes.get('/search/')
async def search(request):
    name = request.query.get('name')
    result = await get_price_info(name)
    return web.Response(body=json.dumps(result), content_type='application/json')


@routes.get('/radar/')
async def radar_page(request):
    await app['queue'].put(b'newcomer')

    with open(
            os.path.join(request.config_dict['PROJECT_DIR'],
                         'templates/table_radar.html'), 'rb') as fi:
        body = fi.read()
    return web.Response(body=body, content_type='text/html')


@routes.get('/radar/data/')
async def websocket_handler(request):

    ws = web.WebSocketResponse(autoping=True, heartbeat=60)

    ready = ws.can_prepare(request=request)
    if not ready:
        await ws.close(code=aiohttp.WSCloseCode.PROTOCOL_ERROR)

    await ws.prepare(request)

    request.app['websockets'].append(ws)

    async for msg in ws:
        if msg.type == aiohttp.WSMsgType.TEXT:
            logger.error('Got some text message' + repr(msg) + repr(request.app['websockets']))
            if msg.data == 'close':
                await ws.close()
            else:
                for user_ws in request.app['websockets']:
                    if ws.closed:
                        continue
                    await user_ws.send_str(f' {datetime.now()}: {msg.data}')
        elif msg.type == aiohttp.WSMsgType.ERROR:
            print('ws connection closed with exception %s' %
                  ws.exception())
    print('websocket connection closed')
    return ws

def create_app():
    app = web.Application()
    app.add_routes(routes)
    app['PROJECT_DIR'] = os.path.dirname(__file__)
    app['queue'] = asyncio.Queue()
    app['websockets'] = []
    app['friends'] = {}


    async def create_aiopg(app):
        app['pg_connection'] = await get_connection(
            user='friender',
            database='friender',
            host='127.0.0.1',
            password='friender'
        )


    async def dispose_aiopg(app):
        await app['pg_connection'].close()
        # app['pg_connection'].wait_closed()


    app.on_startup.append(create_aiopg)
    app.on_cleanup.append(dispose_aiopg)
    return app


async def listen_to_zmq(app):

    # ctx = zmq.asyncio.Context()

    queue = app['queue']
    while True:
        msg = await queue.get()  # waits for msg to be ready
        for ws in app['websockets']:
            logger.info('Websocket:' + repr(ws))
            await ws.send_str(msg + '/broadcast')



async def start_background_task(app):
    app['zmq_listener'] = asyncio.create_task(listen_to_zmq(app))


async def cleanup_background_task(app):
    app['zmq_listener'].cancel()
    await app['zmq_listener']



app = create_app()

app.on_startup.append(start_background_task)
app.on_cleanup.append(cleanup_background_task)