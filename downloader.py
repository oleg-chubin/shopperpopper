import asyncio
import json

from aiohttp import ClientSession

chunk_size = 100

async def inner_function(url, data):
    print('I am pretending that I am very busy')
    async with ClientSession() as session:
        async with session.get(url, params=data) as response:
            result = await response.json()
    return [
        {
            'name': res['title'],
            'price': res['storeProduct']['priceWithSale'],
            'vendor': (res['brand'] or {}).get('title')}
        for res in result
    ]


async def get_price_info(name):
    print('I am going to wait 10 s')
    green_url = gippo_url = 'https://green-dostavka.by/api/v1/products/search/'
    green_data = gippo_data = {
        'storeId': 2,
        'search': name,
        'includeAdultOnly': 'true'
    }
    result = await asyncio.gather(
        inner_function(green_url, green_data),
        inner_function(gippo_url, gippo_data))

    all_prices = []
    for shop, prices in zip(['green', 'gippo'], result):
        for price in prices:
            price.update(shop=shop)
            all_prices.append(price)
    return all_prices

async def main():
    all_prices = await get_price_info('хлеб')
    print('I am done', all_prices)


if __name__ == '__main__':
    asyncio.run(main())
