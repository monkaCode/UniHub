from typing import Literal
import discord
from discord.ext import commands
import json

# with open("guilds.json") as f:
#     guildsJson = json.load(f)


# Counter that counts on how many servers the bot is connected
guild_count = 0 

token = "OTc0NjkwOTAwNjY2MTE4MjE1.GmogGT.hQCi7cfrP-FeWMxfTQcv2mqMHwS_dFIB2_FoBU"
guild = discord.Object(974705743087431691)
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="unihub!", intents=intents, help_command=None, status=discord.Status.online, activity=discord.Game("UniHub"))


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    guild_count = len(bot.guilds)
    print(guild_count)

@bot.event
async def on_guild_join(guild=guild):
    print(guild.id)

@bot.tree.command(guild=guild)
async def create_event(interaction: discord.Interaction, category:Literal["Learning", "Gaming", "Dating"], name:str, max_user:int=None):
    await interaction.response.send_message(name)

@bot.tree.command(guild=guild)
async def help(interaction: discord.Interaction):
    embed = discord.Embed(title = "Help page", description = "All accessible commannds", color = 0x1db546)
    await interaction.response.send_message(embed=embed)

@bot.command()
async def sync(ctx):
    print(await bot.tree.sync(guild=guild))
    await ctx.send("Synced")

bot.run(token)
