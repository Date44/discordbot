import configparser
import datetime
import os
import sqlite3
import time
import tracemalloc

import discord
import random2
from discord import app_commands
from discord.ext import tasks
from discord.ui import View, Button


async def menu(interaction: discord.Interaction, current: str, ) -> list[app_commands.Choice[str]]:
    menu = ["Мафия", "Бункер", "Алиас/Шляпа", "Крокодил", "GarticPhone", "JackBox", "Codenames", "Намёк понял", "Шпион",
            "Кто я?", "Криминалист"]
    return [
        app_commands.Choice(name=string, value=string)
        for string in menu if current.lower() in string.lower()
    ]


def create_db():
    cur.execute("CREATE TABLE Users(name UNIQUE, money, timeout, ban_timeout, mute_timeout, warn)")
    cur.execute("CREATE TABLE Shop(id INTEGER UNIQUE PRIMARY KEY, name, description, price)")


def create_profil(id_name):
    data = [(id_name, 0, 0, 0, 0, 0), ]
    cur.executemany("INSERT INTO Users VALUES(?, ?, ?, ?, ?, ?)", data)
    con.commit()
    cur.execute("SELECT * FROM Users WHERE name = ?", (id_name,))
    return cur.fetchone()


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


if __name__ == '__main__':
    intents = discord.Intents.default()
    intents.typing = False
    intents.presences = False
    intents.message_content = True
    intents.guilds = True
    intents.members = True
    Bot = discord.Client(intents=intents)
    tree = app_commands.CommandTree(Bot)
    tracemalloc.start()

    if not os.path.exists('Miki.db'):
        con = sqlite3.connect("Miki.db")
        cur = con.cursor()
        create_db()
        g = True

    else:
        con = sqlite3.connect("Miki.db")
        cur = con.cursor()

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


def get_future_time2(delta_str):
    delta_unit = delta_str[-1].lower()
    delta_value = int(delta_str[:-1])

    if delta_unit == 'd':
        delta = datetime.timedelta(days=delta_value)
    elif delta_unit == 'm':
        delta = datetime.timedelta(minutes=delta_value)
    elif delta_unit == 'h':
        delta = datetime.timedelta(hours=delta_value)
    elif delta_unit == 's':
        delta = datetime.timedelta(seconds=delta_value)
    elif delta_unit == 'w':
        delta = datetime.timedelta(weeks=delta_value)
    else:
        delta = datetime.timedelta()  # Default to 0

    future_time = datetime.datetime.now() + delta
    return future_time


def get_future_time(delta_str):
    delta_unit = delta_str[-1].lower()
    delta_value = int(delta_str[:-1])

    if delta_unit == 'd':
        delta = datetime.timedelta(days=delta_value)
    elif delta_unit == 'm':
        delta = datetime.timedelta(minutes=delta_value)
    elif delta_unit == 'h':
        delta = datetime.timedelta(hours=delta_value)
    elif delta_unit == 's':
        delta = datetime.timedelta(seconds=delta_value)
    elif delta_unit == 'w':
        delta = datetime.timedelta(weeks=delta_value)
    else:
        delta = datetime.timedelta()  # Default to 0

    future_time = datetime.datetime.now() + delta
    return future_time.strftime('%H:%M:%S %d-%m-%Y')


def get_current_date():
    current_time = datetime.datetime.now()
    return current_time.strftime("%d-%m-%Y")


async def delete_messages(text, channel):
    num = int(text.split()[1]) + 1
    async for msg in channel.history(limit=num):
        await msg.delete()


async def process_text_command(message):
    text = message.content
    text = text.split("\n")
    line = text[0].split(' ')
    del text[0]
    color = line[1] in colors
    if line[2]:
        channel = Bot.get_channel(int(line[2].replace('<#', '').replace('>', '')))
    else:
        channel = message.channel
    content = '\n'.join(text)
    if not color:
        color = 0x000000
    else:
        color = colors[line[1]]
    embed = discord.Embed(description=content, color=color)
    if message.attachments:
        for attach in message.attachments:
            embed.set_image(url=attach.url)
    await channel.send(embed=embed)


async def edit_embed(message):
    text = message.content
    text = text.split("\n")
    line = text[0].split(' ')
    line = line[1].replace("https://discord.com/channels/1007951389198127195/", "").replace(' ', '').split('/')
    del text[0]
    channel = Bot.get_channel(int(line[0].replace('<#', '').replace('>', '')))
    content = '\n'.join(text)
    async for i in channel.history():
        if i.id == int(line[1]):
            for embed in i.embeds:
                embed.description = content
                if message.attachments:
                    for attach in message.attachments:
                        embed.set_image(url=attach.url)
                await i.edit(embed=embed)


async def create_rules(text):
    channel = Bot.get_channel(int(1008286403068702832))
    text = text.split("\n")
    del text[0]

    embed = discord.Embed(color=0x000000)
    embed.title = f"**{text[0]}**"
    embed.set_footer(text=f"{text[7]}")
    embed.add_field(name=f"**> {text[1]} **", value=f"```{text[2]}```", inline=False)
    embed.add_field(name=f"**> {text[3]} **", value=f"```{text[4]}```", inline=True)
    embed.add_field(name=f"**> {text[5]} **", value=f"```{text[6]}```", inline=True)

    await channel.send(embed=embed)


async def edit_rules(text):
    text = text.split("\n")
    line = text[0].replace("https://discord.com/channels/1007951389198127195/", "").replace(' ', '').split('/')[1]
    del text[0]
    channel = Bot.get_channel(int(1008286403068702832))

    embed = discord.Embed(color=0x000000)
    embed.title = f"**{text[0]}**"
    embed.set_footer(text=f"{text[7]}")
    embed.add_field(name=f"**> {text[1]} **", value=f"```{text[2]}```", inline=False)
    embed.add_field(name=f"**> {text[3]} **", value=f"```{text[4]}```", inline=True)
    embed.add_field(name=f"**> {text[5]} **", value=f"```{text[6]}```", inline=True)
    async for i in channel.history():
        if i.id == int(line):
            await i.edit(embed=embed)


@Bot.event
async def on_message(message):
    black_listbot = [str(Bot.user.id), ]
    channel = message.channel
    text = message.content
    if str(message.author.id) not in black_listbot:
        if text.startswith("!del"):
            await delete_messages(text, channel)
        elif text.startswith("!restart"):
            await message.delete()
            await Bot.close()
            exit()
        elif text.startswith("!text"):
            await process_text_command(message)
        elif text.startswith("!edit"):
            await edit_embed(message)
        elif text.startswith("!правила-создание"):
            await create_rules(text)
        elif text.startswith("!правила-изменение"):
            await edit_rules(text)


class my_modal(discord.ui.Modal, title='Modal'):
    m1 = discord.ui.TextInput(label='Ваш возраст', placeholder="23 года")
    m2 = discord.ui.TextInput(label='Никнейм в игре', placeholder="flowle_")
    m3 = discord.ui.TextInput(label='Чем планируете заняться на сервере?', placeholder="Cтроительством, фермерством")
    m4 = discord.ui.TextInput(label='Расскажите немного о себе', style=discord.TextStyle.long,
                              placeholder="Я Максим, люблю пиццу", min_length=16, max_length=128)

    async def on_submit(self, interaction: discord.Interaction):
        channel = Bot.get_channel(int(1075471916204306535))
        embed = discord.Embed(title=self.title,
                              description=f"**{self.m1.label}**\n{self.m1}\n**{self.m2.label}**\n{self.m2}\n**{self.m3.label}**\n{self.m3}\n**{self.m4.label}**\n{self.m4}",
                              color=discord.Colour.blue())
        embed.set_author(name=interaction.user, icon_url=interaction.user.avatar)
        await channel.send(embed=embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="modal", description="Modal", guild=discord.Object(id=guild))
async def modal(interaction):
    await interaction.response.send_modal(my_modal())


@tree.command(name="info", description="Command info/Информация о командах", guild=discord.Object(id=guild))
async def info(interaction):
    info = ("\n"
            "    **Список доступных цветов:**\n"
            "    DarkRed, Red, DarkOrange, Yellow, Gold, DarkBlue, Blue, Cyan, Lime, LimeGreen, OrangeRed\n"
            "\n"
            "    **Список доступных команд:**\n"
            "    **!del** [количиство] - удаляет сообщения\n"
            "    **!text** [цвет] [#канал] - создать пост \n`Заголовок`\n `Текст`\n"
            "    **!edit** [ссылка на сообщение] - изменить пост \n`Заголовок` \n`Текст`\n"
            "    **!restart** - перезапустить бота\n"
            "**!правила-создание** \n `Заголовок` \n`Текст1` \n`Текст1` \n`Текст2` \n`Текст2` \n`Текст3` \n`Текст3` "
            "\n`Футер` \n"
            "**!правила-изменение** [ссылка на сообщение] \n `Заголовок` \n`Текст1` \n`Текст1` \n`Текст2` \n`Текст2` "
            "\n`Текст3` \n`Текст3` \n`Футер` \n")
    embed = discord.Embed(title="Инфо", description=info, color=0x1)
    await interaction.response.send_message(embed=embed)


@tree.command(name="бан", description="забанить пользователя", guild=discord.Object(id=guild))
async def ban(interaction, пользователь: discord.Member, время: str, причина: str):
    channel = Bot.get_channel(log_chat)
    guild1 = Bot.get_guild(guild)
    role_ban = guild1.get_role(1208767887016333363)
    text = f'**Пользователь** <@{пользователь.id}> | `{пользователь}` **был забанен на сервере, время: <t:{get_future_time2(время)}>, причина: {причина}**'
    await пользователь.add_roles(role_ban, reason=причина)
    await channel.send(text)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (пользователь.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(пользователь.id)
    cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (get_future_time(время), пользователь.id))
    con.commit()
    await interaction.response.send_message(text, ephemeral=True)


@tree.command(name="разбан", description="Снять бан", guild=discord.Object(id=guild))
async def unban(interaction, пользователь: discord.Member, причина: str):
    channel = Bot.get_channel(log_chat)
    guild1 = Bot.get_guild(guild)
    role_ban = guild1.get_role(1208767887016333363)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (пользователь.id,))
    all = cur.fetchone()
    if all == None:
        all = create_profil(interaction.user.id)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    await пользователь.remove_roles(role_ban, reason=причина)
    cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (0, interaction.user.id))
    con.commit()
    text = f"**Модератор** <@{interaction.user.id}> | `{interaction.user}` **снял бан с пользователя:** <@{пользователь.id}> | `{пользователь}`  **Причина: {причина}**"
    await channel.send(text)


@tree.command(name="мут", description="mute user", guild=discord.Object(id=guild))
async def mute(interaction, пользователь: discord.Member, время: str, причина: str):
    channel = Bot.get_channel(log_chat)
    guild1 = Bot.get_guild(guild)
    role_mute = guild1.get_role(1211342600204722248)
    text = f'**Пользователь** <@{пользователь.id}> | `{пользователь}` **был замьючен на сервере, время: {время}, причина: {причина}**'
    await пользователь.add_roles(role_mute, reason=причина)
    await channel.send(text)
    cur.execute("SELECT mute_timeout FROM Users WHERE name = ?", (пользователь.id,))
    all = cur.fetchone()
    if all is None:
        all = create_profil(пользователь.id)
    cur.execute("UPDATE Users SET mute_timeout = ? WHERE name = ?", (get_future_time(время), пользователь.id))
    con.commit()
    await interaction.response.send_message(text, ephemeral=True)


@tree.command(name="счёт", description="Проверить счёт", guild=discord.Object(id=guild))
async def money(interaction):
    channel = Bot.get_channel(int(interaction.channel.id))
    guild1 = Bot.get_guild(guild)
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
    if all[1] != get_current_date() or all[0] == 0:
        new_valui = int(all[0]) + 100
        cur.execute("UPDATE Users SET money = ?, timeout = ? WHERE name = ?",
                    (new_valui, get_current_date(), interaction.user.id))
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


@tree.command(name="инфо", description="просмотр профиля", guild=discord.Object(id=guild))
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


#
# def days_1(data1, data2):
#     if data2 == "Monday":
#         return data1 + " - " + "**Понедельник**"
#
#     elif data2 == "Tuesday":
#         return data1 + " - " + "**Вторник**"
#
#     elif data2 == "Wednesday":
#         return data1 + " - " + "**Среда**"
#
#     elif data2 == "Thursday":
#         return data1 + " - " + "**Четверг**"
#
#     elif data2 == "Friday":
#         return data1 + " - " + "**Пятница**"
#
#     elif data2 == "Saturday":
#         return data1 + " - " + "**Суббота**"
#
#     elif data2 == "Sunday":
#         return data1 + " - " + "**Воскресенье**"
#     else:
#         return data1 + " - " + data2

#
# @tree.command(name="запланировать-ивент", description="расписание ивентов", guild=discord.Object(id=guild))
# @app_commands.autocomplete(ивент=menu)
# async def event3(interaction, ивент: str, дата: str, время: str):
#     # time_object = datetime.datetime.strptime(дата, '%d.%m')
#     # time_object = time_object.strftime("%d.%m")
#     # time_object1 = datetime.datetime.strptime(время, '%H:%M')
#     # time_object1 = time_object1.strftime("%H:%M")
#     # await event2([ивент, time_object, time_object1])
#
#     await interaction.response.send_message(
#         content=f"Ивент запланирован, дата и время проведения `{дата}` **:** `{время}`", ephemeral=True)

#
# async def event2(text: list):
#     r = 0
#     channel = Bot.get_channel(1143990947949056061)
#     async for i in channel.history():
#         if i.id == int(1146181805167358063):
#             r = i
#     print(r.embeds[0].description)
#     list1 = list()
#     list2 = list()
#     for i in range(0, 7):
#         data = datetime.date.today() + datetime.timedelta(days=i)
#         data2 = data.strftime("%A")
#         data1 = data.strftime("`%d.%m`")
#         data1 = days_1(data1, data2)
#         if text[1] == data.strftime("%d.%m"):
#             list2.append(text[0] + " - " + text[2])
#         else:
#             list2.append("Нет ивентов")
#
#         list1.append(data1)
#     embed = discord.Embed(
#         description=f"**РАСПИСАНИЕ ИВЕНТОВ**\n\n{list1[0]}\n{list2[0]}\n\n{list1[1]}\n{list2[1]}\n\n{list1[2]}\n{list2[2]}\n\n{list1[3]}\n{list2[3]}\n\n{list1[4]}\n{list2[4]}\n\n{list1[5]}\n{list2[5]}\n\n{list1[6]}\n{list2[6]}\n")
#     embed.set_image(
#         url="https://media.discordapp.net/attachments/1143935103962198137/1146180780175937627/21dea55f066d9d29.png?width=1595&height=637")
#     await r.edit(embed=embed)
#

@tree.command(name="ивент-пост", description="старт ивентов", guild=discord.Object(id=guild))
@app_commands.autocomplete(ивент=menu)
async def event1(interaction, ивент: str, ссылка: str):
    interaction1 = interaction
    guild1 = Bot.get_guild(guild)
    category = guild1.get_channel(1086041654005354689)
    voice = await guild1.create_voice_channel(name=str(ивент), reason="Начало ивента", user_limit=15, category=category)
    channel = Bot.get_channel(int(event_chat))
    embed = discord.Embed(description=f"""**Event {ивент}**\nНачат ивент `{ивент}`""", color=0x1)
    embed1 = discord.Embed(description=f"""**Event {ивент}**\nОкончен ивент `{ивент}`""", color=0x1)
    embed2 = discord.Embed(
        description=f"""**Event {ивент}**\nГолосовой канал ивента создан  -  -  -  >  {voice.jump_url} """, color=0x1)
    embed3 = discord.Embed(
        description=f"""**Event {ивент}**\nИвент был завершён\n\nP.S Не забудьте выписать в канал <#1143981422097481778>\
         награды пользователей + скриншоты за каждую проведённую игру данного ивента (Скриншот конца каждой игры).""",
        color=0x1)

    async def callback2(interaction):
        if interaction.user.id == interaction1.user.id:
            await interaction.response.send_message(embed=embed3)
            await channel.send(embed=embed1)
            print(interaction.message.content)
            await voice.delete()
        else:
            await interaction.response.send_message("123")

    view = View()
    view1 = View()
    button1 = Button(style=discord.ButtonStyle.primary, label='Голосовой канал', url=voice.jump_url)
    view.add_item(button1)
    # -----------------------------ч----------------------------------------------------
    button2 = Button(style=discord.ButtonStyle.primary, label='Завершить ивент')
    view1.add_item(button2)
    button2.callback = callback2
    # ---------------------------------------------------------------------------------
    button3 = Button(style=discord.ButtonStyle.primary, label='Сайт', url=str(ссылка))
    view.add_item(button3)

    await interaction.response.send_message(embed=embed2, view=view1)
    await channel.send(embed=embed, view=view)


@tree.command(name="казино", description="Казино", guild=discord.Object(id=guild))
async def casino(interaction, ставка: int):
    r = random2.randint(0, 1)
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    all = cur.fetchone()
    if all is None:
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
    embed1 = discord.Embed(description=f"""Со мной что-то случилось\nобратитесь к администрации""", color=0x1)
    channel = Bot.get_channel(int(bot_chat))
    await interaction.response.send_message(embed=embed1, ephemeral=True)
    await channel.send(embed=embed)


async def remove_role(guild, member_id, role):
    member = await guild.fetch_member(member_id)
    if member:
        await member.remove_roles(role, reason="(auto)")
    else:
        print(f"Member not found for {role.name}.")


@tasks.loop(minutes=1)
async def remove_expired_roles():
    guild = Bot.get_guild(1007951389198127195)
    role_ban = guild.get_role(1208767887016333363)
    role_mute = guild.get_role(1211342600204722248)
    current_time = datetime.datetime.now()

    cur.execute("SELECT * FROM Users WHERE ban_timeout != 0 OR mute_timeout != 0")
    all_entries = cur.fetchall()

    for entry in all_entries:
        member_id = int(entry[0])
        ban_timeout = datetime.datetime.strptime(str(entry[3]), '%H:%M:%S %d-%m-%Y') if entry[3] != 0 else None
        mute_timeout = datetime.datetime.strptime(str(entry[4]), '%H:%M:%S %d-%m-%Y') if entry[4] != 0 else None

        if ban_timeout and current_time >= ban_timeout:
            await remove_role(guild, member_id, role_ban)
            cur.execute("UPDATE Users SET ban_timeout = 0 WHERE name = ?", (member_id,))
            con.commit()

        if mute_timeout and current_time >= mute_timeout:
            await remove_role(guild, member_id, role_mute)
            cur.execute("UPDATE Users SET mute_timeout = 0 WHERE name = ?", (member_id,))
            con.commit()


@Bot.event
async def on_ready():
    await Bot.change_presence(status=discord.Status.online)
    await tree.sync(guild=discord.Object(id=guild))
    remove_expired_roles.start()


@Bot.event
async def on_member_join(member):
    embed = discord.Embed(description=f"{member} присоединился к серверу")
    channel = Bot.get_channel(int(log_chat))

    cur.execute("SELECT name FROM Users WHERE name = ?", (member.id,))
    entrie = cur.fetchone()
    if entrie is None:
        embed = discord.Embed(description=f"{member} впервые присоединился к серверу")
        create_profil(member.id)
    await channel.send(embed=embed)


@Bot.event
async def on_member_remove(member):
    embed = discord.Embed(description=f"{member} покинул сервер")
    channel = Bot.get_channel(int(log_chat))
    await channel.send(embed=embed)


Bot.run(token)
