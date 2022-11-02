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
    user_url_list = user_url.split('://')
    database = request.app["db"]
    collection = database['shorturl']
    # if url without http
    if len(user_url_list) == 1:
        url_record = await collection.insert_one({'user_url': user_url_list[0], 'prefix': 'http'})
    else:
        url_record = await collection.insert_one({'user_url': user_url_list[1], 'prefix': user_url_list[0]})
    return {'short_url': url_record.inserted_id}


async def handler(request):
    name_url = request.match_info.get('link')
    database = request.app['db']
    collection = database['shorturl']
    obj_url = await collection.find_one({'_id': ObjectId(name_url)})
    url_without_prefix = obj_url['user_url']
    prefix = obj_url.get('prefix', 'http')
    return web.HTTPFound(prefix + '://' + url_without_prefix)


db = asyncio.run(setup_db())
app = web.Application()
app.add_routes([web.get('/', shorturl_get),
                web.get('/{link}', handler),
                web.post('/', shorturl_post)])
aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader('templates'))
app['db'] = db

if __name__ == '__main__':
    web.run_app(app)
