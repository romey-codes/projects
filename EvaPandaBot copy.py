import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime
from pytz import timezone

TOKEN = ''#REPLACE

version = "1.3"
release_date = "11.24.24"
timezone_la = timezone('America/Los_Angeles')
timezone_ny = timezone('America/New_York')

OWNER_ID = 536430344489009153
OWNER_IDS = [536430344489009153, 799738478341390378]

ALERT_CHANNEL_ID = 1018936481903030432

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

user_conversations = {}
forwarded_messages = {}


bot = commands.Bot(command_prefix = '!', intents=intents)


def load_alert_channels():
    try:
        with open("alert_channels.json", "r") as file:
            data = json.load(file)
            return data.get("alert_channels", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading alert channels: {e}")
        return []


def time():
    return datetime.now(timezone_ny).strftime("%m/%d/%y  ●  %I:%M:%S %p ")

async def embed_maker(command, message, ctx):
    if(command == 'say'):
        embed_color = discord.Color.from_rgb(50, 154, 240)
        embed_title = 'Update:'
    elif(command == 'bto'):
        embed_color = discord.Color.from_rgb(0, 255, 0)
        embed_title = 'Open'
    elif(command == 'stc'):
        embed_color = discord.Color.from_rgb(255,0,0)
        embed_title = 'Close'

    embed = discord.Embed(title = embed_title, description = message, color = embed_color)
    current_time = time()
    embed.set_footer(text = f"©Turning Points Entities, Inc. Official EvaPanda Bot. For Information purposes only, not financial advice.\n{current_time}", icon_url=bot.user.avatar.url)
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")

    return embed, files


async def send_alert_message(ctx, command_type: str, message: str):
    embed_color = discord.Color.from_rgb(216, 132, 59)
    embed1 = discord.Embed(
        title="Got it!",
        description=f"Working on sending your message now.",
        color=embed_color
    )
    current_time = time()
    embed1.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}", icon_url=bot.user.avatar.url)

    mes_ref = await ctx.send(embed=embed1)
    embed, files = await embed_maker(command_type, message, ctx)
    alert_channels = load_alert_channels()

    for entry in alert_channels:
        channel_id = entry["channel_id"]
        role = entry["role"]
        channel = bot.get_channel(channel_id)

        if channel:
            try:
                if files:
                    new_files = [await attachment.to_file() for attachment in ctx.message.attachments]
                    await channel.send(content=role, embed=embed, files=new_files)
                else:
                    await channel.send(content=role, embed=embed)
            except Exception as e:
                print(f"Failed to send message to channel {channel_id}: {e}")

    embed2_color = discord.Color.from_rgb(0,255,0)
    embed2 = discord.Embed(
        title="Task complete!",
        description=f"Sent message to all channels.",
        color=embed2_color
        )
    current_time = time()
    embed2.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}", icon_url=bot.user.avatar.url)

    await mes_ref.edit(embed=embed2)

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')
    for guild in bot.guilds:
        print(f"- {guild.name} (ID: {guild.id})")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if isinstance(message.channel, discord.DMChannel) and message.author.id == OWNER_ID and message.reference:
        
        replied_message_id = message.reference.message_id
        if replied_message_id in forwarded_messages:
            user_id = forwarded_messages[replied_message_id]
            user = user_conversations.get(user_id)

            if user:
                try:
                    await user.send(message.content)
                    await message.channel.send(f"Replied to {user.name}: {message.content}")
                except Exception as e:
                    await message.channel.send(f"An error occurred while sending the reply: {e}")
            else:
                await message.channel.send("User not found in conversations.")
        else:
            await message.channel.send("The replied message was not found in the forwarded messages dictionary.")

    if isinstance(message.channel, discord.DMChannel) and message.author.id != OWNER_ID:
        user_id = message.author.id
        user_conversations[user_id] = message.author

        owner = await bot.fetch_user(OWNER_ID)
        if owner:
            forwarded_message = await owner.send(f"Message from {message.author} (ID: {user_id}): {message.content}")
            forwarded_messages[forwarded_message.id] = user_id

    await bot.process_commands(message)


@bot.command()
async def say(ctx, *, message: str):
    if ctx.channel.id == ALERT_CHANNEL_ID:
        if message.lower().startswith("bto"):
            command_type = "bto"
        elif message.lower().startswith("stc"):
            command_type = "stc"
        else:
            command_type = "say"
        await send_alert_message(ctx, command_type, message)

@bot.command()
async def bto(ctx, *, message: str):
    if ctx.channel.id == ALERT_CHANNEL_ID:
        await send_alert_message(ctx, "bto", message)

@bot.command()
async def stc(ctx, *, message: str):
    if ctx.channel.id == ALERT_CHANNEL_ID:
        await send_alert_message(ctx, "stc", message)


@bot.command()
async def add(ctx, channel: discord.TextChannel, role: discord.Role = None):
    if ctx.author.id not in OWNER_IDS:
        await ctx.send("You do not have permission to use this command.")
        return

    if role is None or role.id == ctx.guild.id:
        role_mention = "@everyone"
    else:
        role_mention = role.mention

    new_entry = {
        "channel_id": channel.id,
        "role": role_mention
    }

    try:
        with open("alert_channels.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {"alert_channels": []}

    for entry in data["alert_channels"]:
        if entry["channel_id"] == channel.id:
            embed_color = discord.Color.from_rgb(216, 132, 59)
            embed = discord.Embed(
                title="Error",
                description=f"Channel already added: {channel.mention}",
                color=embed_color
            )
            current_time = time()
            embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")
            await ctx.send(embed=embed)
            return

    data["alert_channels"].append(new_entry)

    try:
        with open("alert_channels.json", "w") as file:
            json.dump(data, file, indent=4)

        embed_color = discord.Color.from_rgb(216, 132, 59)
        embed = discord.Embed(
            title="Channel Added Successfully",
            description=f"Channel: {channel.mention}\nRole: {role_mention}",
            color=embed_color
        )
        current_time = time()
        embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Failed to save data: {e}")

@bot.command()
async def show(ctx):
    """
    Displays all the channels listed in the alert_channels.json file, showing the channel name, ID, and server name.
    """
    if ctx.author.id not in OWNER_IDS:
        return

    try:
        with open("alert_channels.json", "r") as file:
            data = json.load(file)
            alert_channels = data.get("alert_channels", [])
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("The alert_channels.json file is missing or corrupted.")
        return

    if not alert_channels:
        await ctx.send("No alert channels found in the JSON file.")
        return

    embed = discord.Embed(
        title="Configured Alert Channels",
        description="List of channels and the servers they belong to.",
        color=discord.Color.blue()
    )
    current_time = time()
    embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")

    for entry in alert_channels:
        channel_id = entry.get("channel_id")
        role = entry.get("role")
        channel = bot.get_channel(channel_id)

        if channel:
            server_name = channel.guild.name
            channel_name = channel.name
            embed.add_field(
                name=f"{server_name}",
                value=f"Channel: #{channel_name} ({channel_id})\nRole: {role}",
                inline=False
            )
        else:
            embed.add_field(
                name="Unknown Server",
                value=f"Channel ID: {channel_id} (Not accessible or deleted)",
                inline=False
            )

    await ctx.send(embed=embed)


@bot.command()
async def remove(ctx, channel_id: int):
    """
    Removes a server channel from the alert_channels.json file.
    Usage: `=remove <channel_id>`
    """
    if ctx.author.id not in OWNER_IDS:
        await ctx.send("You do not have permission to use this command.")
        return

    try:
        with open("alert_channels.json", "r") as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("The alert_channels.json file is missing or corrupted.")
        return

    removed = False
    for entry in data["alert_channels"]:
        if entry["channel_id"] == channel_id:
            data["alert_channels"].remove(entry)
            removed = True
            break

    if not removed:
        embed_color = discord.Color.from_rgb(216, 132, 59)
        embed = discord.Embed(
            title="Error",
            description=f"Channel ID: `{channel_id}` could not be removed.",
            color=embed_color
        )
        current_time = time()
        embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")

        await ctx.send(embed=embed)
        await ctx.send(f"Channel ID {channel_id} was not found in the alert channels list.")
        return

    try:
        with open("alert_channels.json", "w") as file:
            json.dump(data, file, indent=4)

        embed_color = discord.Color.from_rgb(216, 132, 59)
        embed = discord.Embed(
            title="Channel Removed Successfully",
            description=f"Channel ID: `{channel_id}` has been removed.",
            color=embed_color
        )
        current_time = time()
        embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")

        await ctx.send(embed=embed)

    except Exception as e:
        await ctx.send(f"Failed to save data: {e}")


@bot.command()
async def delete(ctx):
    """
    Deletes the last message sent by the bot in the alert channels listed in the JSON file.
    """
    if ctx.author.id not in OWNER_IDS:
        await ctx.send("You do not have permission to use this command.")
        return

    alert_channels = load_alert_channels()

    if not alert_channels:
        await ctx.send("No alert channels configured in the JSON file.")
        return

    deleted_count = 0
    for entry in alert_channels:
        channel_id = entry.get("channel_id")
        channel = bot.get_channel(channel_id)

        if channel:
            try:
                async for message in channel.history(limit=10):
                    if message.author == bot.user:
                        await message.delete()
                        deleted_count += 1
                        break
            except discord.Forbidden:
                await ctx.send(f"Missing permissions to manage messages in {channel.mention}.")
            except discord.HTTPException as e:
                await ctx.send(f"An error occurred while fetching or deleting messages in {channel.mention}: {e}")
        else:
            await ctx.send(f"Channel with ID `{channel_id}` not found or inaccessible.")

    if deleted_count > 0:
        await ctx.send(f"Deleted the last message sent by the bot in {deleted_count} channel(s).")
    else:
        await ctx.send("No messages sent by the bot were found in the configured channels.")




            
bot.run(TOKEN)
