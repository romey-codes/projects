import discord
import asyncio
from discord.ext import commands
from datetime import datetime
from pytz import timezone

TOKEN = ''  # Replace
ROLE_ID = 1300883179346989066  # Alert-sub role ID

version = "2.4"
release_date = "11.23.24"
arizona_tz = timezone('America/New_York')

WATCHED_CHANNELS = {
    728711121128652851: 1305951344946974770,  # 🌟️prof-and-kian-alerts
    836438781233070130: 1305951663634255942,  # 🌟️eva-alerts
    1199404302700118167: 1305951839736299611,  # 🌟kess-ideas
    1199911694537854996: 1305951966203215894,  # 🌟np-alerts
    1235366372385493074: 1305952069064069140,  # 🌟ab-trades
    1270064409691291774: 1305952402804965577,  # 🌟tt-alerts
    1293188203607625728: 1305952649358741586,  # 🌟remz-alerts
    1296869003138174997: 1305952537052053615,  # 🌟neal-analysis
    1085224967894995004: 1305952842099462175,  # 👀long-term-investments
    1181672382365175808: None,  # Crypto-talk (special handling)
    1299130025005551761: None,  # Alertbot-setup
}

ROLE_IDS = [885910828086362132, 718643316786462772, 718643325502226483]  # pro-member, lifetime member, paid member
intents = discord.Intents.default()
intents.messages = True
intents.message_content = True
intents.members = True

bot = commands.Bot(command_prefix="-/", intents=intents)


@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}!')
    activity = discord.Activity(type=discord.ActivityType.watching, name="for alerts")
    await bot.change_presence(status=discord.Status.online, activity=activity)


def timeAZ():
    ny_time = datetime.now(arizona_tz)
    return ny_time.strftime("%m/%d/%y  ●  %I:%M:%S %p ")


def embed_maker(message):
    embed = discord.Embed(
        title="Alert:",
        description=message.content,
        color=discord.Color.from_rgb(216, 132, 59),
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url,
    )
    embed.set_footer(
        text=(
            f"Owls Investment Group LLC. Informational purposes only. Not financial advice.\n"
            f"Bot Version {version} -- Released {release_date}\nBot by Roman\n{timeAZ()}"
        )
    )
    if message.attachments:
        embed.set_image(url=message.attachments[0].url)
    return embed


async def send_dm(message, role_id):
    guild_role = message.guild.get_role(role_id)
    if not guild_role:
        return

    message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
    embed = embed_maker(message)

    for member in guild_role.members:
        if any(role.id in ROLE_IDS for role in member.roles) and ROLE_ID not in [r.id for r in member.roles]:
            try:
                await member.send(content=f'New alert from {message.channel.name}\nSee it here: {message_link}', embed=embed)
                print(f"DM sent to {member.name}")
            except discord.Forbidden:
                print(f"Couldn't DM {member.name}")
            except asyncio.TimeoutError:
                print(f"Timeout while sending DM to {member.name}")


@bot.event
async def on_message(message):
    if message.author == bot.user or message.channel.id not in WATCHED_CHANNELS:
        return

    role_to_send = WATCHED_CHANNELS[message.channel.id]

    if message.channel.id == 1181672382365175808:  # Crypto-talk
        author_role_id = 718643429852053555
        crypto_role_sub = 1309996465858416640
        if any(role.id == author_role_id for role in message.author.roles) or message.mention_everyone:
            if any(role.id == crypto_role_sub for role in message.role_mentions):
                asyncio.create_task(send_dm(message, crypto_role_sub))

    elif message.channel.id == 1299130025005551761:  # Alert bot setup
        asyncio.create_task(send_dm(message, ROLE_ID))

    elif role_to_send:
        asyncio.create_task(send_dm(message, role_to_send))

    await bot.process_commands(message)


bot.run(TOKEN)

