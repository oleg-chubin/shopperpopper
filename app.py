import json

from aiohttp import web

from downloader import get_price_info

routes = web.RouteTableDef()


@routes.get('/')
async def hello(request):
    return web.Response(text="Hello, world!!!")


@routes.get('/search/')
async def search(request):
    name = request.query.get('name')
    result = await get_price_info(name)
    return web.Response(body=json.dumps(result), content_type='application/json')


@routes.post('/book/')
async def search(request):
    booking_details = await request.json()
    # Do something
    result = {'cart_id': 23432432, 'name': booking_details['name'] }
    return web.Response(body=json.dumps(result), content_type='application/json')


@routes.post('/buy/')
async def search(request):
    booking_details = await request.json()
    # Perform buy operation
    result = {'cart_id': booking_details['cart_id']}
    return web.Response(body=json.dumps(result), content_type='application/json')


app = web.Application()
app.add_routes(routes)
