import discord
from discord.ext import commands
import os 
import asyncio
import re 
import sqlite3 
import random
from py import capy
from dotenv import load_dotenv

conn = sqlite3.connect("database.db")
c = conn.cursor()

intents = discord.Intents.all()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="capy ", intents=intents)
guild_ids = []

@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    print(capy)
    await bot.change_presence(activity=discord.Game(name="capy help"))
    # check if guild.id is in database, else add to db
    for guild in bot.guilds:
        exisiting_guild_ids = c.execute("SELECT guild_id FROM guilds").fetchall()
        exisiting_guild_ids = [x[0] for x in exisiting_guild_ids]
        if guild.id not in exisiting_guild_ids:
            print(f"adding {guild.id} to database") 
            c.execute("INSERT INTO guilds (guild_id) VALUES (?)", (guild.id,))
            conn.commit()

bot.event
async def on_member_join(member): 
    print(f"{member} joined {member.guild}")
    await member.send(f"Welcome to {member.guild}!")

@bot.slash_command(guild_ids = [1080649131057483858])
async def hello(ctx):
    await ctx.send("Hello!")

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

# Gambling commands
@bot.command()
async def coinflip(ctx):
    result = random.choice(["Heads", "Tails"])
    await ctx.send(result)

load_dotenv()
TOKEN = os.getenv("TOKEN") 
bot.run(TOKEN)
