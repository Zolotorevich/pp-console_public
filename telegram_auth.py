from telethon import TelegramClient

# Telegram API keys
api_id = 0000000
api_hash = 'SECRET'
client = TelegramClient('flint', api_id, api_hash)

async def main():
    await client.send_message('@zrdevru', 'Auth success')

with client:
    client.loop.run_until_complete(main())