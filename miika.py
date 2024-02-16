import discord
from discord import app_commands
import tracemalloc
import youtube_dl


intents = discord.Intents.default()

intents.typing = False
intents.presences = False
intents.message_content = True

Bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(Bot)
tracemalloc.start()

guildID = 1007951389198127195
voiceID = 1182728289085816952


@tree.command(name="заказ-музыки", description="Добавить музызку в очередь воспроизведения",
              guild=discord.Object(id=guildID))
async def music(interaction, ссылка: str):
    print(ссылка)
    print(ссылка[0:29])
    if ссылка[0:29] == "https://www.youtube.com/watch":
        print(1231)
        embed = discord.Embed(description=f"""Ответ который человек получит""", color=0x1)
        await interaction.response.send_message(embed=embed, ephemeral=True)
        guild = Bot.get_guild(guildID)
        if guild is not None:
            channel = guild.get_channel(voiceID)
            if channel is not None:
                voice = await channel.connect()


                # Используем youtube_dl для получения информации о видео
                ydl_info = youtube_dl.YoutubeDL().extract_info(ссылка, download=False)
                # Получаем URL потока аудио
                audio_url = ydl_info["formats"][0]["url"]

                player = channel.
                await player.play()



@tree.error
async def on_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    embed = discord.Embed(description=f"""Со мной что-то случилось\n{error}""", color=0x1)
    await interaction.response.send_message(embed=embed, ephemeral=True)


@Bot.event
async def on_ready():
    await Bot.change_presence(status=discord.Status.online)
    await tree.sync(guild=discord.Object(id=guildID))


# ------------------------------------------------------------------------------------#
Bot.run("MTE4MDk1ODg5MTI1MzcxMDk3OQ.GWwbxh.g2qjwjipcGSz_shzgIOzvuavFUvXDXxi9ts7z4")
