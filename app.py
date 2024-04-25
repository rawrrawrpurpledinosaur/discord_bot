import discord
from discord.ext import commands
import os 
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

@bot.event
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
async def coinflip(ctx, bet: int):
    pass
load_dotenv()
TOKEN = os.getenv("TOKEN") 
bot.run(TOKEN)
