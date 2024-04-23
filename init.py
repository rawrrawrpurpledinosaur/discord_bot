import sqlite3

conn = sqlite3.connect('database.db')
c = conn.cursor()

# create a table of all the users in one guild and their balance, then a table of all the guilds the bot is in
c.execute('CREATE TABLE IF NOT EXISTS users (user_id INTEGER PRIMARY KEY, balance INTEGER)')
c.execute('CREATE TABLE IF NOT EXISTS guilds (guild_id INTEGER PRIMARY KEY)')
c.execute('CREATE TABLE IF NOT EXISTS guild_users (guild_id INTEGER REFERENCES guilds(guild_id), user_id INTEGER REFERENCES users(user_id), PRIMARY KEY (guild_id, user_id))')

conn.commit()
