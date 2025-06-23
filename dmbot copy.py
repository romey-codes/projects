import discord
import asyncio
from discord.ext import commands, tasks
from datetime import datetime, time as dt_time
from pytz import timezone
from collections import deque
import time

TOKEN = 'REPLACE'
ROLE_ID = 1300883179346989066 #Alert-sub role ID

version = "4.5"
release_date = "05.23.2025"
arizona_tz = timezone('America/New_York')

DELAY = 1.0

WATCHED_CHANNELS = [
    728711121128652851,  # 🌟️prof-and-kian-alerts
    836438781233070130,  # 🌟️eva-alerts
    1199911694537854996,  # 🌟np-alerts
    1235366372385493074,  # 🌟ab-trades
    1270064409691291774,  # 🌟tt-alerts
    1296869003138174997,  # 🌟neal-analysis
    1319444838826905650,  #🌟florida-man-analysis
    1349016879364046868, #🌟robindahoot-alerts
    1085224967894995004,  # 👀long-term-investments
    1097963394029600839, #futures-trading
    1299130025005551761   #Alertbot-setup
]

SLOWMODE_DELAY = 10
CHECK_INTERVAL = 60
CHANNEL_ID = 718643687097368658

ROLE_IDS = [885910828086362132, 718643316786462772, 718643325502226483, 718643444989427753]#pro-member, lifetime member, paid member 885910828086362132
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True


bot = commands.Bot(command_prefix="$", intents=intents)

report_channel_id = 1293951583268376700
status_channel = bot.get_channel(report_channel_id)

repeat_channel_id = 718643687097368658


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    activity = discord.Activity(type=discord.ActivityType.watching, name="for alerts 👀")
    await bot.change_presence(status=discord.Status.online, activity=activity)
    check_slowmode.start()
                    

def timeAZ():
    ny_time = datetime.now(arizona_tz)
    return ny_time.strftime("%m/%d/%y  ●  %I:%M:%S %p ")

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return
    
    if message.channel.id == 1354488917633798246 and message.author.id in [1354488919433019492, 799738478341390378]:
        segments = message.content.split("🔴")[1:]
        for segment in segments:
            segment = segment.strip()
            
            if not (segment.startswith("MOC") or segment.startswith("MOO")):
                segment = segment.split("\n", 1)[0].strip()

            segment = segment.upper()
            
            if segment:
                news_channel_id = 1081082844807434292
                spy_qqq_id = 1337165306858049546
                repeat_chan = bot.get_channel(repeat_channel_id)
                news_chan = bot.get_channel(news_channel_id)
                spy_qqq_chan = bot.get_channel(spy_qqq_id)
                if repeat_chan:
                    embed = discord.Embed(title="🚨 NEWS ALERT", description=segment, color=discord.Color.from_rgb(255,0,0))
                    curr_time = timeAZ()
                    embed.set_footer(text=f"INFORMATION OBTAINED FROM BLOOMBERG\nBOT VERSION {version} -- RELEASED {release_date}\n{curr_time}")
                    await repeat_chan.send(embed=embed)
                    await spy_qqq_chan.send(embed=embed)
                    ref_mess = await news_chan.send(f'🚨{segment} @here', embed=embed)
                    await ref_mess.edit(content='@here')
 

    if message.channel.id in WATCHED_CHANNELS:
        
        if (message.channel.id == 728711121128652851): #prof-and-kian-alerts
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305951344946974770, "prof-and-kian-alerts"))

        elif (message.channel.id == 836438781233070130): #eva-alerts
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305951663634255942, "eva-alerts"))

        elif (message.channel.id == 1199911694537854996): #np-alerts
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305951966203215894, "np-alerts"))

        elif (message.channel.id == 1235366372385493074): #ab-alerts
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305952069064069140, "ab-alerts"))

        elif (message.channel.id == 1270064409691291774): #tt-alerts
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305952402804965577, "tt-alerts"))

        elif (message.channel.id == 1296869003138174997): #neal-analysis
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305952537052053615, "neal-analysis"))

        elif (message.channel.id == 1319444838826905650): #florida-man-analysis
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1319761011611271228, "Florida-man-analysis"))

        elif (message.channel.id == 1349016879364046868): #robindahood-alerts
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1349017933879447583, "Robindahood-alerts"))

        elif (message.channel.id == 1085224967894995004): #long-term-investments
            asyncio.create_task(send_dm_to_members(message))
            asyncio.create_task(send_dm_to_subs(message, 1305952842099462175, "long-term-investments"))

        elif (message.channel.id == 1097963394029600839): #Futures-trading
            author_role_id = 718643444989427753
            futures_role_sub = 1336353283383754805
            if (any(role.id == author_role_id for role in message.author.roles) or message.mention_everyone):
                if any(role.id == futures_role_sub for role in message.role_mentions):
                    asyncio.create_task(send_dm_to_subs(message, 1336353283383754805, 'Futures-trading'))
                    asyncio.create_task(send_dm_to_members(message))

        elif (message.channel.id == 1299130025005551761): #Alert bot setup
            asyncio.create_task(send_dm_to_members(message))

    await bot.process_commands(message)


def embed_maker(message):
    embed = discord.Embed(
        title=f'Message:',
        description= f'{message.content}',
        color=discord.Color.from_rgb(247,147,26)
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url
    )                

    current_time = timeAZ()

    embed.set_footer(
        text=f"Owls Investment Group LLC. Informational purposes only. Not financial advice.\nBot Version {version} -- Released {release_date}\n{current_time}"
    )
    if message.attachments:
        for attachment in message.attachments:
            embed.set_image(url=attachment.url)
            break

    return embed




async def send_dm(member, message_desc, embeds_to_send, message_link, channel_name):
    try:
        for embed in embeds_to_send:
            await member.send(content=f'{channel_name}: {message_desc}\nSee it here: {message_link}', embed=embed)
        return True
    except (discord.Forbidden, discord.HTTPException):
        return False

async def send_dm_batched(members, message_desc, embeds_to_send, message_link, channel_name, batch_size=10, delay=DELAY):
    results = []
    for i in range(0, len(members), batch_size):
        batch = members[i:i+batch_size]
        tasks = [send_dm(member, message_desc, embeds_to_send, message_link, channel_name) for member in batch]
        batch_results = await asyncio.gather(*tasks)
        results.extend(batch_results)
        await asyncio.sleep(delay)
    return results

async def send_dm_to_subs(message, role_to_send, role_name):
    status_channel = bot.get_channel(report_channel_id)
    start_time = time.perf_counter()
    
    if message.author == bot.user or message.channel.id not in WATCHED_CHANNELS:
        return

    role = message.guild.get_role(role_to_send)
    if not role:
        return

    if message.mentions or message.role_mentions or message.mention_everyone:
        await message.add_reaction("🏆")

        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        if message.embeds:
            embeds_to_send = [embed.copy() for embed in message.embeds]
            message_desc = embeds_to_send[0].description if embeds_to_send[0].description else message.content
        else:
            message_desc = message.content
            embeds_to_send = [embed_maker(message)]

        members = [
            m for m in role.members
            if any(r.id in ROLE_IDS for r in m.roles) and not any(r.id == ROLE_ID for r in m.roles)
        ]

        results = await send_dm_batched(members, message_desc, embeds_to_send, message_link, message.channel.name)
        sent = results.count(True)
        failed = results.count(False)

        elapsed = time.perf_counter() - start_time
        mins, secs = divmod(elapsed, 60)

        embed_report = discord.Embed(
            title='Task Complete',
            description=f'Successful messages sent: {sent}\nFailed: {failed}\nElapsed: {int(mins)}m {secs:.2f}s\nSent to all {role_name} subs',
            color=discord.Color.from_rgb(255, 132, 59)
        )
        embed_report.set_footer(text=f"BOOMBORG\n{timeAZ()}")
        await status_channel.send(embed=embed_report)

async def send_dm_to_members(message):
    status_channel = bot.get_channel(report_channel_id)
    start_time = time.perf_counter()

    if message.author == bot.user or message.channel.id not in WATCHED_CHANNELS:
        return

    role = message.guild.get_role(ROLE_ID)
    if not role:
        return

    if message.mentions or message.role_mentions or message.mention_everyone:
        message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
        if message.embeds:
            embeds_to_send = [embed.copy() for embed in message.embeds]
            message_desc = embeds_to_send[0].description if embeds_to_send[0].description else message.content
        else:
            message_desc = message.content
            embeds_to_send = [embed_maker(message)]

        members = [m for m in role.members if any(r.id in ROLE_IDS for r in m.roles)]
        results = await send_dm_batched(members, message_desc, embeds_to_send, message_link, message.channel.name)
        sent = results.count(True)
        failed = results.count(False)

        elapsed = time.perf_counter() - start_time
        mins, secs = divmod(elapsed, 60)

        embed_report_all = discord.Embed(
            title='Task Complete',
            description=f'Successful messages sent: {sent}\nFailed: {failed}\nElapsed: {int(mins)}m {secs:.2f}s\nSent to alert-subs',
            color=discord.Color.from_rgb(255, 132, 59)
        )
        embed_report_all.set_footer(text=f"BOOMBORG\n{timeAZ()}")
        await status_channel.send(embed=embed_report_all)

AUTHORIZED_USER_IDS = [799738478341390378]

@bot.command(name='delete')
async def delete_referenced_message(ctx):
    if ctx.author.id not in AUTHORIZED_USER_IDS:
        await ctx.send("🚫 You are not authorized to use this command.", delete_after=5)
        return

    if ctx.message.reference:
        try:
            referenced = await ctx.channel.fetch_message(ctx.message.reference.message_id)
            await referenced.delete()
            await ctx.message.delete()
            await ctx.send(f"DELETED POTENTIAL FRAUD BY: {referenced.author}")
        except discord.NotFound:
            await ctx.send("⚠️ Referenced message not found or already deleted.", delete_after=5)
        except discord.Forbidden:
            await ctx.send("🚫 I don't have permission to delete that message.", delete_after=5)
        except discord.HTTPException as e:
            await ctx.send(f"❌ Failed to delete message: {e}", delete_after=5)
    else:
        await ctx.send("❗ You must reply to a message to delete it using this command.", delete_after=5)



@tasks.loop(seconds=CHECK_INTERVAL)
async def check_slowmode():
    now = datetime.now(arizona_tz)
    weekday = now.weekday()
    current_time = now.time()
    
    start = dt_time(9, 25)
    end = dt_time(16, 0)

    in_range = start <= current_time <= end

    channel = bot.get_channel(CHANNEL_ID)
    if channel is None:
        print(f"Channel with ID {CHANNEL_ID} not found.")
        return

    if in_range and weekday < 5:  # Monday–Friday
        if weekday == 4:  # Friday
            target_delay = 5
        else:  # Monday–Thursday
            target_delay = SLOWMODE_DELAY
    else:
        target_delay = 0  # Turn off slowmode

    if channel.slowmode_delay != target_delay:
        await channel.edit(slowmode_delay=target_delay)
        print(f"Slowmode set to {target_delay}s in {channel.name}")


bot.run(TOKEN)
