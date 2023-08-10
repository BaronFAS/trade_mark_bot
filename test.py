# import asyncio
# from telegram import Bot

# bot = Bot(token='6428760828:AAHVSAROod1W0TwiQxHqCeexd6bhmEYjBPE')
# chat_id = '234783286'
# text = 'Hello, World!'


# async def send_message():
#     await bot.send_message(chat_id, text)

# asyncio.run(send_message())


from telegram import Bot

# Здесь укажите токен,
# который вы получили от @Botfather при создании бот-аккаунта
bot = Bot(token='6428760828:AAHVSAROod1W0TwiQxHqCeexd6bhmEYjBPE')
# Укажите id своего аккаунта в Telegram
chat_id = '234783286'
text = 'Вам телеграмма!'
# Отправка сообщения
bot.send_message(chat_id, text)
