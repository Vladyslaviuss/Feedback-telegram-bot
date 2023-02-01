from pyrogram import Client, filters, enums
import logging
from configs import Config as C

# This Is Logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logging.getLogger("pyrogram").setLevel(logging.WARNING)

# Import From Framework
# from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

from pyrogram.types import *
from database.broadcast import broadcast
from database.verifier import handle_user_status
from database.database import Database

LOG_GROUP = C.LOG_GROUP
AUTH_USERS = C.AUTH_USERS
DB_URL = C.DB_URL
DB_NAME = C.DB_NAME

db = Database(DB_URL, DB_NAME)


bot = Client('Feedback bot',
             api_id=C.API_ID,
             api_hash=C.API_HASH,
             bot_token=C.BOT_TOKEN)


owner_id=C.OWNER_ID

LOG_TEXT = "ID: <code>{}</code>\nFirst Name: <a href='tg://user?id={}'>{}{}</a>\nDC ID: <code>{}</code>"

IF_TEXT = "<b>Message from:</b> {}\n<b>Name:</b> {}\n\n{}"

IF_CONTENT = "<b>Message from:</b> {} \n<b>Name:</b> {}"


@bot.on_message((filters.private | filters.group))
async def _(bot, cmd):
    await handle_user_status(bot, cmd)

# Команда, которая оповещает о том, что кто-то нажал на старт и начал пользоваться ботом. Работает в приватке и в группе
# New USER notification должен отсылаться только в группу и второй месседж с DC ID c другой функции тоже
@bot.on_message(filters.command('start') & filters.private)
async def start(bot, message):
    # это юзер айди, а не чат айди, потом исправить
    user_id = message.from_user.id
    user_name = message.from_user.username
    # Adding to DB
    if not await db.is_user_exist(user_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(id=user_id, username=user_name)
        await bot.send_message(
            LOG_GROUP,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
        return

    # 
    ban_status = await db.get_ban_status(user_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**")
        return

    await bot.send_message(
        chat_id=-1001831216052,
        text=f'Пользователь: {message.chat.first_name} {message.chat.last_name} / {message.chat.username} из чата {message.chat.id} только что использовал команду /start',
        parse_mode=enums.ParseMode.HTML
    )
    await message.reply_text(text=f"Приветствую Вас, {message.chat.first_name}! Задайте любой интересующий Вас вопрос.")



# Переслать всем желаемое сообщение
# Работает с группы
# Фильтр только с определенной группы сделать нужно
@bot.on_message(filters.group & filters.command("broadcast"))
async def broadcast_handler_open(_, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if m.reply_to_message is None:
        await m.delete()
        return
    await broadcast(m, db)



# Выводит статистку из БД
# Фильтр только с определенной группы сделать нужно
@bot.on_message(filters.group & filters.command("stats"))
async def sts(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    await m.reply_text(
        text=f"**Total Users in Database 📂:** `{await db.total_users_count()}\n \n{await  db.get_user_list()}`\n\n**Total Users with Notification Enabled 🔔 :** `{await db.total_notif_users_count()}`",
        parse_mode=enums.ParseMode.HTML,
        quote=True,
    )

@bot.on_message(filters.group & filters.command("set_status_to"))
async def set_status(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) < 2:
        await m.reply_text(
            f"Неправильное использование команды!!.",
            quote=True,
        )
        return
    try:
        user_name = str(m.command[1])
        status = " ".join(m.command[2:])
        # ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Setting status {status} for user @{user_name}"

        # if user_id == owner_id:
        #     await message.reply_text("**You can Ban The Owner Vro")
        #     return
        k = await db.set_client_status(username=user_name, client_status=status)
        if k == True:
            await m.reply_text(f"СТАТУС УСПЕШНО ЗАДАН!!.", quote=True)
        else:
            await m.reply_text(f"СТАТУС НЕ ЗАДАН ЧЕРЕЗ ОШИБКУ В БД!!.", quote=True)
    except Exception:
        await m.reply_text(f"Другая ошибка случилась", quote=True)




# Работает только в чате с ботом (Команда для БАНА)
@bot.on_message(filters.group & filters.command("ban_user"))
async def ban(c, m):
    # только особые юзеры могут вызвать эту команду
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to ban 🛑 any user from the bot 🤖.\n\nUsage:\n\n`/ban_user user_id ban_duration ban_reason`\n\nEg: `/ban_user 1234567 28 You misused me.`\n This will ban user with id `1234567` for `28` days for the reason `You misused me`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        ban_duration = int(m.command[2])
        ban_reason = " ".join(m.command[3:])
        ban_log_text = f"Banning user {user_id} for {ban_duration} days for the reason {ban_reason}."
        
        if user_id == owner_id:
            await message.reply_text("**You can Ban The Owner Vro")
            return
        try:
            await c.send_message(
                user_id,
                f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**",
            )
            ban_log_text += "\n\nUser notified successfully!"
        except BaseException:
            traceback.print_exc()
            ban_log_text += (
                f"\n\n ⚠️ User notification failed! ⚠️ \n\n`{traceback.format_exc()}`"
            )
        await db.ban_user(user_id, ban_duration, ban_reason)
        print(ban_log_text)
        await m.reply_text(ban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True,
        )



# Работает и в приватке и в личках (Команда для АНБАНА)
@bot.on_message((filters.group | filters.private) & filters.command("unban_user"))
async def unban(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    if len(m.command) == 1:
        await m.reply_text(
            f"Use this command to unban 😃 any user.\n\nUsage:\n\n`/unban_user user_id`\n\nEg: `/unban_user 1234567`\n This will unban user with id `1234567`.",
            quote=True,
        )
        return

    try:
        user_id = int(m.command[1])
        unban_log_text = f"Unbanning user 🤪 {user_id}"

        try:
            await c.send_message(user_id, f"Your ban was lifted!")
            unban_log_text += "\n\n✅ User notified successfully! ✅"
        except BaseException:
            traceback.print_exc()
            unban_log_text += (
                f"\n\n⚠️ User notification failed! ⚠️\n\n`{traceback.format_exc()}`"
            )
        await db.remove_ban(user_id)
        print(unban_log_text)
        await m.reply_text(unban_log_text, quote=True)
    except BaseException:
        traceback.print_exc()
        await m.reply_text(
            f"⚠️ Error occoured ⚠️! Traceback given below\n\n`{traceback.format_exc()}`",
            quote=True,
        )



# Может быть вызвана с лички с ботом и с группы админов (Команда для вывода информации о банах)
@bot.on_message((filters.group | filters.private) & filters.command("banned_users"))
async def _banned_usrs(c, m):
    if m.from_user.id not in AUTH_USERS:
        await m.delete()
        return
    all_banned_users = await db.get_all_banned_users()
    banned_usr_count = 0
    text = ""
    async for banned_user in all_banned_users:
        user_id = banned_user["id"]
        ban_duration = banned_user["ban_status"]["ban_duration"]
        banned_on = banned_user["ban_status"]["banned_on"]
        ban_reason = banned_user["ban_status"]["ban_reason"]
        banned_usr_count += 1
        text += f"> **User_id**: `{user_id}`, **Ban Duration**: `{ban_duration}`, **Banned on**: `{banned_on}`, **Reason**: `{ban_reason}`\n\n"
    reply_text = f"Total banned user(s) 🤭: `{banned_usr_count}`\n\n{text}"
    if len(reply_text) > 4096:
        with open("banned-users.txt", "w") as f:
            f.write(reply_text)
        await m.reply_document("banned-users.txt", True)
        os.remove("banned-users.txt")
        return
    await m.reply_text(reply_text, True)

    return


# Функция реагирует на текст и кидает его мне в приватку, чтобы я отвечал на вопрос.
# Реагирует только на текст, полученный в боте. Не реагирует на текст с группы.
@bot.on_message(filters.private & filters.text)
async def receive_text_from_user(bot, message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    # Adding to DB
    if not await db.is_user_exist(user_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(id=user_id, username=user_name)
        await bot.send_message(
            LOG_GROUP,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
    ban_status = await db.get_ban_status(user_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**")
        return
      
    if message.from_user.id == owner_id:
        await reply_to_user_by_text(bot, message)
        return
    info = await bot.get_users(user_ids=message.from_user.id)
    reference_id = int(message.chat.id)
    # await bot.send_message(
    #     chat_id=-1001831216052, # Захардкодил группу, в которую буут приходить сообщения с бота
    #     text=IF_TEXT.format(reference_id, info.first_name, message.text),
    #     parse_mode=enums.ParseMode.HTML
    # )
    await bot.forward_messages(
        chat_id=-1001831216052,
        from_chat_id=message.chat.id,
        message_ids=message.id,
    )


# Функция реагирует на медиа и кидает его мне в приватку, чтобы я отвечал на вопрос.
# Баги - Я отвечаю любым видом сообщения и оно работает, но есть пользователь скидывает мне стикер - я не вижу от кого. Вижу аудио, видео, емодзи
# Если пользователь скидывает мне реакцию, я вижу просто пересланное мной же сообщение
@bot.on_message(filters.private & filters.media)
async def receive_media_from_user(bot, message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    # Adding to DB
    if not await db.is_user_exist(user_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(id=user_id, username=user_name)
        await bot.send_message(
            LOG_GROUP,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
    ban_status = await db.get_ban_status(user_id)
    is_banned = ban_status['is_banned']
    ban_duration = ban_status['ban_duration']
    ban_reason = ban_status['ban_reason']
    if is_banned is True:
        await message.reply_text(f"You are Banned 🚫 to use this bot for **{ban_duration}** day(s) for the reason __{ban_reason}__ \n\n**Message from the admin 🤠**")
        return

    if message.from_user.id == owner_id:
        await replay_to_user_by_media(bot, message)
        return
    info = await bot.get_users(user_ids=message.from_user.id)
    reference_id = int(message.chat.id)
    # await bot.copy_message(
    #     chat_id=-1001831216052,
    #     from_chat_id=message.chat.id,
    #     message_id=message.id,
    #     caption=IF_CONTENT.format(reference_id, info.first_name),
    #     parse_mode=enums.ParseMode.HTML
    # )
    await bot.forward_messages(
        chat_id=-1001831216052,
        from_chat_id=message.chat.id,
        message_ids=message.id,
    )




@bot.on_message(filters.user(owner_id) & filters.text)
async def reply_to_user_by_text(bot, message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    # Adding to DB
    if not await db.is_user_exist(user_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(id=user_id, username=user_name)
        await bot.send_message(
            LOG_GROUP,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
    
    reference_id = True
    if message.reply_to_message is not None:
        file = message.reply_to_message
        try:
            reference_id = file.text.split()[2]
        except Exception:
            pass
        try:
            reference_id = file.caption.split()[2]
        except Exception:
            pass
        await bot.send_message(
            chat_id=message.reply_to_message.forward_from.id,
            #from_chat_id=message.chat.id,
            #message_id=message.message_id,
            text=message.text
        )


# Поменять, чтоб не только овнер мог отвечать
@bot.on_message(filters.user(owner_id) & filters.media)
async def replay_to_user_by_media(bot, message):
    user_id = message.from_user.id
    user_name = message.from_user.username
    # Adding to DB
    if not await db.is_user_exist(user_id):
        data = await bot.get_me()
        BOT_USERNAME = data.username
        await db.add_user(id=user_id, username=user_name)
        await bot.send_message(
            LOG_GROUP,
            f"#NEWUSER: \n\nNew User [{message.from_user.first_name}](tg://user?id={message.from_user.id}) started @{BOT_USERNAME} !!",
        )
    reference_id = True
    if message.reply_to_message is not None:
        file = message.reply_to_message
        try:
            reference_id = file.text.split()[2]
        except Exception:
            pass
        try:
            reference_id = file.caption.split()[2]
        except Exception:
            pass
        await bot.copy_message(
            chat_id=message.reply_to_message.forward_from.id,
            from_chat_id=message.chat.id,
            message_id=message.id,
            parse_mode=enums.ParseMode.HTML
        )


bot.run()
