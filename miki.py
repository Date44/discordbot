import configparser
import datetime
import json
import os
import sqlite3
import time

import tracemalloc

import discord
import random2
from discord import app_commands
from discord.ext import tasks
from discord.ui import View, Button


def get_future_time(delta_str):
    delta_unit = str(delta_str)[-1].lower()
    delta_value = int(str(delta_str)[:-1])

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
        delta = datetime.timedelta()

    future_time = datetime.datetime.now() + delta
    return int(future_time.timestamp())


def get_current_date():
    current_time = datetime.datetime.now()
    return current_time.strftime("%d-%m-%Y")


def create_db():
    cur.execute("CREATE TABLE Users(name UNIQUE, money, timeout, ban_timeout, mute_timeout, warn)")
    cur.execute("CREATE TABLE Shop(id INTEGER UNIQUE PRIMARY KEY, name, description, price)")
    cur.execute("CREATE TABLE History(id INTEGER UNIQUE PRIMARY KEY, name, type, data, rule, moderator)")


def create_profile(id_name):
    data = [(id_name, 0, 0, 0, 0, 0), ]
    cur.executemany("INSERT INTO Users VALUES(?, ?, ?, ?, ?, ?)", data)
    con.commit()
    cur.execute("SELECT * FROM Users WHERE name = ?", (id_name,))
    return cur.fetchone()


def add_history(name, type, data, rule, moderator):
    data = [(None, name, type, data, rule, moderator), ]
    cur.executemany("INSERT INTO History VALUES(?, ?, ?, ?, ?, ?)", data)
    con.commit()


# config
def create_config():
    id_chat = "0000000000000000000"
    config = configparser.ConfigParser()

    config.add_section('Login')
    config.add_section('Protect')
    config.add_section('Log')
    config.add_section('Event')
    config.add_section('Roles')

    config.set('Login', 'token', '')
    config.set('Login', 'command_chat', id_chat)
    config.set('Login', 'guild_id', id_chat)
    config.set('Protect', 'white_list', "[281772955690860544, ]")
    config.set('Log', 'log_chat', id_chat)
    config.set('Event', 'event_chat', id_chat)
    config.set('Event', 'event_categorize', id_chat)
    config.set('Roles', 'role_ban', id_chat)
    config.set('Roles', 'role_mute', id_chat)

    with open('config.cfg', 'w') as configfile:
        config.write(configfile)


async def menu(interaction: discord.Interaction, current: str, ) -> list[app_commands.Choice[str]]:
    menu = ["Мафия", "Бункер", "Алиас/Шляпа", "Крокодил", "GarlicPhone", "JackBox", "Codenames", "Намёк понял", "Шпион",
            "Кто я?", "Криминалист"]
    return [
        app_commands.Choice(name=string, value=string)
        for string in menu if current.lower() in string.lower()
    ]


def read_config():
    config = configparser.ConfigParser()
    config.read('config.cfg')
    config = {
        "token": config.get('Login', 'token'),
        "command_chat": config.get('Login', 'command_chat'),
        "guild_id": config.get('Login', 'guild_id'),
        "white_list": config.get('Protect', 'white_list'),
        "log_chat": config.get('Log', 'log_chat'),
        "event_chat": config.get('Event', 'event_chat'),
        "event_categorize": config.get('Event', 'event_categorize'),
        "role_ban": config.get('Roles', 'role_ban'),
        "role_mute": config.get('Roles', 'role_mute'),
    }
    return config


intents = discord.Intents.default()
intents.typing = False
intents.presences = True
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

else:
    con = sqlite3.connect("Miki.db")
    cur = con.cursor()

if not os.path.exists("data_file.json"):
    with open("data_file.json", "w", encoding="utf-8") as write_file:
        json.dump({}, write_file, indent=4)


if not os.path.exists('config.cfg'):
    create_config()
    time.sleep(5)
    cfg = read_config()
else:
    cfg = read_config()

token = cfg["token"]
bot_chat_id = int(cfg["command_chat"])
white_list = cfg["white_list"]
log_chat_id = int(cfg["log_chat"])
guild_id = int(cfg["guild_id"])
event_chat = int(cfg["event_chat"])
event_categorize = int(cfg["event_categorize"])
role_ban_id = int(cfg["role_ban"])
role_mute_id = int(cfg["role_mute"])
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
    line = (line[1].replace(f"https://discord.com/channels/{guild_id}/", "")
            .replace(' ', '')
            .split('/'))
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


async def create_rules(message):
    text = message.content
    text = text.split("\n")
    line = (text[0]
            .replace("!правила-создание", "")
            .replace("<#", "")
            .replace(">", "")
            .replace(" ", "")
            )
    if line == "":
        channel = message.channel
    else:
        channel = Bot.get_channel(int(line))

    del text[0]

    embed = discord.Embed(color=0x000000)
    embed.title = f"**{text[0]}**"
    embed.set_footer(text=f"{text[7]}")
    embed.add_field(name=f"**> {text[1]} **", value=f"```{text[2]}```", inline=False)
    embed.add_field(name=f"**> {text[3]} **", value=f"```{text[4]}```", inline=True)
    embed.add_field(name=f"**> {text[5]} **", value=f"```{text[6]}```", inline=True)

    await channel.send(embed=embed)


class EditModal(discord.ui.Modal):
    def __init__(self, message: discord.Message):
        super().__init__(title="Edit")
        self.message = message
        for field in message.embeds[0].fields:
            self.add_item(
                discord.ui.TextInput(label=field.name, default=field.value, style=discord.TextStyle.paragraph))

    async def on_submit(self, interaction: discord.Interaction):
        embed = discord.Embed(color=0x000000)
        embed.title = self.message.embeds[0].title
        embed.add_field(name=self.children[0].label, value=self.children[0].value, inline=False)
        embed.add_field(name=self.children[1].label, value=self.children[1].value, inline=True)
        embed.add_field(name=self.children[2].label, value=self.children[2].value, inline=True)
        await self.message.edit(embed=embed)


@tree.context_menu(name="edit", guild=discord.Object(id=guild_id))
async def edit_rules(interaction: discord.Interaction, message: discord.Message):
    if message.author == Bot.user:
        await interaction.response.send_modal(EditModal(message))
    else:
        await interaction.response.send_message(f"Данная функция работает только на сообщения от <@!{Bot.user.id}>",
                                                suppress_embeds=True, ephemeral=True)


async def test(message):
    await message.channel.send(message.content)


async def restart(message):
    await message.delete()
    await Bot.close()
    exit()


@Bot.event
async def on_message(message: discord.Message):
    black_listbot = [str(Bot.user.id), ]
    channel = message.channel
    text = message.content
    if str(message.author.id) not in black_listbot:
        if text.startswith("!del"):
            await delete_messages(text, channel)
        elif text.startswith("!restart"):
            await restart(message)
        elif text.startswith("!text"):
            await process_text_command(message)
        elif text.startswith("!edit"):
            await edit_embed(message)
        elif text.startswith("!правила-создание"):
            await create_rules(message)
        # elif text.startswith("!правила-изменение"):
        #     await edit_rules(message)
        elif text.startswith("!123"):
            await test(message)


@tree.command(name="info", description="Command info/Информация о командах", guild=discord.Object(id=guild_id))
async def info(interaction: discord.Interaction):
    Infomercial = ("\n"
                   "    **Список доступных цветов:**\n"
                   "    DarkRed, Red, DarkOrange, Yellow, Gold, DarkBlue, Blue, Cyan, Lime, LimeGreen, OrangeRed\n"
                   "\n"
                   "    **Список доступных команд:**\n"
                   "    **!del** [количиство] - удаляет сообщения\n"
                   "    **!text** [цвет] [#канал] - создать пост \n`Заголовок`\n `Текст`\n"
                   "    **!edit** [ссылка на сообщение] - изменить пост \n`Заголовок` \n`Текст`\n"
                   "    **!restart** - перезапустить бота\n"
                   "**!правила-создание** [#канал] \n `Заголовок` \n`Текст1` "
                   "\n`Текст1` \n`Текст2` \n`Текст2` \n`Текст3`"
                   "\n`Текст3`"
                   "\n"
                   "**!правила-изменение** [ссылка на сообщение] \n `Заголовок` "
                   "\n`Текст1` \n`Текст1` \n`Текст2` \n`Текст2` "
                   "\n`Текст3` \n`Текст3` \n")

    embed = discord.Embed(title="Инфо", description=Infomercial, color=0x1)
    await interaction.response.send_message(embed=embed)


async def ban(interaction: discord.Interaction, user: discord.Member, время: str, причина: str,
              комментарий: str):
    embed = discord.Embed(
        description=f"**Пользователь** <@{user.id}> | `{user}` **был забанен на сервере.**"
                    f"\n**Модератор:** <@{interaction.user.id}> | `{interaction.user}`."
                    f"\n**Время окончания:**  <t:{get_future_time(время)}>"
                    f"\n**Причина:{причина}**"
                    f"\n**Комментарий:{комментарий}**",
        color=0x000000)
    await user.add_roles(role_ban, reason=str(причина))
    await log_chat.send(embed=embed)
    add_history(user.id, 1, int(time.time()), причина, interaction.user.id)
    cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (get_future_time(время), user.id))
    con.commit()
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def unban(interaction: discord.Interaction, user: discord.Member, причина: str, коментарий: str):
    text = "Пользователь не забанен"
    embed = discord.Embed(
        description=f"**Модератор** <@{interaction.user.id}> | `{interaction.user}`\n **Снял бан с "
                    f"пользователя:** <@{user.id}> | `{user}`\n**Причина:"
                    f" {причина}**\n**Коментарий: {коментарий}**",
        color=0x000000)
    cur.execute("SELECT ban_timeout FROM Users WHERE name = ?", (user.id,))
    if cur.fetchone()[0] == 0:
        await interaction.response.send_message(text, ephemeral=True)
    else:
        await user.remove_roles(role_ban, reason=str(причина))
        cur.execute("UPDATE Users SET ban_timeout = ? WHERE name = ?", (0, user.id))
        con.commit()
        add_history(user.id, 3, int(time.time()), причина, interaction.user.id)
        await log_chat.send(embed=embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)


async def mute(interaction: discord.Interaction, user: discord.Member, время: str, причина: str,
               коментарий: str):
    embed = discord.Embed(
        description=f"**Пользователь** <@{user.id}> | `{user}` **был замьючен на сервере "
                    f"модератором** <@{interaction.user.id}> | `{interaction.user}`."
                    f"\n**время окончания: <t:{get_future_time(время)}>.**\n **Причина:"
                    f" {причина}.**\n**Коментарий: {коментарий}**",
        color=0x000000)
    await user.add_roles(role_mute, reason=str(причина))
    await log_chat.send(embed=embed)
    add_history(user.id, 2, int(time.time()), причина, interaction.user.id)
    cur.execute("UPDATE Users SET mute_timeout = ? WHERE name = ?", (get_future_time(время), user.id))
    con.commit()
    await interaction.response.send_message(embed=embed, ephemeral=True)


async def unmute(interaction: discord.Interaction, user: discord.Member, причина: str, коментарий: str):
    text = "Пользователь не замьючен"
    embed = discord.Embed(
        description=f"**Модератор** <@{interaction.user.id}> | `{interaction.user}`\n **Снял мьют с "
                    f"пользователя:** <@{user.id}> | `{user}`\n**Причина:"
                    f" {причина}**\n**Коментарий: {коментарий}**",
        color=0x000000)
    cur.execute("SELECT mute_timeout FROM Users WHERE name = ?", (user.id,))
    if cur.fetchone()[0] == 0:
        await interaction.response.send_message(text, ephemeral=True)
    else:
        await user.remove_roles(role_mute, reason=str(причина))
        cur.execute("UPDATE Users SET mute_timeout = ? WHERE name = ?", (0, user.id))
        con.commit()
        add_history(user.id, 3, int(time.time()), причина, interaction.user.id)
        await log_chat.send(embed=embed)
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="счёт", description="Проверить счёт", guild=discord.Object(id=guild_id))
async def money(interaction):
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    embed = discord.Embed(
        description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nНа вашем счету: {cur.fetchone()[0]} :coin:",
        color=0x1)
    embed.set_thumbnail(url=interaction.user.avatar)
    embed.set_author(name="Пользователь")
    await interaction.response.send_message(embed=embed)


@tree.command(name="перевести", description="перевести коины", guild=discord.Object(id=guild_id))
async def move(interaction: discord.Interaction, пользователь: discord.Member, сумма: int):
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    result1 = cur.fetchone()
    cur.execute("SELECT money FROM Users WHERE name = ?", (пользователь.id,))
    result2 = cur.fetchone()
    if result1[0] >= сумма:
        if сумма == 0:
            embed = discord.Embed(
                description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nКак мне кажется от нуля нечего не "
                            f"изменится",
                color=0x1)
        elif сумма < 0:
            embed = discord.Embed(
                description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nЧисло должно быть положительным",
                color=0x1)
        else:
            if interaction.user == пользователь:
                embed = discord.Embed(
                    description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nПеревести самому себе"
                                f" интересно конечно но зачем ?",
                    color=0x1)
            else:
                embed = discord.Embed(
                    description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nВы перевели {сумма} :coin: "
                                f"пользователю <@{пользователь.id}>| `{пользователь}`",
                    color=0x1)
        cur.execute("UPDATE Users SET money = ? WHERE name = ?", (result1[0] - сумма, interaction.user.id))
        con.commit()
        cur.execute("UPDATE Users SET money = ? WHERE name = ?", (result2[0] + сумма, пользователь.id))
        con.commit()
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nу вас недостаточно средств ",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)


# @tree.context_menu()
# async def command(interaction: discord.Interaction):


@tree.command(name="награда", description="Ежедневная награда", guild=discord.Object(id=guild_id))
async def reward(interaction: discord.Interaction):
    cur.execute("SELECT money, timeout FROM Users WHERE name = ?", (interaction.user.id,))
    result = cur.fetchone()
    if result[1] != get_current_date() or result[0] == 0:
        new_valui = int(result[0]) + 100
        cur.execute("UPDATE Users SET money = ?, timeout = ? WHERE name = ?",
                    (new_valui, get_current_date(), interaction.user.id))
        con.commit()
        embed = discord.Embed(
            description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nВы получили 100 :coin: Следующую "
                        "награду, можно будет получить завтра.",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        embed = discord.Embed(
            description=f"<@{interaction.user.id}> | `{interaction.user}`\n\nНаграда была уже получена, следующую "
                        "награду, можно будет получить завтра.",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="правила", guild=discord.Object(id=guild_id))
async def t4(interaction: discord.Interaction, правило: str, описание: str, наказание: str, длительность: str):
    with open("data_file.json", "r", encoding="utf-8") as read_file:
        data = json.load(read_file)
    data["post" + str(len(data) + 1)] = {
        "rules": правило,
        "description": описание,
        "punishment": наказание,
        "duration": длительность
    }
    with open("data_file.json", "w", encoding="utf-8") as write_file:
        json.dump(data, write_file, indent=4)
    embed = discord.Embed(color=0x000000)
    embed.title = "** " + правило + "**"
    embed.add_field(name=f"**> Описание **", value=f"```" + описание + "```", inline=False)
    embed.add_field(name=f"**> Наказание **", value=f"```" + наказание + "```", inline=True)
    embed.add_field(name=f"**> Длительность **", value=f"```" + длительность + "```", inline=True)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="правила-отправить", guild=discord.Object(id=guild_id))
async def t5(interaction: discord.Interaction):
    with open("data_file.json", "r", encoding="utf-8") as read_file:
        data = json.load(read_file)
    for i in data.values():
        embed = discord.Embed(color=0x000000)
        embed.title = "** " + i["rules"] + "**"
        embed.add_field(name=f"**> Описание **", value=f"```" + i["description"] + "```", inline=False)
        embed.add_field(name=f"**> Наказание **", value=f"```" + i["punishment"] + "```", inline=True)
        embed.add_field(name=f"**> Длительность **", value=f"```" + i["duration"] + "```", inline=True)
        await interaction.channel.send(embed=embed)


# @tree.command(name="мод-меню")
@tree.context_menu(name="мод-меню", guild=discord.Object(id=guild_id))
async def check(interaction: discord.Interaction, пользователь: discord.Member):
    cur.execute("SELECT * FROM Users WHERE name = ?", (пользователь.id,))
    entries = cur.fetchone()
    if entries[3] != 0:
        n1 = "Снять бан"
        ban1 = f"<t:{entries[3]}>"
    else:
        n1 = "Бан"
        ban1 = 0
    if entries[4] != 0:
        n2 = "Снять мьют"
        mute1 = f"<t:{entries[4]}>"
    else:
        n2 = "Мьют"
        mute1 = 0

    class ban_modal(discord.ui.Modal, title='Наказание'):
        m1 = discord.ui.TextInput(label='Время', placeholder="1d")
        m2 = discord.ui.TextInput(label='Причина', placeholder="flowle_")
        m3 = discord.ui.TextInput(label='Комментарий', placeholder="Бла бла бла", required=False)

        async def on_submit(self, interaction1: discord.Interaction):
            await ban(interaction1, пользователь, str(self.m1), str(self.m2), str(self.m3))

    class unban_modal(discord.ui.Modal, title='Наказание'):
        m2 = discord.ui.TextInput(label='Причина', placeholder="flowle_")
        m3 = discord.ui.TextInput(label='Комментарий', placeholder="Бла бла бла", required=False)

        async def on_submit(self, interaction1: discord.Interaction):
            await unban(interaction1, пользователь, str(self.m2), str(self.m3))

    async def mod_ban(interaction: discord.Interaction):
        m = button1.label
        if m == "Бан":
            await interaction.response.send_modal(ban_modal())
        else:
            await interaction.response.send_modal(unban_modal())

    class mute_modal(discord.ui.Modal, title='Наказание'):
        m1 = discord.ui.TextInput(label='Время', placeholder="1d")
        m2 = discord.ui.TextInput(label='Причина', placeholder="flowle_")
        m3 = discord.ui.TextInput(label='Комментарий', placeholder="Бла бла бла", required=False)

        async def on_submit(self, interaction1: discord.Interaction):
            await mute(interaction1, пользователь, str(self.m1), str(self.m2), str(self.m3))

    class unmute_modal(discord.ui.Modal, title='Наказание'):
        m2 = discord.ui.TextInput(label='Причина', placeholder="flowle_")
        m3 = discord.ui.TextInput(label='Комментарий', placeholder="Бла бла бла", required=False)

        async def on_submit(self, interaction1: discord.Interaction):
            await unmute(interaction1, пользователь, str(self.m2), str(self.m3))

    async def mod_mute(interaction: discord.Interaction):
        m = button2.label
        if m == "Мьют":
            await interaction.response.send_modal(mute_modal())
        else:
            await interaction.response.send_modal(unmute_modal())

    async def history(interaction: discord.Interaction):
        s1 = ""
        cur.execute("SELECT * FROM History WHERE name == ?", (пользователь.id,))
        all_entries = cur.fetchall()
        if len(all_entries) > 0:
            s1 += "## История наказаний\n`  Тип / Дата  ` `  Причина  ` `⠀⠀⠀Модератор⠀⠀⠀`\n"
            for i in all_entries:
                if i[2] == 0:
                    s1 += "<:pred:1267205995231187056> "
                elif i[2] == 1:
                    s1 += "<:ban:1267205964315103394> "
                elif i[2] == 2:
                    s1 += "<:mute:1267205986108571700> "
                elif i[2] == 3:
                    s1 += "<:pred:1267205995231187056> "
                s1 += f"<t:{str(i[3])}:d>⠀{str(i[4])}⠀⠀⠀<@!{str(i[5])}>\n"


        else:
            s1 += "Нечего нету"

        embed = discord.Embed(description=s1, color=0x1)
        await interaction.response.send_message(embed=embed, ephemeral=True)

    view = View()
    if interaction.user.id != пользователь.id:
        button1 = Button(style=discord.ButtonStyle.gray, label=n1)
        view.add_item(button1)
        button1.callback = mod_ban
        button2 = Button(style=discord.ButtonStyle.gray, label=n2)
        view.add_item(button2)
        button2.callback = mod_mute
        button3 = Button(style=discord.ButtonStyle.gray, label='Предупреждение')
        view.add_item(button3)
    button4 = Button(style=discord.ButtonStyle.gray, label='История наказаний', row=1)
    view.add_item(button4)
    button4.callback = history

    embed = discord.Embed(
        description=f"<@{пользователь.id}> | `{пользователь}`\n\nНа счету: {entries[1]} :coin:\nВремя разбана:"
                    f" {ban1}\nВремя размута: {mute1}\n",
        color=0x1)
    embed.set_thumbnail(url=пользователь.avatar)
    embed.set_author(name="Пользователь")
    await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@tree.command(name="ивент-пост", guild=discord.Object(id=guild_id))
@app_commands.autocomplete(ивент=menu)
async def event1(interaction: discord.Interaction, ивент: str, ссылка: str):
    interaction1 = interaction
    category = guild.get_channel(event_categorize)
    voice = await guild.create_voice_channel(name=str(ивент), reason="Начало ивента", user_limit=15, category=category)
    channel = Bot.get_channel(event_chat)
    embed = discord.Embed(description=f"**Event {ивент}**\nНачат ивент `{ивент}`", color=0x1)
    embed1 = discord.Embed(description=f"**Event {ивент}**\nОкончен ивент `{ивент}`", color=0x1)
    embed2 = discord.Embed(
        description=f"**Event {ивент}**\nГолосовой канал ивента создан  -  -  -  >  {voice.jump_url} ", color=0x1)
    embed3 = discord.Embed(
        description=f"**Event {ивент}**\nИвент был завершён\n\nP.S Не забудьте выписать в канал "
                    f"<#1143981422097481778> награды пользователей + скриншоты за каждую проведённую игру данного "
                    f"ивента (Скриншот конца каждой игры).",
        color=0x1)

    async def callback2(interaction2):
        if interaction2.user.id == interaction1.user.id:
            await interaction2.response.send_message(embed=embed3)
            await channel.send(embed=embed1)
            await voice.delete()
        else:
            await interaction2.response.send_message("123")

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


@tree.command(name="казино", guild=discord.Object(id=guild_id))
async def casino(interaction: discord.Interaction, ставка: int):
    r = random2.randint(0, 1)
    max_values = 1000
    cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
    result = cur.fetchone()
    if ставка > max_values:
        embed = discord.Embed(
            description=f"<@{interaction.user.id}> | `{interaction.user}`\n\n Ваша ставка привышает лимит, "
                        f"максимальная ставка {max_values} :coin:",
            color=0x1)
        embed.set_thumbnail(url=interaction.user.avatar)
        embed.set_author(name="Пользователь")
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        if int(result[0]) < ставка:
            embed = discord.Embed(
                description=f"<@{interaction.user.id}> | `{interaction.user}`\n\n У Вас не достаточно средств",
                color=0x1)
            embed.set_thumbnail(url=interaction.user.avatar)
            embed.set_author(name="Пользователь")
            await interaction.response.send_message(embed=embed, ephemeral=True)
        else:
            if r == 1:
                new_valui = int(result[0]) + (ставка * 2 - ставка)
                cur.execute("UPDATE Users SET money = ? WHERE name = ?", (new_valui, interaction.user.id))
                con.commit()
                embed = discord.Embed(
                    description=f"<@{interaction.user.id}> | `{interaction.user}`\n\n Ваша ставка выйграла, Вы "
                                f"получили: {int(ставка * 2)} :coin:",
                    color=0x1)
                embed.set_thumbnail(url=interaction.user.avatar)
                embed.set_author(name="Пользователь")
                await interaction.response.send_message(embed=embed, ephemeral=True)
            else:
                new_valui = int(result[0]) - ставка
                cur.execute("UPDATE Users SET money = ? WHERE name = ?", (new_valui, interaction.user.id))
                con.commit()
                embed = discord.Embed(
                    description=f"<@{interaction.user.id}> | `{interaction.user}`\n\n Ваша ставка проиграла, Вы "
                                f"потеряли: {ставка} :coin:",
                    color=0x1)
                embed.set_thumbnail(url=interaction.user.avatar)
                embed.set_author(name="Пользователь")
                await interaction.response.send_message(embed=embed, ephemeral=True)


@tree.command(name="магазин", guild=discord.Object(id=guild_id))
async def shop1(interaction: discord.Interaction, лот: int = -1):
    view = View()
    button = Button(style=discord.ButtonStyle.primary, label='Подтвердить')

    async def button_callback(interaction: discord.Interaction, price):
        cur.execute("SELECT money FROM Users WHERE name = ?", (interaction.user.id,))
        if price[3] > cur.fetchone():
            await interaction.response.send_message('Не достаточно средств', ephemeral=True)
        else:
            await interaction.response.send_message('Вы купили товар', ephemeral=True)

    if лот == -1:
        r = []
        r1 = ""
        cur.execute("SELECT * FROM Shop")
        for i in cur.fetchall():
            r.append("лот: " + str(i[0]) + " Название: " + "<@&" + str(i[1]) + ">" + " Цена: " + str(
                i[3]) + " :coin:" + "\n")
        for i in range(len(r)):
            r1 += r[i]
        embed = discord.Embed(
            description=r1,
            color=0x36393E)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        cur.execute("SELECT * FROM Shop WHERE id = ?", (лот,))
        result = cur.fetchone()
        button.callback = button_callback(interaction, result)
        view.add_item(button)
        embed = discord.Embed(
            description=f"Название: {result[1]}\nОписание: {result[2]}\nЦена: {result[3]} :coin:",
            color=0x36393E)
        await interaction.response.send_message(embed=embed, view=view, ephemeral=True)


@tree.command(name="createl", description="123", guild=discord.Object(id=guild_id))
async def create_lot(interaction: discord.Interaction, name: discord.Role, description: str, price: float):
    print(f"{name} \n {description} \n {price}")
    data = [None, name.id, description, price]

    cur.execute("INSERT INTO Shop VALUES(?, ?, ?, ?)", data)
    con.commit()
    await interaction.response.send_message(f"{name} \n {description} \n {price}", ephemeral=True)


class Dropdown(discord.ui.Select):
    def __init__(self):
        options = [
            discord.SelectOption(label="Мафия", value="Мафия"),
            discord.SelectOption(label="Бункер", value="Бункер"),
            discord.SelectOption(label="Алиас/Шляпа", value="Алиас/Шляпа"),
            discord.SelectOption(label="Крокодил", value="Крокодил"),
            discord.SelectOption(label="GarlicPhone", value="GarlicPhone"),
            discord.SelectOption(label="JackBox", value="JackBox"),
            discord.SelectOption(label="Codenames", value="Codenames"),
            discord.SelectOption(label="Намёк понял", value="Намёк понял"),
            discord.SelectOption(label="Шпион", value="Шпион"),
            discord.SelectOption(label="Кто я?", value="Кто я?"),
            discord.SelectOption(label="Криминалист", value="Криминалист")
        ]

        super().__init__(placeholder="Игры", min_values=0, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Вы выбрали: {self.values[0]}", ephemeral=True)


class DropdownView(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.add_item(Dropdown())


@tree.command(name="roles", guild=discord.Object(id=guild_id))
async def roles(interaction: discord.Interaction):
    view = DropdownView()
    await interaction.response.send_message("Выберите серверные роли:", view=view, ephemeral=True)


@tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    embed = discord.Embed(description=f"Со мной что-то случилось\n{error}", color=0x1)
    embed1 = discord.Embed(description=f"Со мной что-то случилось\nобратитесь к администрации", color=0x1)

    await interaction.response.send_message(embed=embed1, ephemeral=True)
    await bot_chat.send(embed=embed)


async def remove_role(guild: discord.Guild, member_id, role):
    member = await guild.fetch_member(member_id)
    if member:
        await member.remove_roles(role, reason="(auto)")
    else:
        print(f"Member not found for {role.name}.")


@tasks.loop(minutes=1)
async def remove_expired_roles():
    current_time = datetime.datetime.now().timestamp()

    cur.execute("SELECT * FROM Users WHERE ban_timeout != 0 OR mute_timeout != 0")
    all_entries = cur.fetchall()

    for entry in all_entries:
        member_id = int(entry[0])
        ban_timeout = entry[3] if entry[3] != 0 else None
        mute_timeout = entry[4] if entry[4] != 0 else None

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
    global guild, role_ban, role_mute, log_chat, bot_chat
    await Bot.change_presence(status=discord.Status.online)
    await tree.sync(guild=discord.Object(id=guild_id))
    remove_expired_roles.start()
    guild = Bot.get_guild(guild_id)
    role_ban = guild.get_role(role_ban_id)
    role_mute = guild.get_role(role_mute_id)
    log_chat = Bot.get_channel(log_chat_id)
    bot_chat = Bot.get_channel(bot_chat_id)
    for member in guild.members:
        if not member.bot:
            cur.execute("SELECT money FROM Users WHERE name = ?", (member.id,))
            if cur.fetchone() is None:
                create_profile(member.id)
                print(member.name)


@Bot.event
async def on_member_join(member):
    role = guild.get_role(1245751061705392208)
    embed = discord.Embed(description=f"{member} присоединился к серверу")

    cur.execute("SELECT name FROM Users WHERE name = ?", (member.id,))
    entrie = cur.fetchone()
    if entrie is None:
        embed = discord.Embed(description=f"{member} впервые присоединился к серверу")
        create_profile(member.id)
    await log_chat.send(embed=embed)
    await member.add_roles(role, reason="(auto)")


@Bot.event
async def on_member_remove(member):
    embed = discord.Embed(description=f"{member} покинул сервер")
    await log_chat.send(embed=embed)


Bot.run(token)
