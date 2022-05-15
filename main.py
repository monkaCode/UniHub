from typing import Literal
import discord
from discord.ui import View, Button
from discord.ext import commands
import json

from numpy import true_divide

with open(r"guilds.json") as f:
    guildsJson = json.load(f)






'''
Class for Colorattributes
'''
class Color:
    green = 0x1ac436
    red = 0xc41a1a

# Counter that counts on how many servers the bot is connected
guild_count = 0

token = "OTc0NjkwOTAwNjY2MTE4MjE1.GmogGT.hQCi7cfrP-FeWMxfTQcv2mqMHwS_dFIB2_FoBU"
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="unihub!", intents=intents, help_command=None,
                   status=discord.Status.online, activity=discord.Game("UniHub"))


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    guild_count = len(bot.guilds)
    await bot.change_presence(status=discord.Status.online, activity=discord.Game(f"connecting {guild_count} servers"))


@bot.event
async def on_guild_join(guild):
    x = len(guildsJson["servers"])
    guildsJson["servers"].append({"guild": guild.id, "channel": 0})
    with open("guilds.json", "w") as f:
        json.dump(guildsJson, f)
    await bot.get_user(guild.owner_id).send(embed=discord.Embed(title="Vielen Dank dass du UniHub benutzt.", description="Führe den Command /set_info_channel aus um den Info-Channel festzulegen", color=Color.green))


@bot.tree.command()
async def create_event(interaction: discord.Interaction, category: Literal["Learning", "Gaming", "Dating"], name: str, max_user: int):
    """
    Command the user has to type to create an event 
    
    Parameters
    ----------
    category : Literal["Learning", "Gaming", "Dating"]

    name : str
        Name of the topic the user wants to create an event for 
    
    max_user : int 
        Maximum amount of users who can join the event

    """
    with open("ongoing_events.json") as f:
        ongoingEvents = json.load(f)
    ongoingEvents[str(interaction.user.id)] = {
        "category": category, "name": name, "user": [{"id": interaction.user.id}]}
    with open("ongoing_events.json", "w") as f:
        json.dump(ongoingEvents, f)
    guildMain = bot.get_guild(974705743087431691)
    perms = {
        guildMain.default_role: discord.PermissionOverwrite(view_channel=False)
    }
    voiceChannel = await guildMain.create_voice_channel(name, category=discord.Object(974813975533482034), overwrites=perms)
    inviteLink = await guildMain.get_channel(voiceChannel.id).create_invite(max_uses=max_user, unique=True)

    '''
    Class representing the Delete and Join-Voice-Channel Button
    '''
    class Buttons(discord.ui.View):
        def __init__(self, *, timeout=180):
            super().__init__(timeout=timeout)

        @discord.ui.button(label="Event löschen", style=discord.ButtonStyle.red)
        async def delete_event(self, buttonInteraction: discord.Interaction, button: discord.Button):
            """
            Button the user who created the channel can use to delete the channel  
            """
            button.disabled = True
            await guildMain.get_channel(voiceChannel.id).delete()
            await buttonInteraction.response.edit_message(embed=discord.Embed(title=":x: Event wurde gelöscht!", color=Color.red), view=self)

    view = Buttons()
    view.add_item(discord.ui.Button(label="Voice-Channel beitreten",
                  style=discord.ButtonStyle.link, url=inviteLink.url))
    await interaction.response.send_message(embed=discord.Embed(
        title=":white_check_mark: Event wurde erstellt!", 
        description=f"Name: **{name}**\nKategorie: **{category}**\nMaximale Nutzer: **{max_user}**", 
        color=Color.green), 
        view=view, 
        ephemeral=True
    )


    '''
    Class representing the Join and Leave Buttons 
    '''
    class InfoButtons(discord.ui.View):
        def __init__(self, *, timeout=180):
            super().__init__(timeout=timeout)
            self.uses = 1

        @discord.ui.button(label="Event beitreten", style=discord.ButtonStyle.green)
        async def join_event(self, buttonInteraction: discord.Interaction, button: discord.Button):
            """
            Button every other user who wants to join the event can click on to join
            Only allows users up to the given max_user in create_event

            """
            if(self.uses < max_user):
                with open("ongoing_events.json") as f:
                    ongoingEvents = json.load(f)
                for x in range(len(ongoingEvents[str(interaction.user.id)]["user"])):
                    if(ongoingEvents[str(interaction.user.id)]["user"][x]["id"] == buttonInteraction.user.id):
                        await buttonInteraction.response.send_message(embed=discord.Embed(
                            title=":x: Du bist dem Event schon beigetreten", color=Color.red), ephemeral=True)
                        return
                self.uses += 1
                ongoingEvents[str(interaction.user.id)]["user"].append(
                    {"id": buttonInteraction.user.id})
                with open("ongoing_events.json", "w") as f:
                    json.dump(ongoingEvents, f)
                channel = await guildMain.get_channel(voiceChannel.id)
                perms = channel.overwrites_for(buttonInteraction.user)
                perms.view_channel = True
                await channel.set_permissions(buttonInteraction.user, overwrite=perms)
                if(self.uses == max_user):
                    button.disabled = True
            else:
                button.disabled = True
            await buttonInteraction.response.edit_message(embed=discord.Embed(
                title=name, description=f"Kategorie: **{category}**\nAktuelle User: **{self.uses}** / **{max_user}**", 
                color=Color.green), view=self)

        @discord.ui.button(label="Event verlassen", style=discord.ButtonStyle.red)
        async def leave_event(self, buttonInteraction: discord.Interaction, button: discord.Button):
            """
            Button users can click on to leave the event they have already joined
            """
            with open("ongoing_events.json") as f:
                ongoingEvents = json.load(f)
            for x in range(len(ongoingEvents[str(interaction.user.id)]["user"])):
                if(ongoingEvents[str(interaction.user.id)]["user"][x]["id"] == buttonInteraction.user.id):
                    ongoingEvents[str(interaction.user.id)]["user"].pop(x)
                    with open("ongoing_events.json", "w") as f:
                        json.dump(ongoingEvents, f)
                    await buttonInteraction.response.send_message(embed=discord.Embed(title="Du hast das Event verlassen", 
                    color=Color.green), ephemeral=True)
                    self.uses -= 1
                    await buttonInteraction.followup.edit_message(message_id=buttonInteraction.message.id, embed=discord.Embed(
                        title=name, description=f"Kategorie: **{category}**\nAktuelle User: **{self.uses}** / **{max_user}**", 
                        color=Color.green), view=self)
                    break
            await buttonInteraction.response.send_message(embed=discord.Embed(title=":x: Du bist nicht in diesem Event", 
            color=Color.red), ephemeral=True)
    infoView = InfoButtons()
    infoView.add_item(discord.ui.Button(label="Voice-Channel beitreten",
                      style=discord.ButtonStyle.link, url=inviteLink.url))
    with open(r"guilds.json") as f:
        guildsJson = json.load(f)
    for x in range(len(guildsJson["servers"])):
        await bot.get_guild(guildsJson["servers"][x]["guild"]).get_channel(guildsJson["servers"][x]["channel"]).send(
            embed=discord.Embed(title=name, description=f"Kategorie: **{category}**\nAktuelle User: **{infoView.uses}** / **{max_user}**", color=Color.green), view=infoView)


@bot.tree.command()
async def help(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Help page", description="All accessible slash commannds for UniHub.", color=Color.green)
    embed.set_thumbnail(
        url="https://cdn.discordapp.com/attachments/971405638460653688/974942963237023764/unknown.png")
    embed.add_field(name="Create event",
                    value="/create_event to create a category with a name and function to limit participants", inline=False)
    embed.add_field(name="Set the Unihub text channel",
                    value="/set_info_channel to set a channel which allows UniHub to share events", inline=False)
    embed.set_footer(text="Help page requested by:{}".format(
        interaction.user.display_name))
    await interaction.response.send_message(embed=embed, ephemeral=True)


@bot.tree.command()
async def set_info_channel(interaction: discord.Interaction, channelid: str):
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
