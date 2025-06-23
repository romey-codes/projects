#WAGER KINGS
import discord
import asyncio
from discord.ext import commands
from datetime import datetime, timedelta
from pytz import timezone
import time

#VARIABLES
version = "1.5"
release_date = "04.19.25"

timezone_ny = timezone('America/New_York')

moderator_role_id = 1285405130107260940

BOT_TOKEN = "REPLACE"

ALLOWED_ROLE_IDS = [1285405139225677834, 1285405130107260940, 1322290000657776782]

ROLE_IDS = [1344541811477057537] #Pro-Mmber

WATCHED_CHANNELS = [
    1316201110121484288, #Keyz-picks
    1316201964958126121, #rocks-picks
    1316202128263483493, #gaz-picks
    1319756243623088309, #dixies-picks
    1355700825464246282, #geeks-picks
    1327017155606351913, #bo's-picks
    1295514674598514688, #degen-picks
]

intents = discord.Intents.all()
intents.messages = True
bot = commands.Bot(command_prefix = "+", intents=intents)

def timeAZ():
    return datetime.now(timezone_ny).strftime("%m/%d/%y  ●  %I:%M:%S %p ")

def embed_maker(message):
    embed = discord.Embed(
        title=f'Alert:',
        description= f'{message.content}',
        color=discord.Color.from_rgb(0,0,0)#259,132,59
    )
    embed.set_author(
        name=message.author.display_name,
        icon_url=message.author.avatar.url
    )                
    current_time_value = timeAZ()
    embed.set_footer(
        text=f"WAGERKINGZ\nBot Version {version} -- Released {release_date}\nBot by BOOMBORG\n{current_time_value}"
    )
    if message.attachments:
        for attachment in message.attachments:
            embed.set_image(url=attachment.url)
            break

    return embed

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name}')

@bot.event
async def on_message(message):
    if message.channel.id in WATCHED_CHANNELS:

        if(message.channel.id == 1316201110121484288): #keyz-picks
            asyncio.create_task(send_dm_to_subs(message, 1325969479884079217, "Keyz picks"))

        if(message.channel.id == 1316201964958126121): #rocks-picks
            asyncio.create_task(send_dm_to_subs(message, 1325970603118690357, "Rocks picks"))

        if(message.channel.id == 1355700825464246282): #Geeks-picks
            asyncio.create_task(send_dm_to_subs(message, 1363257099290677451, "Geeks picks"))

        if(message.channel.id == 1319756243623088309): #Dixies-picks
            asyncio.create_task(send_dm_to_subs(message, 1325970989397573712, "Dixies picks"))

        if(message.channel.id == 1295514674598514688): #degen-picks
            asyncio.create_task(send_dm_to_subs(message, 1325971225889214536, "Degen picks"))

        if(message.channel.id == 1332061077562986660): #stones-picks
            asyncio.create_task(send_dm_to_subs(message, 1334765815450570823, "stones picks"))

        if(message.channel.id == 1327017155606351913): #bo's-picks
            asyncio.create_task(send_dm_to_subs(message, 1327654474528854106, "bo's picks"))

        # if(message.channel.id == 1316201110121484288): #crypto-picks
        #     asyncio.create_task(send_dm_to_subs(message, 1325972211298992138, "Crypto picks"))
            
    await bot.process_commands(message)

@bot.command()
async def bet(ctx, *, message: str):
    user_roles = [role.id for role in ctx.author.roles]
    if not any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        await ctx.send("You do not have the required role to use this command.")
        return
    
    embed_color = discord.Color.from_rgb(0, 128, 128)

    embed = discord.Embed(title = "🎰 New Bet: ",description=message, color=embed_color)

    embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    current_time = timeAZ()
    embed.set_footer(text=f"Sports Betting can result in significant financial loss and addiction. Do not treat any messages as advice.\n{current_time}")
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")

    if ctx.message.reference:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        ref_mes = await ctx.send(f"🎰: {message} @everyone", embed=embed, reference=referenced_message, files=files)
    else:
        ref_mes = await ctx.send(f"🎰: {message} @everyone", embed=embed, files=files)
    
    await ctx.message.delete()
    await ref_mes.edit(content = '@everyone')



@bot.command()
async def cash(ctx, *, message: str):
    user_roles = [role.id for role in ctx.author.roles]
    if not any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        await ctx.send("You do not have the required role to use this command.")
        return
    
    embed_color = discord.Color.from_rgb(0, 255, 0)

    embed = discord.Embed(title = "💵 CASHOUT:",description=message, color=embed_color)

    embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    current_time = timeAZ()
    embed.set_footer(text=f"Sports Betting can result in significant financial loss and addiction. Do not treat any messages as advice.\n{current_time}")
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")

    if ctx.message.reference:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        ref_mes = await ctx.send(f"💵: {message} @everyone", embed=embed, reference=referenced_message, files=files)
    else:
        ref_mes = await ctx.send(f"💵: {message} @everyone", embed=embed, files=files)

    await ref_mes.edit(content = '@everyone')
    await ctx.message.delete()

@bot.command()
async def win(ctx, *, message: str):
    user_roles = [role.id for role in ctx.author.roles]
    if not any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        await ctx.send("You do not have the required role to use this command.")
        return
    
    embed_color = discord.Color.from_rgb(0, 255, 0)

    embed = discord.Embed(title = "WIN: ",description=message, color=embed_color)

    embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    current_time = timeAZ()
    embed.set_footer(text=f"Sports Betting can result in significant financial loss and addiction. Do not treat any messages as advice.\n{current_time}")
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")

    if ctx.message.reference:
        referenced_message = await ctx.channel.fetch_message(ctx.message.reference.message_id)
        ref_mes = await ctx.send(f"💵: {message} @everyone", embed=embed, reference=referenced_message, files=files)
    else:
        ref_mes = await ctx.send(f"💵: {message} @everyone", embed=embed, files=files)

    await ref_mes.edit(content = '@everyone')
    await ctx.message.delete()

@bot.command()
async def update(ctx, *, message: str):
    user_roles = [role.id for role in ctx.author.roles]
    if not any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        await ctx.send("You do not have the required role to use this command.")
        return
    
    embed_color = discord.Color.from_rgb(50, 154, 240)

    embed = discord.Embed(title = "Update: ",description=message, color=embed_color)

    embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    current_time = timeAZ()
    embed.set_footer(text=f"Sports Betting can result in significant financial loss and addiction. Do not treat any messages as advice.\n{current_time}")
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")


    ref_mes = await ctx.send(f'🔵Update: {message} @everyone', embed=embed, files=files)
    await ref_mes.edit(content = '@everyone')
    await ctx.message.delete()

@bot.command()
async def open(ctx, *, message: str):
    user_roles = [role.id for role in ctx.author.roles]
    if not any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        await ctx.send("You do not have the required role to use this command.")
        return
    
    role_id = 1325972211298992138

    role = ctx.guild.get_role(role_id)

    embed_color = discord.Color.from_rgb(0,255,0)

    embed = discord.Embed(title = "NEW POSITION: ", description = message, color = embed_color)

    embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    current_time = timeAZ()
    embed.set_footer(text=f"WAGERKINGZ - Information purposes only, not financial advice\nBot Version {version} -- Released {release_date}\n{current_time}")
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")


    ref_mes = await ctx.send(f'🟢OPENED: {message} {role.mention}', embed=embed, files=files)
    await ref_mes.edit(content = '@everyone')
    await ctx.message.delete()


@bot.command()
async def close(ctx, *, message: str):
    user_roles = [role.id for role in ctx.author.roles]
    if not any(role_id in ALLOWED_ROLE_IDS for role_id in user_roles):
        await ctx.send("You do not have the required role to use this command.")
        return
    
    role_id = 1325972211298992138

    role = ctx.guild.get_role(role_id)

    embed_color = discord.Color.from_rgb(255,0,0)

    embed = discord.Embed(title = "CLOSED: ", description = message, color = embed_color)

    embed.set_author(name=f"{ctx.author.display_name}", icon_url=ctx.author.avatar.url)

    current_time = timeAZ()
    embed.set_footer(text=f"WAGERKINGZ - Information purposes only, not financial advice\nBot Version {version} -- Released {release_date}\n{current_time}")
    files = []
    if ctx.message.attachments:
        for attachment in ctx.message.attachments:
            file = await attachment.to_file()
            files.append(file)
            embed.set_image(url=f"attachment://{file.filename}")


    ref_mes = await ctx.send(f'🔴CLOSED: {message} {role.mention}', embed=embed, files=files)
    await ref_mes.edit(content = '@everyone')
    await ctx.message.delete()


async def send_dm_to_subs(message, role_to_send, role_name):
    report_channel_id = 1325632085112655982
    status_channel = bot.get_channel(report_channel_id)
    start_time = time.perf_counter()
    
    if message.channel.id in WATCHED_CHANNELS:
        role = message.guild.get_role(role_to_send)
        if role:
            if message.mentions or message.role_mentions or message.mention_everyone:

                await message.add_reaction("🎰")
                await asyncio.sleep(1.5)

                message_link = f"https://discord.com/channels/{message.guild.id}/{message.channel.id}/{message.id}"
                message_desc = message.content
                
                
                if message.embeds:
                    embeds_to_send = [embed.copy() for embed in message.embeds]
                    if embeds_to_send[0].description:
                        message_desc = embeds_to_send[0].description
                else:
                    embed = embed_maker(message)
                    embeds_to_send = [embed]
                
                i = 0
                sent = 0
                failed = 0

                for member in role.members:
                    
                    has_role_in_ids = any(r.id in ROLE_IDS for r in member.roles)
                    
                    if has_role_in_ids:
                        try:
                            for embed in embeds_to_send:
                                mes_ref = await member.send(content=f'{message.channel.name}: {message_desc}')
                                await mes_ref.edit(content=f'New alert from {message.channel.name}\nSee it here: {message_link}', embed=embed)
                                sent +=1
                                await asyncio.sleep(1)

                        except asyncio.TimeoutError:
                            await status_channel.send(f"Timeout while sending DM to {member.name}")
                        except discord.Forbidden:
                            failed +=1

                end_time = time.perf_counter()
                elapsed_time = end_time - start_time
                minutes, seconds = divmod(elapsed_time, 60)
                embed_report = discord.Embed(
                    title=f'Task Complete: ',
                    description= f'Successful messeges sent: {sent}\nFailed: {failed}\nElapsed time: {int(minutes)} minutes and {seconds:.2f} seconds.\nSent to all {role_name} subs',
                    color=discord.Color.from_rgb(255,132,59)
                )                
                current_time_value = timeAZ()
                embed_report.set_footer(
                    text=f"BOOMBORG\n{current_time_value}"
                )
                await status_channel.send(embed=embed_report)


bot.run(BOT_TOKEN)
