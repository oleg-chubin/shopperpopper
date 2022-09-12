import asyncio
import asyncpg

async def run():
    conn = await asyncpg.connect(user='friender', password='friender',
                                 database='friender', host='127.0.0.1')
    values = await conn.fetch(
        'SELECT * FROM friends_friend WHERE id = $1',
        10481790,
    )
    print(values)
    await conn.close()

loop = asyncio.get_event_loop()
loop.run_until_complete(run())
