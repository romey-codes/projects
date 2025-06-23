#IRONHEART CAPITAL BOT
#LIBRARIES
import discord
import asyncio
from discord.ext import commands
from datetime import datetime, time
from pytz import timezone
import tweepy

consumer_key = 'REPLACE'
consumer_secret = 'REPLACE'

access_token = 'REPLACE'
access_secret = 'REPLACE'

client = tweepy.Client(
    consumer_key = consumer_key, consumer_secret=consumer_secret, 
    access_token=access_token, access_token_secret = access_secret
)

version = "1.2"
release_date = "05.22.25"

timezone_ny = timezone('America/New_York')

allowed_role_ids = [1265113726227320885, 1262103584699580586, 1374107756620943522, 1265113726227320885]

alert_input_channel = 1327014816421773443

role_to_channel_map = {
    1327006001605640233: 1361347865888292894, #Inked-Alerts
    1327005302700376175: 1367546841813483655, #alex-alerts
    1328411088093708328: 1367546723324395561, #rob-trades
    1346486122712137798: 1367546607830040676, #swami alerts
    1366108142898774116: 1367546666546102352, #jbev-alerts
    1374482463304192014: 1374501185318293524 #tester-channel 
}

alert_channels = [
    1367546607830040676, #Swami-Alerts
    1361347865888292894, #TT-Alerts
    1367546723324395561, #Rob-Alerts
    1367546666546102352, #jbev-alerts
    1367546841813483655, #alex-alerts
    1374108781499387904 #ironheart-alert-testing
]

token = "REPLACE"

#INTENTIONS
intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix = "=", intents=intents)

#FUNCTIONS
def is_within_allowed_time():
    now = datetime.now(timezone_ny).time()
    start = time(5, 30)    # 5:30 AM
    end = time(21, 0)      # 9:00 PM

    return start <= now <= end

def get_time():
    return datetime.now(timezone_ny).strftime("%m/%d/%y  ●  %I:%M:%S %p ")

@bot.event
async def on_message(message_obj):
    if message_obj.channel.id == 1354488917633798246 and message_obj.author.id in [1354488919433019492, 799738478341390378]:
        segments = message_obj.content.split("🔴")[1:]
        for segment in segments:
            segment = segment.strip()
            
            if not (segment.startswith("MOC") or segment.startswith("MOO")):
                segment = segment.split("\n", 1)[0].strip()

            segment = segment.upper()

            if is_within_allowed_time():
                response = client.create_tweet(text = "🚨" + segment)

            
            if segment:
                news_chan_id = 1366768799503880223
                repeat_chan = bot.get_channel(news_chan_id)
                if repeat_chan:
                    embed = discord.Embed(title="🚨 NEWS ALERT", description=segment, color=discord.Color.from_rgb(255,0,0))
                    curr_time = get_time()
                    embed.set_footer(text=f"INFORMATION OBTAINED FROM BLOOMBERG\nBOT VERSION {version} -- RELEASED {release_date}\n{curr_time}")
                    await repeat_chan.send(embed=embed)
                    await asyncio.sleep(1)

    if message_obj.author.bot:
        return

    if message_obj.channel.id != alert_input_channel:
        return

    allowed = any(role.id in allowed_role_ids for role in message_obj.author.roles)
    if not allowed:
        return

    if not message_obj.role_mentions:
        await message_obj.channel.send("❌ Please mention a role to route the alert.")
        return

    target_role = message_obj.role_mentions[0]
    target_channel_id = role_to_channel_map.get(target_role.id)

    if not target_channel_id:
        await message_obj.channel.send("❌ That role is not mapped to a target channel.")
        return

    trimmed_message = message_obj.content.replace(f"<@&{target_role.id}>", "").strip()

    command_type = "say"
    if trimmed_message.lower().startswith(".bto"):
        command_type = "bto"
        trimmed_message = trimmed_message[4:].strip()
    elif trimmed_message.lower().startswith(".stc"):
        command_type = "stc"
        trimmed_message = trimmed_message[4:].strip()

    class DummyCtx:
        author = message_obj.author
        message = message_obj

    embed, files = await embed_maker(command_type, trimmed_message, DummyCtx, role_color=target_role.color)

    target_channel = message_obj.guild.get_channel(target_channel_id)
    if not target_channel:
        await message_obj.channel.send("❌ Target channel not found.")
        return

    mes = await target_channel.send(f"{trimmed_message} @everyone", embed=embed, files=files)
    await mes.edit(content="@everyone")



async def embed_maker(command, message, ctx, role_color=None):
    if(command == 'say'):
        embed_color = role_color or discord.Color.from_rgb(15, 74, 132)
    elif(command == 'bto'):
        embed_color = discord.Color.from_rgb(0, 255, 0)
        embed_title = 'OPEN:'
    elif(command == 'stc'):
        embed_color = discord.Color.from_rgb(255,0,0)
        embed_title = 'CLOSE'

    if(command == 'say'):
        embed = discord.Embed(description = message, color = embed_color)
    else:
        embed = discord.Embed(title = embed_title, description = message, color = embed_color)

    try:
        icon_url = ctx.author.avatar.url if ctx.author.avatar else bot.user.avatar.url
        embed.set_author(name=ctx.author.display_name, icon_url=icon_url)
    except Exception as e:
        embed.set_author(name=ctx.author.display_name, icon_url=bot.user.avatar.url)

    current_time = get_time()
    embed.set_footer(text = f"Ironheart Capital - For informational purposes only, not financial advice\n{current_time}", icon_url=bot.user.avatar.url)
    files = []
    if ctx.message.attachments:
         for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")

    return embed, files


async def send_alert_message(ctx, command_type: str, message: str):
    if ctx.channel.id != alert_input_channel:
        return

    allowed = any(role.id in allowed_role_ids for role in ctx.author.roles)
    if not allowed:
        return

    # Extract first role mention (if any)
    if ctx.message.role_mentions:
        target_role = ctx.message.role_mentions[0]
        target_channel_id = role_to_channel_map.get(target_role.id)
    else:
        await ctx.send("❌ Please mention a role to route the alert.")
        return

    if not target_channel_id:
        await ctx.send("❌ That role is not mapped to a target channel.")
        return

    # Trim role mention from the message
    trimmed_message = message.replace(f"<@&{target_role.id}>", "").strip()

    # Build embed
    embed, files = await embed_maker(command_type, trimmed_message, ctx, role_color=target_role.color)

    # Send to target channel
    target_channel = ctx.guild.get_channel(target_channel_id)
    if not target_channel:
        await ctx.send("❌ Target channel not found.")
        return

    mes = await target_channel.send(f"{message} @everyone", embed=embed, files=files)
    await mes.edit(content="@everyone")



bot.run(token)
