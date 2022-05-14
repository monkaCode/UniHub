from typing import Literal
import discord
from discord.ui import View, Button
from discord.ext import commands
import json

with open(r"guilds.json") as f:
    guildsJson = json.load(f)


# Counter that counts on how many servers the bot is connected
guild_count = 0 
class Color:
    green = 0x1ac436
    red = 0xc41a1a
    orange = 0xff9900


token = "OTc0NjkwOTAwNjY2MTE4MjE1.GmogGT.hQCi7cfrP-FeWMxfTQcv2mqMHwS_dFIB2_FoBU"
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="unihub!", intents=intents, help_command=None, status=discord.Status.online, activity=discord.Game("UniHub"))


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    guild_count = len(bot.guilds)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"connecting {guild_count} servers"))

@bot.event
async def on_guild_join(guild):
    x = len(guildsJson["servers"])
    guildsJson["servers"][x] = {"guild": guild.id, "channel": 0}
    with open("guilds.json", "w") as f:
        json.dump(guildsJson, f)

@bot.tree.command()
async def create_event(interaction: discord.Interaction, category:Literal["Learning", "Gaming", "Dating"], name:str, max_user:int=None):
    guildMain = bot.get_guild(974705743087431691)
    voiceChannel = await guildMain.create_voice_channel(name, category=discord.Object(974813975533482034))
    inviteLink = await guildMain.get_channel(voiceChannel.id).create_invite(max_uses=max_user, unique=True)
    button = Button(label="Event löschen", style=discord.ButtonStyle.red)
    async def button_callback(interaction:discord.Interaction):
        await guildMain.get_channel(voiceChannel.id).delete()
        await interaction.response.send_message(embed=discord.Embed(title="Du hast diese Event gelöscht"), ephemeral=True)

    button.callback = button_callback
    view = View()
    view.add_item(button)
    await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: Event wurde erstellt!", description=f"Name: **{name}**\nKategorie: **{category}**\nMaximale Nutzer: **{max_user}**\nHier beitreten: {inviteLink}", color=Color.green), view=view, ephemeral=True)
    with open(r"guilds.json") as f:
        guildsJson = json.load(f)
    for x in range(len(guildsJson["servers"])):
        await bot.get_guild(guildsJson["servers"][x]["guild"]).get_channel(guildsJson["servers"][x]["channel"]).send(embed=discord.Embed(title=name, description=f"Kategorie: {category}\nMaximale User: {max_user}\nBeitreten: {inviteLink}", color=Color.green))

@bot.tree.command()
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title = "Help page", description = "All accessible slash commands for UniHub.", color=Color.orange)
    createEventCommand = str("""```css\n/create_event```""")
    setInfoChannelCommand = str("""```css\n/set_info_channel```""")
    embed.set_thumbnail(url="https://cdn.discordapp.com/attachments/971405638460653688/974942963237023764/unknown.png")
    embed.add_field(name="Create event", value=createEventCommand + "\nto create a category with a name and optional to function to limit participants", inline=False)
    embed.add_field(name="Set the Unihub text channel", value =setInfoChannelCommand + "\nto set a channel which allows UniHub to share events", inline=False)
    embed.set_footer(text="Help page requested by:{}".format(interaction.user.display_name))
    await interaction.response.send_message(embed=embed)

@bot.tree.command()
async def set_info_channel(interaction:discord.Interaction, channelid:str):
    channelid = int(channelid)
    for x in range(len(guildsJson["servers"])):
        if(guildsJson["servers"][x]["guild"] == interaction.guild_id):
            guildsJson["servers"][x]["channel"] = channelid
            break
    with open("guilds.json", "w") as f:
        try:
            json.dump(guildsJson, f)
            await interaction.response.send_message(embed=discord.Embed(title=":white_check_mark: UniHub-Info-Channel wurde gespeichert.", description=f"Der aktuelle UniHub-Info-Channel ist <#{channelid}>", color=Color.green))
        except:
            await interaction.response.send_message(embed=discord.Embed(title=":x: Etwas ist schiefgelaufen!", color=Color.red))

@bot.command()
async def sync(ctx):
    print(await bot.tree.sync())
    await ctx.send("Synced")

bot.run(token)
