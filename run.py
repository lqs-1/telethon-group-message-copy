import redis
from telethon import TelegramClient, events
import time

from app.config import api_id, api_hash

client = TelegramClient('lee7s', api_id, api_hash, proxy=("socks5", '127.0.0.1', 7890))
# client = TelegramClient('lee7s', api_id, api_hash)
#此处的some_name是一个随便起的名称，第一次运行会让你输入手机号和验证码，之后会生成一个some_name.session的文件，再次运行的时候就不需要反复输入手机号验证码了

redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

# async def main():
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

async def copy_group_and_channel_message(resource_id, target_id, redis_index_key_word: str, reverse: bool):
    """
    :param resource_id: 要复制的群或者频道id
    :param target_id: 目标群或者频道id
    :param redis_index_key_word: redis中存放的消息起始id的key名字
    :param reverse: 是否倒序 true为从0来时 false为从最新消息开始
    :return:
    """


    min_id = redis_client.get(redis_index_key_word)  # 91 1108
    # messages = client.iter_messages(resource_id, reverse=reverse, min_id=int(min_id))
    messages = client.iter_messages(resource_id, reverse=reverse, max_id=int(min_id))

    flag = 0
    # 打印历史消息
    async for message in messages:
        redis_client.set(redis_index_key_word, message.id)
        print(message.id, message.message)

        if flag == 10:
            flag = 0
            time.sleep(60*60*12)

        message_text = message.message
        if "http" in message_text or "https" in message_text or "@" in message_text:
            continue

        if message.message is not None:
            flag += 1

            await client.send_message(target_id, message)

        # 可以下载媒体内容
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media() # path是文件名
        #     print('File saved to', path)  # printed after download is done


async def order_copy_group_and_channel_message(resource_id, target_id, redis_index_key_word: str, reverse: bool, count: int):
    """
    :param resource_id: 要复制的群或者频道id
    :param target_id: 目标群或者频道id
    :param redis_index_key_word: redis中存放的消息起始id的key名字
    :param reverse: 是否倒序 true为从0来时 false为从最新消息开始
    :param count: 发送多少个
    :return:
    """


    min_id = redis_client.get(redis_index_key_word)  # 91 1108
    # messages = client.iter_messages(resource_id, reverse=reverse, min_id=int(min_id))
    messages = client.iter_messages(resource_id, reverse=reverse, max_id=int(min_id))

    flag = count
    # 打印历史消息
    async for message in messages:
        if flag == 0:
            break
        redis_client.set(redis_index_key_word, message.id)

        message_text = message.message
        if "http" in message_text or "https" in message_text or "@" in message_text:
            continue

        if message.message is not None:
            flag -= 1
            print(message.id, message.message, "已发送")
            await client.send_message(target_id, message)

        # 可以下载媒体内容
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media() # path是文件名
        #     print('File saved to', path)  # printed after download is done

async def send_private_message(group_link: str, message_text: str):
    """
    指定公开群聊 给里面的人发私信 需要账号进入
    :param group_link: 群的链接
    :param message_text: 私聊文本
    :return:
    """

    # target_user = await client.get_entity("lee7s_7s")
    # await client.send_message(target_user, "message_text")
    group_entity = await client.get_entity(group_link)
    chat_members = await client.get_participants(group_entity)

    # 遍历成员列表并发送私信
    for member in chat_members:
        if member.bot:
            time.sleep(20)
            continue  # 跳过机器人成员
        username = member.username
        if not username:
            time.sleep(70)
            continue  # 跳过没有用户名的成员
        # 获取目标用户的信息
        try:
            target_user = await client.get_entity(username)
            print(f"正在给用户  {username}  发送邀请")
            time.sleep(128)
            await client.send_message(target_user, message_text)
        except ValueError:
            print("找不到目标用户")
            time.sleep(34)
            continue


@client.on(events.NewMessage)
async def my_event_handler(event):


    try:
        # if event.is_channel and event.chat_id == -1001436263897:
        #     # print()
        #     await copy_group_and_channel_message(-1001436263897, -1002130678124, "min_id")

        if event.original_update.user_id in [5060527090, 6967203577]:
            message = event.original_update.message.split('_')
            if len(message) == 2:
                await order_copy_group_and_channel_message(-1001436263897, -1002130678124, "min_id", False, int(message[1]))

    except Exception as e:
        pass

with client:
    # client.loop.run_until_complete(copy_group_and_channel_message(-1001436263897, -1002130678124, "min_id", False))
    # client.loop.run_until_complete(send_private_message("https://t.me/xylxf777", "https://t.me/av_share_channel 欢迎来这个频道看骚逼!每日更新"))
    client.run_until_disconnected()

