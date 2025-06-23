import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime
from pytz import timezone

TOKEN = 'REPLACE'

version = "3.1"
release_date = "05.14.25"
timezone_la = timezone('America/Los_Angeles')
timezone_ny = timezone('America/New_York')

OWNER_ID = 536430344489009153
OWNER_IDS = [536430344489009153, 799738478341390378]

ALERT_CHANNEL_ID = 1018936481903030432

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

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
    elif(command == 'ta'):
        embed_color = discord.Color.from_rgb(247, 134, 39)
        embed_title = 'Analysis:'

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
        description="Working on sending your message now.",
        color=embed_color
    )
    current_time = time()
    embed1.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}", icon_url=bot.user.avatar.url)
    mes_ref = await ctx.send(embed=embed1)

    embed, files = await embed_maker(command_type, message, ctx)
    alert_channels = load_alert_channels()
    files = [await attachment.to_file() for attachment in ctx.message.attachments] if ctx.message.attachments else []

    failed_channels = []

    batch_size = 2
    for i in range(0, len(alert_channels), batch_size):
        batch = alert_channels[i:i + batch_size]
        tasks = []

        for entry in batch:
            channel_id = entry["channel_id"]
            role = entry["role"]
            tech_analysis = entry["techAnalysis"]

            if command_type == "ta" and tech_analysis != 1:
                continue

            channel = bot.get_channel(channel_id)
            if not channel:
                continue

            attachments = [await attachment.to_file() for attachment in ctx.message.attachments] if ctx.message.attachments else []
            tasks.append(send_with_handling(channel, role, embed, attachments, failed_channels))


        await asyncio.gather(*tasks)
        await asyncio.sleep(2)  # 2 second delay between batches

    embed2_color = discord.Color.from_rgb(0, 255, 0)
    embed2 = discord.Embed(
        title="Task complete!",
        description="Sent message to all channels." if not failed_channels else f"Some sends failed: {len(failed_channels)} channel(s)",
        color=embed2_color
    )
    current_time = time()
    embed2.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}", icon_url=bot.user.avatar.url)
    await mes_ref.edit(embed=embed2)


async def send_with_handling(channel, role, embed, files, failed_channels):
    try:
        await channel.send(content=role, embed=embed, files=files if files else None)
    except Exception as e:
        print(f"Error sending to channel {channel.id}: {e}")
        failed_channels.append(channel.id)


def load_blocked_users():
    try:
        with open("blocked_users.json", "r") as file:
            return json.load(file).get("blocked_users", [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_blocked_users(blocked_users):
    try:
        with open("blocked_users.json", "w") as file:
            json.dump({"blocked_users": blocked_users}, file, indent=4)
    except Exception as e:
        print(f"Failed to save blocked users: {e}")

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    blocked_users = load_blocked_users()

    if message.author.id in blocked_users:
        return
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
async def block(ctx):
    """
    Blocks a user by adding them to the blocked_users.json file.
    Usage: !block (used in reply to a message in DMs).
    """
    if not isinstance(ctx.channel, discord.DMChannel) or ctx.author.id != OWNER_ID:
        return

    if not ctx.message.reference:
        await ctx.send("Please use this command as a reply to a user's message to block them.")
        return

    replied_message_id = ctx.message.reference.message_id
    replied_message = await ctx.channel.fetch_message(replied_message_id)

    user_id = replied_message.author.id

    blocked_users = load_blocked_users()

    if user_id in blocked_users:
        await ctx.send(f"User {replied_message.author} is already blocked.")
        return

    blocked_users.append(user_id)
    save_blocked_users(blocked_users)

    await ctx.send(f"Blocked user {replied_message.author} (ID: {user_id}).")

@bot.command()
async def unblock(ctx, user_id: int):
    """
    Unblocks a user by removing them from the blocked_users.json file.
    Usage: !unblock <user_id>
    """
    if ctx.author.id != OWNER_ID:
        return

    # Load the current blocked users
    blocked_users = load_blocked_users()

    if user_id not in blocked_users:
        await ctx.send(f"User ID {user_id} is not in the blocked list.")
        return

    # Remove the user from the blocked list and save
    blocked_users.remove(user_id)
    save_blocked_users(blocked_users)

    await ctx.send(f"Unblocked user with ID {user_id}.")


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
async def ta(ctx, *, message: str):
    if ctx.channel.id == ALERT_CHANNEL_ID:
        await send_alert_message(ctx, "ta", message)

@bot.command()
async def mes(ctx, *, message: str):
    """
    Sends a message to all alert channels. If @here or @everyone is included in the message,
    they will be replaced with the role assigned to each channel. Also forwards images and attachments.
    """
    if ctx.channel.id != ALERT_CHANNEL_ID:
        return
    
    embed_color = discord.Color.from_rgb(216, 132, 59)
    embed1 = discord.Embed(
        title="Got it!",
        description=f"Working on sending your message now.",
        color=embed_color
    )
    current_time = time()
    embed1.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}", icon_url=bot.user.avatar.url)

    mes_ref = await ctx.send(embed=embed1)

    alert_channels = load_alert_channels()

    if not alert_channels:
        await ctx.send("No alert channels found in the JSON file.")
        return


    files = [await attachment.to_file() for attachment in ctx.message.attachments] if ctx.message.attachments else []

    send_tasks = []
    for entry in alert_channels:
        channel_id = entry["channel_id"]
        role = entry["role"]

        updated_message = message
        if role == "@everyone":
            updated_message = message.replace("@here", "@everyone")
        elif role:
            updated_message = message.replace("@here", role).replace("@everyone", role)

        channel = bot.get_channel(channel_id)
        if channel:
            try:
                task = channel.send(content=updated_message, files=files if files else None)
                send_tasks.append(task)
            except Exception as e:
                print(f"Failed to queue message for channel {channel_id}: {e}")

    results = await asyncio.gather(*send_tasks, return_exceptions=True)

    for i, result in enumerate(results):
        if isinstance(result, Exception):
            print(f"Error sending to channel {alert_channels[i]['channel_id']}: {result}")

    
    embed2_color = discord.Color.from_rgb(0,255,0)
    embed2 = discord.Embed(
        title="Task complete!",
        description=f"Sent message to all channels.",
        color=embed2_color
        )
    current_time = time()
    embed2.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}", icon_url=bot.user.avatar.url)

    await mes_ref.edit(embed=embed2)
    


@bot.command()
async def add(ctx, channel: discord.TextChannel, role: discord.Role = None, tech_analysis: bool = False):
    """
    Adds a server channel and role to the alert_channels.json file.
    Usage: `=add #channel-name [@role-mention]`
    If no role is provided, it defaults to `@everyone`.
    """
    if ctx.author.id not in OWNER_IDS:
        await ctx.send("You do not have permission to use this command.")
        return

    if role is None or role.id == ctx.guild.id:
        role_mention = ""
    else:
        role_mention = role.mention

    tech_analysis_value = 1 if tech_analysis else 0

    new_entry = {
        "channel_id": channel.id,
        "role": role_mention,
        "techAnalysis" : tech_analysis_value,
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
            description=(
                f"Channel: {channel.mention}\n"
                f"Role: {role_mention}\n"
                f"Tech Analysis: {tech_analysis}\n"
            ),
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

    embeds = []
    current_embed = discord.Embed(
        title="Configured Alert Channels",
        description="List of channels and the servers they belong to.",
        color=discord.Color.blue()
    )
    current_time = time()
    current_embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")

    for i, entry in enumerate(alert_channels):
        channel_id = entry.get("channel_id")
        role = entry.get("role")
        tech_analysis = entry.get("techAnalysis")
        channel = bot.get_channel(channel_id)

        if channel:
            server_name = channel.guild.name
            channel_name = channel.name
            field_name = f"{server_name}"
            field_value = f"Channel: #{channel_name} ({channel_id})\nRole: {role}\nTechnical analysis: {tech_analysis}"
        else:
            field_name = "Unknown Server"
            field_value = f"Channel ID: {channel_id} (Not accessible or deleted)"
        current_embed.add_field(name=field_name, value=field_value, inline=False)

        if (i + 1) % 25 == 0 or (i + 1) == len(alert_channels):
            embeds.append(current_embed)
            current_embed = discord.Embed(
                title="Configured Alert Channels (Continued)",
                description="List of channels and the servers they belong to.",
                color=discord.Color.blue()
            )
            current_embed.set_footer(text=f"Bot Version {version} -- Released {release_date}\n{current_time}")

    for embed in embeds:
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
                # Fetch the last 50 messages in the channel to look for the bot's most recent message
                async for message in channel.history(limit=10):
                    if message.author == bot.user:
                        await message.delete()
                        deleted_count += 1
                        break  # Only delete the most recent bot message
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
