from aiohttp import web
from db import setup_db
import asyncio
from bson import ObjectId
import aiohttp_jinja2
import jinja2
import urllib.parse


@aiohttp_jinja2.template('ask_url.html')
async def shorturl_get(request):
    return {}


@aiohttp_jinja2.template('short_url.html')
async def shorturl_post(request):
    result_text = await request.text()
    user_url = result_text.replace('user_url=', '')
    user_url = urllib.parse.unquote(user_url)
    database = request.app["db"]
    collection = database['shorturl']
    url_record = await collection.insert_one({'user_url': user_url})
    return {'short_url': url_record.inserted_id}


async def handler(request):
    name_url = request.match_info.get('name')
    database = request.app['db']
    collection = database['shorturl']
    obj_url = await collection.find_one({'_id': ObjectId(name_url)})
    select_url = obj_url['user_url']
    if 'http://' in select_url or 'https://' in select_url:
        return web.HTTPFound(select_url)
    else:
        return web.HTTPFound('http://' + select_url)


db = asyncio.run(setup_db())
app = web.Application()
app.add_routes([web.get('/', shorturl_get),
                web.get('/{name}', handler),
                web.post('/', shorturl_post)])
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app['db'] = db

if __name__ == '__main__':
    web.run_app(app)
