import redis
from telethon import TelegramClient, events

from app import api_id, api_hash

client = TelegramClient('lee7s', api_id, api_hash, proxy=("socks5", '127.0.0.1', 7890))
# client = TelegramClient('lee7s', api_id, api_hash)
#此处的some_name是一个随便起的名称，第一次运行会让你输入手机号和验证码，之后会生成一个some_name.session的文件，再次运行的时候就不需要反复输入手机号验证码了

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

async def main():
    # 获取个人信息
    # me = await client.get_me()

    # 打印个人信息 对象元组
    # print(me.stringify())

    # 打印用户名电话号码
    # print(me.username)
    # print(me.phone)

    # 打印所有的群和频道
    # async for dialog in client.iter_dialogs():
    #     print(dialog.name, 'has ID', dialog.id)

    # 给自己发消息 发送在收藏夹
    # await client.send_message('me', 'Hello, myself!')

    # 给指定id发消息 可以是群 人 机器人 频道
    # await client.send_message(-1001939724175, 'Hello!')

    # 可以给联系人发 电话号码
    # await client.send_message('+8617398827615', 'Hello, friend!')

    # 根据账号发送
    # await client.send_message('lee7s_7s', 'Testing Telethon!')

    # 可以发送markdown消息 并返回消息的对象
    # message = await client.send_message(
    #     'me',
    #     'This message has **bold**, `code`, __italics__ and a [nice website](https://example.com)!',
    #     link_preview=False
    # )
    # 可以用上面的这个消息对象获取信息
    # print(message.raw_text)
    # 根据消息对象回复消息
    # await message.reply('Cool!')

    # 发送文件文档等
    # await client.send_file('me', r'C:\Users\grade\Downloads\google5.png')

    min_id = redis_client.get('min_id') # 617070
    messages = client.iter_messages(-1001939724175, reverse=True, min_id=int(min_id))

    # 打印历史消息
    async for message in messages:
        redis_client.set('min_id', message.id)
        print(message.id, message.message)

        if message.message is not None:
            await client.send_message(-1001956313217, message)

        # 可以下载媒体内容
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media() # path是文件名
        #     print('File saved to', path)  # printed after download is done

@client.on(events.NewMessage)
async def my_event_handler(event):
    try:
        if event.is_channel and event.chat_id == -1001939724175:
            # print()
            await main()

    except Exception as e:
        pass

with client:
    # client.loop.run_until_complete(main())
    client.run_until_disconnected()

