import discord
import json
import asyncio
from discord.ext import commands
from datetime import datetime
from pytz import timezone

TOKEN = 'REPLACE'

version = "1.0"
release_date = "05.20.25"
timezone_ny = timezone('America/New_York')

OWNER_IDS = [748671909280874586, 799738478341390378, 330590178546548736]

ALERT_INPUT_CHANNEL = 1361347865888292894
SOURCE_BOT_ID = 1374403366859440128

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True


bot = commands.Bot(command_prefix = '-/', intents=intents)


def load_alert_channels():
    try:
        with open("alert_channels.json", "r") as file:
            data = json.load(file)
            return data.get("alert_channels", [])
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error loading alert channels: {e}")
        return []


def time_now():
    return datetime.now(timezone_ny).strftime("%m/%d/%y  ●  %I:%M:%S %p ")


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.event
async def on_message(message):
    await bot.process_commands(message)

    if message.channel.id != ALERT_INPUT_CHANNEL or message.author.id != SOURCE_BOT_ID:
        return

    if not message.embeds:
        return

    embeds = []
    current_time = time_now()
    for original_embed in message.embeds:
        embed = discord.Embed.from_dict(original_embed.to_dict())
        embed.set_footer(text=f"Official TT alert bot. For informational purposes only, not financial advice\n{current_time}")
        embeds.append(embed)

    files = [await attachment.to_file() for attachment in message.attachments] if message.attachments else []

    alert_channels = load_alert_channels()

    for entry in alert_channels:
        channel_id = entry["channel_id"]
        role = entry["role"]
        tech_analysis = entry["techAnalysis"]

        channel = bot.get_channel(channel_id)
        if channel:
            try:
                embed_text = embeds[0].description if embeds and embeds[0].description else ""

                initial_content = f"{embed_text} {role}".strip()

                mes = await channel.send(content=initial_content, embeds=embeds, files=files if files else None)

                await asyncio.sleep(1)
                await mes.edit(content=role)
                
            except Exception as e:
                print(f"❌ Error sending to {channel_id}: {e}")


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
        role_mention = "@everyone"
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
            current_time = time_now()
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
        current_time = time_now()
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
    current_time = time_now()
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
        current_time = time_now()
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
        current_time = time_now()
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
