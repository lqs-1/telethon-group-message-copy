import json

import requests
import redis
from telethon import TelegramClient, events
import time

from app.config import api_id, api_hash

client = TelegramClient('lee7s', api_id, api_hash, proxy=("socks5", '127.0.0.1', 7890))
# client = TelegramClient('lee7s', api_id, api_hash)
# 此处的some_name是一个随便起的名称，第一次运行会让你输入手机号和验证码，之后会生成一个some_name.session的文件，再次运行的时候就不需要反复输入手机号验证码了

# redis_client = redis.StrictRedis(host='75.127.13.112', port=6379, db=0)
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

async def do_copy_group_and_channel_message_news_to_target(resource_account: str, target_account: str):
    """
    同步更新新闻到频道或者群组
    :param resource_account: 被复制的频道或群组
    :param target_account:  目标频道或群组
    :return:
    """
    messages = await client.get_messages(f"@{resource_account}", ids=int(await latest_message_id(resource_account)))

    await client.send_message(f"@{target_account}", messages)






async def do_copy_group_and_channel_message_to_target_by_count(resource_account, target_account, user_id, count: str,
                                                               response_data: list, reverse: bool,
                                                               redis_index_key_word: str):
    """
    复制指定条数的消息到目标位置
    :param resource_account: 要复制的群或者频道id
    :param target_account: 目标群或者频道id
    :param user_id: 管理员id
    :param count: 发送多少条
    :param redis_index_key_word: redis中存放的消息起始id的key名字
    :param reverse: 是否倒序 true为从0来时 false为从最新消息开始
    :param response_data: 字典对象
    :return:
    """

    try:
        min_id = redis_client.get(f"{resource_account}_{redis_index_key_word}")
        messages = client.iter_messages(f"@{resource_account}", reverse=reverse, max_id=int(min_id))
    except Exception as e:
        redis_client.set(f"{resource_account}_{redis_index_key_word}", await latest_message_id(resource_account))
        messages = client.iter_messages(f"@{resource_account}", reverse=reverse,
                                        max_id=await latest_message_id(resource_account))

    flag = int(count)
    # 打印历史消息
    async for message in messages:
        if flag == 0:
            break
        redis_client.set(f"{resource_account}_{redis_index_key_word}", message.id)

        message_text = message.message

        if "http" in message_text or "https" in message_text or "@" in message_text:
            continue

        main_channel_str = response_data.get('main_channel')
        main_channel_obj = main_channel_str.split(":")

        all_channel_str = response_data.get('other_channel')
        all_channel_list = all_channel_str.split(",")

        if main_channel_obj[1] == target_account:

            channel_message_str = str()

            for channel in all_channel_list:
                channel_obj = channel.split("_")
                channel_message_str += f"\n[📣{channel_obj[0]}]({channel_obj[1]})"

            message.text = (f"`{message.text}`\n" +
                            "🎊" * 10 + "\n"
                                       # f"[💰点我赚佣金]({response_data.get('contact')})\n"
                                       f"[🛍️点我去商店]({response_data.get('account_shop_url')})" + channel_message_str
                            )
        else:
            channel_message_str = str()
            for channel in all_channel_list:
                channel_obj = channel.split("_")
                if not channel_obj[1] == f'https://t.me/{target_account}':
                    channel_message_str += f"\n[📣{channel_obj[0]}]({channel_obj[1]})"

            message.text = (f"`{message.text}`\n" +
                             "-" * 30 + "\n"
                                        # f"[💰点我赚佣金]({response_data.get('contact')})\n"
                                        f"[🛍️点我去商店]({response_data.get('account_shop_url')})\n"
                                        f"[📣{main_channel_obj[0]}](https://t.me/{main_channel_obj[1]})" + channel_message_str
                             )

        flag -= 1
        await client.send_message(f"@{target_account}", message)
        # await client.send_message(target_account, messages)
        await client.send_message(user_id, f"{message.id}, {message.text}" + "\n筛选通过 已发送到目的地")


async def do_copy_group_and_channel_message_to_target(resource_account, target_account, user_id, message_id: str,
                                                      response_data: list):
    """
    复制指定的消息到目标位置
    :param resource_account: 要复制的群或者频道id
    :param target_account: 目标群或者频道id
    :param user_id: 管理员id
    :param message_id: 消息id
    :param response_data: 字典对象

    :return:
    """

    # messages = client.iter_messages(resource_id, reverse=reverse, min_id=int(min_id))
    messages = await client.get_messages(f"@{resource_account}", ids=int(message_id))

    # print(messages)
    # message = messages[0]
    print(messages.id, messages.message, "筛选通过 已发送到目的地")

    main_channel_str = response_data.get('main_channel')
    main_channel_obj = main_channel_str.split(":")

    all_channel_str = response_data.get('other_channel')
    all_channel_list = all_channel_str.split(",")

    # 发到主频道
    if main_channel_obj[1] == target_account:

        channel_message_str = str()

        for channel in all_channel_list:
            channel_obj = channel.split("_")
            channel_message_str += f"\n[📣{channel_obj[0]}]({channel_obj[1]})"

        messages.text = (f"`{messages.text}`\n" +
                         "-" * 30 + "\n"
                                    # f"[💰点我赚佣金]({response_data.get('contact')})\n"
                                    f"[🛍️点我去商店]({response_data.get('account_shop_url')})" + channel_message_str
                         )
    else:

        channel_message_str = str()
        for channel in all_channel_list:
            channel_obj = channel.split("_")
            if not channel_obj[1] == f'https://t.me/{target_account}':
                channel_message_str += f"\n[📣{channel_obj[0]}]({channel_obj[1]})"

        messages.text = (f"`{messages.text}`\n" +
                         "-" * 30 + "\n"
                                    # f"[💰点我赚佣金]({response_data.get('contact')})\n"
                                    f"[🛍️点我去商店]({response_data.get('account_shop_url')})\n"
                                    f"[📣{main_channel_obj[0]}](https://t.me/{main_channel_obj[1]})" + channel_message_str
                         )

    await client.send_message(f"@{target_account}", messages)
    # await client.send_message(target_account, messages)
    await client.send_message(user_id, f"{messages.id}, {messages.text}" + "\n筛选通过 已发送到目的地")


async def do_copy_group_and_channel_message_to_admin(resource_account, target_id, redis_index_key_word: str,
                                                     reverse: bool, count: int):
    """
    把指定条数的消息发送给管理员 管理员好筛选
    :param resource_account: 要复制的群或者频道id
    :param target_id: 目标id 管理员id
    :param redis_index_key_word: redis中存放的消息起始id的key名字
    :param reverse: 是否倒序 true为从0来时 false为从最新消息开始
    :param count: 发送多少个
    :return:
    """

    try:
        min_id = redis_client.get(f"{resource_account}_{redis_index_key_word}")
        messages = client.iter_messages(f"@{resource_account}", reverse=reverse, max_id=int(min_id))
    except Exception as e:
        redis_client.set(f"{resource_account}_{redis_index_key_word}", await latest_message_id(resource_account))
        messages = client.iter_messages(f"@{resource_account}", reverse=reverse,
                                        max_id=await latest_message_id(resource_account))

    flag = count
    # 打印历史消息
    async for message in messages:
        if flag == 0:
            break
        redis_client.set(f"{resource_account}_{redis_index_key_word}", message.id)

        message_text = message.message

        message.text = ("title: " + message_text + "\n" + "msgId: " + str(
            message.id) + "\n" + "resource: " + "https://t.me/" + message.chat.username + f"/{message.id}" + "\n" + "put: " + "`put_" + str(
            message.id) + "`")
        # message.text = "[baidu](https://www.baidu.com)"
        if "http" in message_text or "https" in message_text or "@" in message_text:
            continue

        # if message.message is not None:
        flag -= 1
        print(message.id, message.message, "已发送给管理员筛选")
        await client.send_message(target_id, message, parse_mode='md')

        # 可以下载媒体内容
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media() # path是文件名
        #     print('File saved to', path)  # printed after download is done


async def do_copy_group_and_channel_latest_message_to_admin(resource_account, target_id, reverse: bool, count: int):
    """
    发送指定条数的最新消息给管理员
    :param resource_id: 要复制的群或者频道id
    :param target_id: 管理员id
    :param reverse: 是否倒序 true为从0来时 false为从最新消息开始
    :param count: 发送多少个
    :return:
    """

    messages = client.iter_messages(f"@{resource_account}", reverse=reverse,
                                    max_id=await latest_message_id(resource_account))

    flag = count
    # 打印历史消息
    async for message in messages:
        if flag == 0:
            break

        message_text = message.message

        message.text = ("title: " + message_text + "\n" + "msgId: " + str(
            message.id) + "\n" + "resource: " + "https://t.me/" + message.chat.username + f"/{message.id}" + "\n" + "put: " + "`put_" + str(
            message.id) + "`")
        # message.text = "[baidu](https://www.baidu.com)"
        if "http" in message_text or "https" in message_text or "@" in message_text:
            continue

        # if message.message is not None:
        flag -= 1
        print(message.id, message.message, "已发送给管理员筛选")
        await client.send_message(target_id, message, parse_mode='md')

        # 可以下载媒体内容
        # The method will return the path where the file was saved.
        # if message.photo:
        #     path = await message.download_media() # path是文件名
        #     print('File saved to', path)  # printed after download is done


async def do_copy_group_and_channel_all_message_to_target_by_count(resource_account, target_account, count: str,
                                                               response_data: list, reverse: bool,
                                                               redis_index_key_word: str):
    """
      复制指定条数的消息到目标位置
      :param resource_account: 要复制的群或者频道id
      :param target_account 目标群或者频道id
      :param count: 发送多少条
      :param redis_index_key_word: redis中存放的消息起始id的key名字
      :param reverse: 是否倒序 true为从0来时 false为从最新消息开始
      :param response_data: 字典对象
      :return:
      """

    try:
        min_id = redis_client.get(f"{resource_account}_{redis_index_key_word}")
        messages = client.iter_messages(f"@{resource_account}", reverse=reverse, max_id=int(min_id))
    except Exception as e:
        redis_client.set(f"{resource_account}_{redis_index_key_word}", await latest_message_id(resource_account))
        messages = client.iter_messages(f"@{resource_account}", reverse=reverse,
                                        max_id=await latest_message_id(resource_account))

    flag = int(count)
    # 打印历史消息
    async for message in messages:
        if flag == 0:
            break

        redis_client.set(f"{resource_account}_{redis_index_key_word}", message.id)

        message_text = message.message

        if ("http" in message_text or "https" in message_text or "@" in message_text or len(message.text) == 0):
            continue

        message.text = (f"`{message.text}`\n" +
                        "-" * 30 + "\n"
                                   f"[📣导航频道]({response_data.get('daohang_channel')})\n"
                                   f"[🛍️点我去商店]({response_data.get('account_shop_url')})"

                        )
        print(message.text)

        flag -= 1
        await client.send_message(target_account, message)

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


async def latest_message_id(session_account):
    '''
    获取会话中最新的消息id
    :param session_id: 会话id
    :return:
    '''
    messages = client.iter_messages(f"@{session_account}")
    async for message in messages:
        return message.id


@client.on(events.NewMessage)
async def my_event_handler(event):
    try:

        # 发起获取字典的请求
        response = requests.get("https://nobibibi.top/back/sysDict/requestDictByParent/telegram_copy_dict")
        response_data = response.json().get("parentDictAllSonDict")

        # 获取有权执行命令的用户id
        order_ids_str_list = response_data.get('order_ids').split(":")
        order_ids = list()
        for order_id in order_ids_str_list:
            order_ids.append(int(order_id))

        # 获取复制源和目标账号
        resource_account = response_data.get('resource_account')
        target_account = response_data.get('target_account')

        # 获取redis中存放的消息id的key
        redis_index_key_word = response_data.get('redis_index_key_word')
        if event.original_update.user_id in order_ids:
            message = event.original_update.message.split('_')
            if len(message) == 2:
                action = message[0]
                if action == 'get':
                    await do_copy_group_and_channel_message_to_admin(resource_account, event.chat_id,
                                                                     redis_index_key_word, False, int(message[1]))
                if action == 'ga':  # getAll:ga_10 发送最新的10条消息
                    await do_copy_group_and_channel_latest_message_to_admin(resource_account, event.chat_id, False,
                                                                            int(message[1]))
                if action == 'put':
                    await do_copy_group_and_channel_message_to_target(resource_account, target_account, event.chat_id,
                                                                      message[1], response_data)
                    # await do_copy_group_and_channel_message_to_target(resource_account, event.chat_id, event.chat_id, message[1], response_data)
                if action == 'putn':
                    await do_copy_group_and_channel_message_to_target_by_count(resource_account, target_account,
                                                                               event.chat_id,
                                                                               message[1], response_data, False,
                                                                               redis_index_key_word)
                if action == 'putna':
                    update_all_channels = response_data.get('update_channels_all_name').split(":")
                    for update_channel in update_all_channels:
                        await do_copy_group_and_channel_all_message_to_target_by_count(resource_account, update_channel,
                                                                                   message[1], response_data, False,
                                                                                   redis_index_key_word)
                if action == 'msg' and message[1] == 'resource':
                    dialogs = await client.get_dialogs()
                    result_channel = str()
                    count = 1
                    for dialog in dialogs:
                        if dialog.is_channel or dialog.is_group:
                            result_channel += f"{count} = {dialog.title} : @{dialog.message.chat.username}\n\n"
                            count += 1
                    await client.send_message(event.chat_id, result_channel)

            else:
                await client.send_message(event.chat_id, f"使用格式:\n"
                                                         f"`get_`: 获取多少个\n"
                                                         f"`ga_`: 获取最新的多少个\n"
                                                         f"`put_`: 推送消息\n"
                                                         f"`putn_`: 推送消息指定个数\n"
                                                         f"`putna_`: 推送消息指定个数到所有频道\n"
                                                         f"`msg_resource`: 获取所有的群组和频道")

    except Exception as e:
        try:
            auto_update_chat = dict()
            auto_update_chat_keys = list()
            auto_update_chat_str = response_data.get('auto_update_chat')
            auto_update_chat_str_list = auto_update_chat_str.split(",")

            for auto_update_chat_str_one in auto_update_chat_str_list:
                auto_update_chat_resource_target = auto_update_chat_str_one.split(":")
                auto_update_chat_keys.append(auto_update_chat_resource_target[0])
                auto_update_chat.update({auto_update_chat_resource_target[0]: auto_update_chat_resource_target[1]})

            if event.chat.username in auto_update_chat_keys:
                await do_copy_group_and_channel_message_news_to_target(event.chat.username,
                                                                   auto_update_chat.get(event.chat.username))
        except Exception as e2:
            pass


async def test():
    dialogs = await client.get_dialogs()

    # 创建一个字典来存储每个文件夹的聊天
    folder_chats = {}

    # 遍历所有对话，并根据文件夹 ID 进行分组
    for dialog in dialogs:
        if dialog.is_channel and not dialog.is_group:
            print(dialog.id, await latest_message_id(dialog.id), dialog.title)


with client:
    # client.loop.run_until_complete(do_copy_group_and_channel_message_to_target_loop())
    # client.loop.run_until_complete(send_private_message("https://t.me/xylxf777", "https://t.me/av_share_channel 欢迎来这个频道看骚逼!每日更新"))
    # client.loop.run_until_complete(test())
    client.run_until_disconnected()
