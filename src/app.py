import discord
from discord.ext import commands
# from pretty_help import PrettyHelp, EmojiMenu
import os 
import asyncio
import re 
import sqlite3 
import random
from py import capy
from dotenv import load_dotenv
from cogs import Economy  
conn = sqlite3.connect("database.db")
c = conn.cursor()



# shen zhiming is so cool 

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
# menu = EmojiMenu(page_left="\U0001F44D", page_right="👎", remove=":discord:743511195197374563", active_time=5)
# ending_note = "The ending note from {ctx.bot.user.name}\nFor command {help.clean_prefix}{help.invoked_with}"
bot = commands.Bot(command_prefix="capy ", intents=intents)
guild_ids = []

# db initialisation below 
# c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER)')

def initialise_user(user_id):
    c.execute("INSERT INTO users (user_id, balance) VALUES (?, ?)", (user_id, 0))

    conn.commit()

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(capy)
    await bot.change_presence(activity=discord.Game(name="capy help"))

@bot.event
async def on_message(message):
    # call initialise_user if user is not in the database and give 1000 coins
    if not c.execute("SELECT * FROM users WHERE user_id = ?", (message.author.id,)).fetchone():
        initialise_user(message.author.id)
        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (1000, message.author.id))
    conn.commit()

    # add guild_id to guild_ids list if not already in it
    if message.guild.id not in guild_ids:
        guild_ids.append(message.guild.id)

    await bot.process_commands(message)

bot.event
async def on_member_join(member): 
    print(f"{member} joined {member.guild}")
    await member.send(f"Welcome to {member.guild}!")

# @bot.slash_command(guild_ids = [1080649131057483858])
# async def hello(ctx):
#     await ctx.send("Hello!")

# Utility commands 
@bot.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(bot.latency * 1000)}ms")

@bot.command()
async def stats(ctx):
    embed = discord.Embed(title="Server statistics", color=discord.Color.teal())
    embed.set_image(url=ctx.guild.icon.url)
    embed.add_field(name="Members", value=ctx.guild.member_count, inline=False)
    embed.add_field(name="Channels", value=len(ctx.guild.channels), inline=False)
    embed.add_field(name="Roles", value=len(ctx.guild.roles), inline=False)
    await ctx.send(embed=embed)


# Moderation commands 
@bot.command()
@commands.has_permissions(manage_messages=True)
async def purge(ctx, amount: int):
    await ctx.channel.purge(limit=amount+1)
    await ctx.send(f"{ctx.author.mention} purged {amount} messages")

@purge.error
async def purge_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify an amount of messages to delete")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to do that")

@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.kick(reason=reason)
    await ctx.send(f"{member.mention} has been kicked")

@kick.error
async def kick_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a member to kick")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to do that")

@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member, *, reason="No reason provided"):
    await member.ban(reason=reason)
    await ctx.send(f"{member.mention} has been banned")

@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a member to ban")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to do that")


@bot.command()
async def softban(ctx, member: discord.Member, reason = "No reason provided"):
    await member.ban(reason=reason)
    await member.unban(reason="Softban")
    await ctx.send(f"{member.mention} has been softbanned")
    await ctx.channel.purge(limit=100, check=lambda m: m.author == member)

# Helper function to convert duration string to seconds
def parse_duration(duration):
    pattern = r'(?P<months>\d+m)?(?P<days>\d+d)?(?P<hours>\d+h)?(?P<minutes>\d+m)?(?P<seconds>\d+s)?'
    match = re.match(pattern, duration, re.IGNORECASE)

    if not match:
        return None

    total_seconds = 0
    for key, value in match.groupdict().items():
        if value:
            if key == 'months':
                total_seconds += int(value[:-1]) * 2629746  # Seconds in a month (30.44 days)
            elif key == 'days':
                total_seconds += int(value[:-1]) * 86400
            elif key == 'hours':
                total_seconds += int(value[:-1]) * 3600
            elif key == 'minutes':
                total_seconds += int(value[:-1]) * 60
            elif key == 'seconds':
                total_seconds += int(value[:-1])

    return total_seconds

@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, member: discord.Member, duration: str, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not muted_role:
        muted_role = await ctx.guild.create_role(name="Muted")
        for channel in ctx.guild.channels:
            await channel.set_permissions(muted_role, send_messages=False)

    seconds = parse_duration(duration)
    if seconds is None:
        await ctx.send("Invalid duration format. Use the format: `[months]m [days]d [hours]h [minutes]m [seconds]s`")
        return

    await member.add_roles(muted_role, reason=reason)
    await ctx.send(f"{member.mention} has been muted for {duration}. Reason: {reason}")

    await asyncio.sleep(seconds)

    await member.remove_roles(muted_role)
    await ctx.send(f"{member.mention} has been unmuted.")

@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, member: discord.Member, *, reason=None):
    muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if muted_role in member.roles:
        await member.remove_roles(muted_role, reason=reason)
        await ctx.send(f"{member.mention} has been manually unmuted. Reason: {reason}")
    else:
        await ctx.send(f"{member.mention} is not muted.")

@bot.command()
async def lockdown(ctx):
    if ctx.channel.overwrites_for(ctx.guild.default_role).send_messages == False:
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=None)
        await ctx.send(f"{ctx.channel.mention} has been unlocked")
        return
    else: 
        await ctx.channel.set_permissions(ctx.guild.default_role, send_messages=False)
        await ctx.send(f"{ctx.channel.mention} has been locked down")

@softban.error
async def softban_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a member to softban")
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send("You do not have permission to do that")

@bot.command() 
async def unban(ctx, *, member):
    banned_users = ctx.guild.bans()
    async for ban_entry in banned_users:
        user = ban_entry.user
        if user.name == member:
            await ctx.guild.unban(user)
            await ctx.send(f"{user.mention} has been unbanned")
            return

# Handles errors
@bot.event 
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send("Command not found")

class MyNewHelp(commands.MinimalHelpCommand):
    async def send_pages(self):
        destination = self.get_destination()
        for page in self.paginator.pages:
            emby = discord.Embed(description=page)
            await destination.send(embed=emby)

bot.help_command = MyNewHelp()

# Economy commands
@bot.command(aliases=["bal"])
async def balance(ctx, member: discord.Member=None):
    if member is None:
        member = ctx.author

    user = c.execute("SELECT * FROM users WHERE user_id = ?", (member.id,)).fetchone()
    balance = user[1]
    await ctx.send(f"{member.mention} has {balance} coins")
 
@bot.command()
@commands.has_permissions(administrator=True)
async def setbal(ctx, member: discord.Member=None, amount: int=0):
    c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (amount, member.id))
    conn.commit()
    await ctx.send(f"{member.mention} now has {amount} coins")

@bot.command(aliases=["cf"])
async def coinflip(ctx, bet: int, choice: str):
    """
    coinflip accepts arguments bet and choice (heads/h or tails/t)
    """
    user = c.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,)).fetchone()
    balance = user[1]

    if balance < bet:
        await ctx.send("You do not have enough coins")
        return

    if bet < 1: 
        raise commands.BadArgument

    if choice.lower() not in ["heads", "tails", "h", "t"]:    
        await ctx.send("Invalid choice. Please choose heads or tails")
        return

    coin = random.choice(["heads", "tails"])
    if choice.lower() == coin or choice.lower() == coin[0]:
        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance + bet, ctx.author.id))
        conn.commit()
        await ctx.send(f"{coin.capitalize()}! You won {bet} coins")
    else:
        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance - bet, ctx.author.id))
        conn.commit()
        await ctx.send(f"{coin.capitalize()}! You lost {bet} coins")

@coinflip.error
async def coinflip_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please specify a bet and choice")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Invalid bet amount")

@bot.command() 
async def slots(ctx, bet: int):
    user = c.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,)).fetchone()
    balance = user[1]

    if balance < bet:
        await ctx.send("You do not have enough coins")
        return

    if bet < 1:
        raise commands.BadArgument

    emojis = ["🍇", "🍊", "🍐", "🍒", "🍋", "🍉"]
    slot1 = random.choice(emojis)
    slot2 = random.choice(emojis)
    slot3 = random.choice(emojis)

    if slot1 == slot2 == slot3:
        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance + bet * 2, ctx.author.id))
        conn.commit()
        await ctx.send(f"{slot1} {slot2} {slot3}! You won {bet * 2} coins")
    elif slot1 == slot2 or slot1 == slot3 or slot2 == slot3:
        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance + bet, ctx.author.id))
        conn.commit()
        await ctx.send(f"{slot1} {slot2} {slot3}! You won {bet} coins")
    else:
        c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance - bet, ctx.author.id))
        conn.commit()
        await ctx.send(f"{slot1} {slot2} {slot3}! You lost {bet} coins")

@bot.command(aliases = ["lb"])
async def leaderboard(ctx):
    # show top 10 users by balance
    users = c.execute("SELECT * FROM users ORDER BY balance DESC limit 10").fetchall()
    embed = discord.Embed(title="Leaderboard", color=discord.Color.gold())
    print(users)
    # returns a list of tuples with (user_id, balance)
    for index, user in enumerate(users):
        member = ctx.guild.get_member(user[0])
        print(member)
        embed.add_field(name=f"{index+1}. {member.name}", value=f"{user[1]} coins", inline=False)
    await ctx.send(embed=embed)

# work command to give user random amount of coins between 50 and 300, with a cooldown of 60 seconds
@bot.command()
@commands.cooldown(1, 60, commands.BucketType.user)
async def work(ctx):
    user = c.execute("SELECT * FROM users WHERE user_id = ?", (ctx.author.id,)).fetchone()
    balance = user[1]

    c.execute("UPDATE users SET balance = ? WHERE user_id = ?", (balance + random.randint(50, 300), ctx.author.id))
    conn.commit()
    await ctx.send(f"You worked hard and earned {random.randint(50, 300)} coins")

load_dotenv()
TOKEN = os.getenv("TOKEN") 
bot.run(TOKEN)
