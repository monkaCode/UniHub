from typing import Literal
import discord
from discord.ext import commands
import json

with open("guilds.json") as f:
    guildsJson = json.load(f)

token = "OTc0NjkwOTAwNjY2MTE4MjE1.GmogGT.hQCi7cfrP-FeWMxfTQcv2mqMHwS_dFIB2_FoBU"
guild = discord.Object(974705743087431691)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="unihub!", intents=intents, help_command=None, status=discord.Status.online, activity=discord.Game("UniHub"))

with open("guilds.json", "w") as f:
    guildsJson = json.load(f)
    guildsJson.append({"id": f"{guild.id}"})

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.event
async def on_guild_join(guild=guild):
    with open("guilds.json", "w") as f:
        guildsJson = json.load(f)
        guildsJson.append({""})
    print(guild.id)

@bot.tree.command(guild=guild)
async def create_event(interaction: discord.Interaction, category:Literal["Learning", "Gaming", "Dating"], name:str, max_user:int=None):
    await interaction.response.send_message(name)

@bot.command()
async def sync(ctx):
    print(await bot.tree.sync(guild=guild))
    await ctx.send("Synced")

bot.run(token)
print("Hello World")
