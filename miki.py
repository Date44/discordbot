import datetime
import tracemalloc
import random2
# from chatterbot import ChatBot
from discord import app_commands
import configparser
import os
import time
import discord
import sqlite3

from discord.ui import View, button, Button


async def menu(
        interaction: discord.Interaction,
        current: str,
) -> list[app_commands.Choice[str]]:
    menu = ["Мафия", "Бункер", "Алиас/Шляпа", "Крокодил", "GarticPhone", "JackBox", "Codenames", "Намёк понял", "Шпион",
            "Кто я?", "Криминалист"]
    return [
        app_commands.Choice(name=string, value=string)
        for string in menu if current.lower() in string.lower()
    ]


def check123(id, type: str):
    a = True
    cur.execute("SELECT ? FROM Users WHERE name = ?", (type, id,))
    timeban = cur.fetchone()
    time = datetime.datetime.now()
    time = time.strftime('%H:%M:%S %d-%m-%Y')
    time = check_time(str(time))
    timeban = check_time(str(timeban[0]))
    i = 0
    while a:
        if i < len(time) + 1:
            if time[i] == timeban[i]:
                i = i + 1
            elif time[i] > timeban[i]:
                cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (0, id))
                con.commit()
                a = False
            elif time[i] < timeban[i]:
                a = False
        else:
            a = False


def check_time(time2):
    # channel = Bot.get_channel(1007954919090831360)
    # 16:49:28 02-04-2023
    H = time2[0:2]
    M = time2[3:5]
    S = time2[6:8]
    d = time2[9:11]
    m = time2[12:14]
    Y = time2[15:19]
    # print(f"123 {H}:{M}:{S} {d}-{m}-{Y}")
    return [Y, m, d, H, M, S]


def create_db():
    cur.execute("CREATE TABLE Users(name UNIQUE, money, timeout, ban_timeout, mute_timeout, warn, marry)")
    cur.execute("CREATE TABLE Shop(id INTEGER UNIQUE PRIMARY KEY, name, description, price)")


def create_profil(id):
    data = [((id), 0, 0, 0, 0, 0, 0), ]
    cur.executemany("INSERT INTO Users VALUES(?, ?, ?, ?, ?, ?, ?)", data)
    con.commit()
    cur.execute("SELECT * FROM Users WHERE name = ?", (id,))
    return cur.fetchone()


if not os.path.exists('Miki.db'):
    con = sqlite3.connect("Miki.db")
    cur = con.cursor()
    create_db()
else:
    con = sqlite3.connect("Miki.db")
    cur = con.cursor()


# config
def create_config():
    id_chat = "0000000000000000000"
    config = configparser.ConfigParser()

    config.add_section('Login')
    config.add_section('Protect')
    config.add_section('Log')
    config.add_section('Event')

    config.set('Login', 'token', '')
    config.set('Login', 'command_chat', id_chat)
    config.set('Login', 'guild_id', id_chat)
    config.set('Protect', 'white_list', "[281772955690860544, ]")
    config.set('Log', 'log_chat', id_chat)
    config.set('Event', 'event_chat', id_chat)

    with open('config.cfg', 'w') as configfile:
        config.write(configfile)


def read_config():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    cfg = {
        "token": config.get('Login', 'token'),
        "command_chat": config.get('Login', 'command_chat'),
        "guild_id": config.get('Login', 'guild_id'),
        "white_list": config.get('Protect', 'white_list'),
        "log_chat": config.get('Log', 'log_chat'),
        "event_chat": config.get('Event', 'event_chat')
    }
    return cfg


if not os.path.exists('config.cfg'):
    create_config()
    time.sleep(5)
    cfg = read_config()
else:
    cfg = read_config()
token = cfg["token"]
bot_chat = int(cfg["command_chat"])
white_list = cfg["white_list"]
log_chat = int(cfg["log_chat"])
guild = int(cfg["guild_id"])
event_chat = cfg["event_chat"]
colors = {
    'DarkRed': 0x8B0000,
    'Red': 0xFF0000,
    'DarkOrange': 0xFF8C00,
    'Yellow': 0xFFFF00,
    'Gold': 0xFFD700,
    'DarkBlue': 0x00008B,
    'Blue': 0x0000FF,
    'Cyan': 0x00FFFF,
    'Lime': 0x00FF00,
    'LimeGreen': 0x32CD32,
    'OrangeRed': 0xFF4500
}
# Настройка бота

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
Bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(Bot)
# chatbot = ChatBot("Chatpot")
tracemalloc.start()


# 1. Время логов
def getTime(time):
    if time[-1] == "d" or time[-1] == "D":
        time = datetime.datetime.now() + datetime.timedelta(days=int(time[0:-1]))
    elif time[-1] == "m" or time[-1] == "M":
        time = datetime.datetime.now() + datetime.timedelta(minutes=int(time[0:-1]))
    elif time[-1] == "h" or time[-1] == "H":
        time = datetime.datetime.now() + datetime.timedelta(hours=int(time[0:-1]))
    elif time[-1] == "s" or time[-1] == "S":
        time = datetime.datetime.now() + datetime.timedelta(seconds=int(time[0:-1]))
    elif time[-1] == "w" or time[-1] == "W":
        time = datetime.datetime.now() + datetime.timedelta(weeks=int(time[0:-1]))
    else:
        time = datetime.datetime.now()
    return time.strftime('%H:%M:%S %d-%m-%Y')


def getTime2():
    time = datetime.datetime.now()
    return time.strftime("%d-%m-%Y")


def getTime3():
    time = "13:52:24 18-03-2023"
    time = datetime.datetime.strptime(time, "%H:%M:%S %d-%m-%Y")
    time1 = datetime.datetime.now() + datetime.timedelta(days=1)
    time1 = time1.strftime("%Y-%m-%d %H:%M:%S")


@Bot.event
async def on_message(message):
    global colors
    # await channel.send(message.reference) ответ
    black_listbot = [str(Bot.user.id), ]
    text = message.content
    channel = Bot.get_channel(int(message.channel.id))
    if text[0:4] == "!del":
        text = text.replace("!del ", "")
        async for i in channel.history(limit=int(text) + 1):
            await i.delete()
    # elif text[0:4] == "!123":
    #     time4 = datetime.datetime.now() + datetime.timedelta(hours=2)
    #     time4 = time4.strftime("%H:%M:%S %d-%m-%Y")
    #     time1 = "17:10:54 21-03-2023"
    #     await channel.send(f"Сейчас = {time4}")
    #     await message.delete()
    #     await check_time(time1)
    #     # getTime3()
    #     # event = discord.ScheduledEvent(start_time=getTime3())
    #     # event.channel=text[4:]
    elif str(message.author.id) not in black_listbot:
        # if message.channel.id == 1075443989089636472:
        # await channel.send(chatbot.get_response(str(message.content)))
        if message.channel.id == bot_chat:
            if text[0:5] == "!stop":
                await message.delete()
                exit()
            # elif text[0:5] == "!text":
            #     print("123")
            #     text = text.replace("!text ", "")
            #     text = text.split("\n")
            #     text2 = text[0].split(' ')
            #     color = colors[text2[0]]
            #     channel = Bot.get_channel(int(text2[1].replace('<#', '').replace('>', '')))
            #     del text[0]
            #     if message.attachments:
            #         for attach in message.attachments:
            #             await attach.save(f"foto/{attach.filename}")
            #             embed = discord.Embed(color=color)
            #             embed.set_image(url=attach.url)
            #             await channel.send(embed=embed)
            #     else:
            #         content = '\n'.join(text)
            #         embed = discord.Embed(description=content, color=color)
            #         await channel.send(embed=embed)
            elif text[0:5] == "!text":
                print("12342")
                text = text.replace("!text ", "")
                text = text.split("\n")
                text2 = text[0].split(' ')
                color2 = text2[0] in colors
                content = '\n'.join(text)
                print(content)
                if color2:
                    color = colors[text2[0]]
                    channel = Bot.get_channel(int(text2[1].replace('<#', '').replace('>', '')))
                    del text[0]
                    if message.attachments:
                        for attach in message.attachments:
                            await attach.save(f"foto/{attach.filename}")
                            embed = discord.Embed(description=content, color=color)
                            embed.set_image(url=attach.url)
                            await channel.send(embed=embed)
                    else:
                        embed = discord.Embed(description=content, color=color)
                        await channel.send(embed=embed)
                else:
                    await message.reply(f"Нету такого цвета '{text2[0]}'")
            elif text[0:5] == "!edit":
                text = text.replace("!edit ", "").split("\n")
                color2 = text[0].split(" ")[0] in colors
                if color2:
                    color = colors[text[0].split(" ")[0]]
                    text2 = text[0].split(" ")[1].replace("https://discord.com/channels/1007951389198127195/",
                                                          "").replace(' ', '').split('/')
                    channel = Bot.get_channel(int(text2[0]))
                    del text[0]
                    async for i in channel.history():
                        if i.id == int(text2[1]):
                            content = '\n'.join(text[1:])
                            embed = discord.Embed(title=text[0], description=content, color=color)
                            await i.edit(embed=embed)
                            break
                        else:
                            pass
        if message.channel.id == 1007954919090831360:
            channel = Bot.get_channel(int(message.channel.id))
            if str(message.author.id) not in black_listbot:
                text = message.content
                channel = message.channel
                if text == "гей":
                    await channel.send(text)


@tree.command(name="info", description="Command info/Информация о командах", guild=discord.Object(id=guild))
async def info(interaction):
    info = ("\n"
            "    **Список доступных цветов:**\n"
            "    DarkRed, Red, DarkOrange, Yellow, Gold, DarkBlue, Blue, Cyan, Lime, LimeGreen, OrangeRed\n"
            "\n"
            "    **Список доступных команд:**\n"
            "    **!del** [количиство] - удаляет сообщения\n"
            "    **!text** [цвет] [#канал] - создать пост\n"
            "    `заголовок`\n"
            "    `текст`\n"
            "    **!edit** [цвет] [ссылка на сообщение] - изменить пост\n"
            "    `заголовок`\n"
            "    `текст`\n"
            "    **!stop** - перезапустить бота\n"
            "    ")
    embed = discord.Embed(title="Инфо", description=info, color=0x1)
    await interaction.response.send_message(embed=embed)


@tree.command(name="бан", description="забанить пользователя", guild=discord.Object(id=guild))
async def ban(interaction, пользователь: discord.Member, время: str, причина: str):
    channel = Bot.get_channel(log_chat)
    guild1 = Bot.get_guild(1007951389198127195)
    role_ban = guild1.get_role(1085655121775579187)
    text = f'Пользователь <@{пользователь.id}> | `{пользователь}` был забанен на сервере, время: {время}, причина: {причина}'
    await пользователь.add_roles(role_ban, reason=причина)
    await channel.send(text)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (пользователь.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(пользователь.id)
    cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (getTime(время), interaction.user.id))
    con.commit()


@tree.command(name="разбан", description="Снять бан", guild=discord.Object(id=guild))
async def unban(interaction, пользователь: discord.Member, причина: str):
    channel = Bot.get_channel(log_chat)
    guild1 = Bot.get_guild(1007951389198127195)
    role_ban = guild1.get_role(1085655121775579187)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (пользователь.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(interaction.user.id)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    await пользователь.remove_roles(role_ban, reason=причина)
    cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (0, interaction.user.id))
    con.commit()
    text = f"Модератор <@{interaction.user.id}> | `{interaction.user}` снял бан с пользователя: <@{пользователь.id}> | `{пользователь}`  Причина: {причина}"
    await channel.send(text)


@tree.command(name="мут", description="mute user", guild=discord.Object(id=guild))
async def mute(interaction, пользователь: discord.Member, время: str, причина: str):
    channel = Bot.get_channel(log_chat)
    guild1 = Bot.get_guild(1007951389198127195)
    role_mute = guild1.get_role(1085655720311132230)
    text = f'Пользователь <@{пользователь.id}> | `{пользователь}` был замьючен на сервере, время: {время}, причина: {причина}'
    await пользователь.add_roles(role_mute, reason=причина)
    cur.execute("SELECT timeout FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(пользователь.id)
    await channel.send(text)


@tree.command(name="счёт", description="Проверить счёт", guild=discord.Object(id=guild))
async def money(interaction):
    channel = Bot.get_channel(int(interaction.channel.id))
    guild1 = Bot.get_guild(1007951389198127195)
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(interaction.user.id)
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    embed = discord.Embed(
        description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nНа вашем счету: {all[0]} :coin:""",
        color=0x1)
    embed.set_thumbnail(url=interaction.user.avatar)
    embed.set_author(name="Пользователь")
    # async with aiohttp.ClientSession() as session: webhook = discord.Webhook.from_url(
    # url='https://discord.com/api/webhooks/1008413933847191573
    # /NcCm_HNnRoYjaqrWyGgAxhglXfwL_CVQVCYvyHfKkh_tyoSxz3SjVkLE3C0UV66oREAx', session=session) await webhook.send(
    # embed=embed, username=interaction.user.name, avatar_url=interaction.user.avatar.url)
    await interaction.response.send_message(embed=embed)


@tree.command(name="перевести", description="перевести коины", guild=discord.Object(id=guild))
async def move(interaction, пользователь: discord.Member, сумма: int):
    data = [((interaction.user.id), 0, 0, 0, 0, 0), ]
    data1 = [((пользователь.id), 0, 0, 0, 0, 0), ]
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    cur.execute("SELECT money FROM Users WHERE name = ?", (пользователь.id,))
    all1 = cur.fetchone()
    if all is None:
        all = create_profil(interaction.user.id)
    if all1 is None:
        all1 = create_profil(пользователь.id)
    if all[0] >= сумма:
        if сумма == 0:
            embed = discord.Embed(
                description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nКак мне кажется от нуля нечего не изменится""",
                color=0x1)
        elif сумма < 0:
            embed = discord.Embed(
                description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nЧисло должно быть положительным""",
                color=0x1)
        else:
            embed = discord.Embed(
                description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nВы перевели {сумма} :coin: пользователю <@{пользователь.id}>| `{пользователь}`""",
                color=0x1)
        cur.execute("UPDATE Users SET money = ? WHERE name = ?", (all[0] - сумма, interaction.user.id))
        con.commit()
        cur.execute("UPDATE Users SET money = ? WHERE name = ?", (all1[0] + сумма, пользователь.id))
        con.commit()
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nу вас недостаточно средств """,
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="награда", description="Ежедневная награда", guild=discord.Object(id=guild))
async def reward(interaction):
    data = [((interaction.user.id), 0, 0, 0, 0, 0), ]
    cur.execute("SELECT money, timeout FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    if all == None:
        create_profil(interaction.user.id)
        cur.execute("SELECT money, timeout FROM Users WHERE name = ?", (interaction.user.id,))
        all = cur.fetchone()
    if all[1] != getTime2() or all[0] == 0:
        new_valui = int(all[0]) + 100
        cur.execute("UPDATE Users SET money = ?, timeout = ? WHERE name = ?",
                    (new_valui, getTime2(), interaction.user.id))
        con.commit()
        embed = discord.Embed(
            description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nВы получили 100 :coin: Следующую награду, можно будет получить завтра.""",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\nНаграда была уже получена, следующую награду, можно будет получить завтра.""",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="наказания", description="просмотр профиля", guild=discord.Object(id=guild))
async def check(interaction, пользователь: discord.Member = None):
    if пользователь == None:
        пользователь = interaction
    cur.execute("SELECT * FROM Users WHERE name = ?", (пользователь.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(пользователь.id)
    embed = discord.Embed(
        description=f"""<@{пользователь.id}> | `{пользователь}`\n\nНа счету: {all[1]} :coin:\nВремя до разбана: {all[3]}\nВремя до размута: {all[4]}\nКоличиство предупреждений: {all[5]}""",
        color=0x1)
    embed.set_thumbnail(url=пользователь.avatar)
    embed.set_author(name="Пользователь")
    await interaction.response.send_message(embed=embed, ephemeral=True)


def days_1(data1, data2):
    if data2 == "Monday":
        return data1 + " - " + "**Понедельник**"

    elif data2 == "Tuesday":
        return data1 + " - " + "**Вторник**"

    elif data2 == "Wednesday":
        return data1 + " - " + "**Среда**"

    elif data2 == "Thursday":
        return data1 + " - " + "**Четверг**"

    elif data2 == "Friday":
        return data1 + " - " + "**Пятница**"

    elif data2 == "Saturday":
        return data1 + " - " + "**Суббота**"

    elif data2 == "Sunday":
        return data1 + " - " + "**Воскресенье**"
    else:
        return data1 + " - " + data2


@tree.command(name="запланировать-ивент", description="расписание ивентов", guild=discord.Object(id=guild))
@app_commands.autocomplete(ивент=menu)
async def event3(interaction, ивент: str, дата: str, время: str):
    time_object = datetime.datetime.strptime(дата, '%d.%m')
    time_object = time_object.strftime("%d.%m")
    time_object1 = datetime.datetime.strptime(время, '%H:%M')
    time_object1 = time_object1.strftime("%H:%M")
    await event2([ивент, time_object, time_object1])

    await interaction.response.send_message(content = f"Ивент запланирован, дата и время проведения `{дата}` **:** `{время}`", ephemeral = True)


async def event2(text: list):
    r = 0
    channel = Bot.get_channel(1143990947949056061)
    async for i in channel.history():
        if i.id == int(1146181805167358063):
            r = i
    print(r.embeds[0].description)
    list1 = list()
    list2 = list()
    for i in range(0, 7):
        data = datetime.date.today() + datetime.timedelta(days=i)
        data2 = data.strftime("%A")
        data1 = data.strftime("`%d.%m`")
        data1 = days_1(data1, data2)
        if text[1] == data.strftime("%d.%m"):
            list2.append(text[0] + " - " + text[2])
        else:
            list2.append("Нет ивентов")

        list1.append(data1)
    embed = discord.Embed(
        description=f"**РАСПИСАНИЕ ИВЕНТОВ**\n\n{list1[0]}\n{list2[0]}\n\n{list1[1]}\n{list2[1]}\n\n{list1[2]}\n{list2[2]}\n\n{list1[3]}\n{list2[3]}\n\n{list1[4]}\n{list2[4]}\n\n{list1[5]}\n{list2[5]}\n\n{list1[6]}\n{list2[6]}\n")
    embed.set_image(url="https://media.discordapp.net/attachments/1143935103962198137/1146180780175937627/21dea55f066d9d29.png?width=1595&height=637")
    await r.edit(embed=embed)


@tree.command(name="ивент-пост", description="старт ивентов", guild=discord.Object(id=guild))
@app_commands.autocomplete(ивент=menu)
async def event1(interaction, ивент: str, ссылка: str):
    interaction1 = interaction
    guild1 = Bot.get_guild(guild)
    category = guild1.get_channel(1086041654005354689)
    voice = await guild1.create_voice_channel(name=str(ивент), reason="Начало ивента", user_limit=15, category=category)
    channel = Bot.get_channel(int(event_chat))
    embed = discord.Embed(description=f"""**Event {ивент}**\nНачат ивент `{ивент}`""", color=0x1)
    #embed1 = discord.Embed(description=f"""**Event {ивент}**\nОкончен ивент `{ивент}`""", color=0x1)
    embed2 = discord.Embed(
        description=f"""**Event {ивент}**\nГолосовой канал ивента создан  -  -  -  >  {voice.jump_url} """, color=0x1)
    embed3 = discord.Embed(
        description=f"""**Event {ивент}**\nИвент был завершён\n\nP.S Не забудьте выписать в канал <#1143981422097481778>\
         награды пользователей + скриншоты за каждую проведённую игру данного ивента (Скриншот конца каждой игры).""",
        color=0x1)

    async def callback2(interaction):
        if interaction.user.id == interaction1.user.id:
            await interaction.response.send_message(embed=embed3)
            #await channel.send(embed=embed1)
            print(interaction.message.content)
            await voice.delete()
        else:
            await interaction.response.send_message("123")

    view = View()
    view1 = View()
    button1 = Button(style=discord.ButtonStyle.primary, label='Голосовой канал', url=voice.jump_url)
    view.add_item(button1)
    #---------------------------------------------------------------------------------
    button2 = Button(style=discord.ButtonStyle.primary, label='Завершить ивент')
    view1.add_item(button2)
    button2.callback = callback2
    #---------------------------------------------------------------------------------
    button3 = Button(style=discord.ButtonStyle.primary, label='Сайт', url=str(ссылка))
    view.add_item(button3)

    await interaction.response.send_message(embed=embed2, view=view1)
    await channel.send(embed=embed, view=view)


# @tree.command(name="post", description="123", guild=discord.Object(id=guild))
# async def post(interaction):
#     await channel.send(interaction.message)

@tree.command(name="казино", description="Казино", guild=discord.Object(id=guild))
async def casino(interaction, ставка: int):
    r = random2.randint(0, 1)
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    if all == None:
        create_profil(interaction.user.id)
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    if ставка > 1000:
        embed = discord.Embed(
            description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\n Ваша ставка привышает лимит, максимальная ставка 1000 :coin:""",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        if int(all[0]) < ставка:
            embed = discord.Embed(
                description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\n У Вас не достаточно средств""",
                color=0x1)
            embed.set_thumbnail(url=interaction.user.avatar)
            embed.set_author(name="Пользователь")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if r == 1:
                new_valui = int(all[0]) + (ставка * 2 - ставка)
                cur.execute("UPDATE Users SET money = ? WHERE name = ?", (new_valui, interaction.user.id))
                con.commit()
                embed = discord.Embed(
                    description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\n Ваша ставка выйграла, Вы получили: {int(ставка * 2)} :coin:""",
                    color=0x1)
                embed.set_thumbnail(url=interaction.user.avatar)
                embed.set_author(name="Пользователь")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                new_valui = int(all[0]) - ставка
                cur.execute("UPDATE Users SET money = ? WHERE name = ?", (new_valui, interaction.user.id))
                con.commit()
                embed = discord.Embed(
                    description=f"""<@{interaction.user.id}> | `{interaction.user}`\n\n Ваша ставка проиграла, Вы потеряли: {ставка} :coin:""",
                    color=0x1)
                embed.set_thumbnail(url=interaction.user.avatar)
                embed.set_author(name="Пользователь")
                await interaction.response.send_message(embed=embed, ephemeral=True)


#
# @Bot.event
# async def on_button_click(interaction: discord.Interaction):
#     print(interaction.component.custom_id)

# @tree.command(name="брак", description="брак", guild=discord.Object(id=guild))
# async def marry(interaction, пользователь: discord.Member):
#     print(пользователь.id)
#     if interaction.user.id == пользователь.id:
#         await interaction.response.send_message('Нельзя выйти за себя 🙅‍♂️', ephemeral=True)
#     else:
#         cur.execute("SELECT marry FROM Users WHERE name = ?", (пользователь.id,))
#         all = cur.fetchone()
#         cur.execute("SELECT marry FROM Users WHERE name = ?", (interaction.user.id,))
#         all1 = cur.fetchone()
#         print(1)
#         if all[0] == None:
#             create_profil(пользователь.id)
#         if all1[0] == None:
#             create_profil(interaction.user.id)
#         cur.execute("SELECT marry FROM Users WHERE name = ?", (пользователь.id,))
#         cur.execute("SELECT marry FROM Users WHERE name = ?", (interaction.user.id,))
#         all = cur.fetchall()
#         if all[0][0] != 0:
#             if all[1][0] != 0:
#                 await interaction.response.send_message('Пользователь уже замужем/женат', ephemeral=True)
#             else:
#                 await interaction.response.send_message('Вы уже замужем/женат', ephemeral=True)
#         else:
#             channel = Bot.get_channel(int(interaction.channel.id))
#             view = View()
#             button = Button(style=discord.ButtonStyle.primary, label='Подтвердить')
#
#             async def button_callback(interaction: discord.Interaction):
#
#                 await interaction.response.send_message('Предложение было отпрвлено', ephemeral=True)
#
#                 await repit111(пользователь, interaction, channel)
#
#             button.callback = button_callback
#             view.add_item(button)
#             text = f"Предложение брака.\nВы предложили вступить в брак пользователю {пользователь.name} | <@{пользователь.id}>\nПодтвердите снизу"
#             await interaction.response.send_message(text, view=view, ephemeral=True)
#
#
# async def repit111(interaction1: discord.Interaction, user1, channel):
#     user = await Bot.fetch_user(interaction1.id)
#
#     view = View()
#     button1 = Button(style=discord.ButtonStyle.primary, label='Да', custom_id='button1')
#     button2 = Button(style=discord.ButtonStyle.success, label='Нет', custom_id='button2')
#
#     async def callback1(interaction):
#         print(user1.id, " ", interaction.user.id)
#         cur.execute("UPDATE Users SET marry = ? WHERE name = ?", (user1.id, interaction.user.id))
#         cur.execute("UPDATE Users SET marry = ? WHERE name = ?", (interaction.user.id, user1.id))
#         con.commit()
#         await message.reply(f'Вы согласились сделать пару с <@{user1.user.id}>')
#
#         await channel.send(f"<@{interaction1.id}>|{interaction1.name} || <@{user1.user.id}>|{user1.user.name}")
#
#     async def callback2(interaction):
#         await message.reply(f'Вы отказались сделать пару с <@{user1.user.id}>')
#
#     button1.callback = callback1
#     button2.callback = callback2
#     view.add_item(button1)
#     view.add_item(button2)
#
#     embed = discord.Embed(
#         description=f"\nПользователь <@{user1.user.id}> сделал вам предложение руки и сердца.\n\nГотовы ли вы вступить с ним в брак? ❤️‍🔥",
#         color=0x36393E)
#     embed.set_author(name="Предложение брака.")
#     embed.set_image(url="https://cdn.discordapp.com/attachments/1075518862889590895/1125738955250352188/1004.gif")
#     message = await user.send(embed=embed, view=view)


@tree.command(name="магазин", description="магазин", guild=discord.Object(id=guild))
async def shop1(interaction, лот: int = -1):
    view = View()
    button = Button(style=discord.ButtonStyle.primary, label='Подтвердить')

    async def button_callback(interaction: discord.Interaction, price):
        cur.execute("SELECT money FROM Users WHERE name = ?", (interaction,))
        all = cur.fetchone()
        if price[3] > all:
            await interaction.response.send_message('Не достаточно средств', ephemeral=True)
        else:
            await interaction.response.send_message('Вы купили товар', ephemeral=True)

    if лот == -1:
        cur.execute("SELECT * FROM Shop")
        all = cur.fetchall()
        r = []
        r1 = ""
        for i in all:
            r.append("лот: " + str(i[0]) + " Название: " + str(i[1]) + " Цена: " + str(i[3]) + " :coin:" + "\n")
        for i in range(len(r)):
            r1 += r[i]
        embed = discord.Embed(
            description=r1,
            color=0x36393E)
        # print([i[0] for i in all])
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        cur.execute("SELECT * FROM Shop WHERE id = ?", (лот,))
        all = cur.fetchone()
        button.callback = button_callback(interaction, all)
        view.add_item(button)
        embed = discord.Embed(
            description=f"Название: {all[1]}\nОписание: {all[2]}\nЦена: {all[3]} :coin:",
            color=0x36393E)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@tree.command(name="createl", description="123", guild=discord.Object(id=guild))
async def create_lot(interaction, name: discord.Role, description: str, price: float):
    data = [None, name, description, price]

    cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", data)
    con.commit()
    await interaction.response.send_message(f"{name} \n {description} \n {price}", ephemeral=True)


@tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    embed = discord.Embed(description=f"""Со мной что-то случилось\n{error}""", color=0x1)
    print(error)
    await interaction.response.send_message(embed=embed, ephemeral=True)


# 1. Во время запуска бота
@Bot.event
async def on_ready():
    await Bot.change_presence(status=discord.Status.online)
    await tree.sync(guild=discord.Object(id=guild))
    # check123(281772955690860544)
    # a = True
    # while a:
    #     r = str(input())
    #     if r == "stop":
    #         exit()
    #     elif r == "123":
    #

    # while True:
    #     cur.execute("SELECT name, ban_timeout, mute_timeout FROM Users")
    #     all = cur.fetchone()
    #     time.sleep(300)
    # await channel.send(f"{time} Start")
    # channel = Bot.get_channel(1067138540544200724)
    # a = False
    # r = requests.get(f"https://logs1.shadowcraft.ru/Magic_public_logs/{getTime2()}.txt")
    # lastlog = r.text
    # while a == True:
    #     if times != getTime2():
    #         a = False
    #     else:
    #         if r.text != lastlog:
    #             rr = r.text
    #             text = r.text.replace(lastlog, "")
    #             lastlog = rr
    #             await channel.send(text)
    #             sleep(10)
    #         else:
    #             r = requests.get(f"https://logs1.shadowcraft.ru/Magic_public_logs/{getTime2()}.txt")
    #             sleep(10)


# Запуск бота
Bot.run(token)
