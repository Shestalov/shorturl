import os
import asyncio
from aiogram import Bot, Dispatcher, types
from db import setup_db
from bson import ObjectId
from bson.errors import InvalidId

BOT_TOKEN = os.environ.get('BOT_TOKEN')


async def start_handler(event: types.Message):
    await event.answer(
        f"Hello, {event.from_user.get_mention(as_html=True)} 👋!",
        parse_mode=types.ParseMode.HTML,
    )


async def url_handler(event: types.Message):
    db = await setup_db()
    collection = db['shorturl']
    user_url = event.text
    user_url_list = user_url.split('://')

    if len(user_url_list) == 1:
        obj_url = await collection.insert_one({'user_url': user_url_list[0], 'prefix': 'http'})
    else:
        obj_url = await collection.insert_one({'user_url': user_url_list[1], 'prefix': user_url_list[0]})
    url_id = obj_url.inserted_id
    await event.answer(str(url_id))


async def send_url(event: types.Message):
    url_id = event.text
    db = await setup_db()
    collection = db['shorturl']
    try:
        obj_url = await collection.find_one({'_id': ObjectId(url_id)})
        prefix = str(obj_url.get('prefix', 'http'))
        url_without_prefix = str(obj_url.get('user_url'))
        await event.answer(prefix + '://' + url_without_prefix)
    except InvalidId:
        await event.answer('Wrong url_id or URL is not correct (URL must start with hhtp)')


async def main():
    bot = Bot(token=BOT_TOKEN)
    try:
        disp = Dispatcher(bot=bot)
        disp.register_message_handler(start_handler, commands={"start", "restart"})
        disp.register_message_handler(url_handler, regexp='http.+')
        disp.register_message_handler(send_url, regexp='[a-z0-9]+')
        await disp.start_polling()
    finally:
        await bot.close()


asyncio.run(main())
