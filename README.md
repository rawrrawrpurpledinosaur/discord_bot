## Discord bot for moderation and fun with currency system (WIP) 
### Features:
- Moderation commands
1. kick
2. ban 
3. softban and delete 100 most recent messages
4. unban 
5. purge - delete messages

- Fun commands
1. coinflip

- Currency system: Uses a sqlite database to store user data and currency.
1. bal/balance - check your balance
2. daily - get daily currency
3. transfer - transfer currency to another user
4. leaderboard - check the leaderboard
5. slots - play slots
6. bj/blackjack - play blackjack
7. roulette - play roulette

- Other commands
1. help - list all commands
2. ping - check bot latency
3. stats - get server statistics
4. invite - get bot invite link
5. prefix - change bot prefix

## Installation and use 
```bash 
git clone https://github.com/rawrrawrpurpledinosaur/discord_bot
cd discord_bot
pip install -r requirements.txt
echo "TOKEN = YOUR_BOTS_TOKEN" > .env
python main.py
```
