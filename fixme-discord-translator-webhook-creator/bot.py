import discord
from discord.ext import commands
from googletrans import LANGUAGES, Translator

translator = Translator()

bot = commands.Bot(command_prefix='/')

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user} ({bot.user.id})')
    print('------')

@bot.slash_command(name='translate', description='Translate a message')
async def translate(ctx, source_lang: str, target_lang: str, *, message: str):
    try:
        translated = translator.translate(message, src=source_lang, dest=target_lang).text
        await ctx.respond(f'Translation: {translated}')
    except ValueError:
        await ctx.respond('Invalid language code')

@bot.slash_command(name='autotranslate', description='Enable or disable automatic translation')
async def autotranslate(ctx, mode: str, source_lang: str = None, target_lang: str = None):
    if mode == 'on':
        if not source_lang or not target_lang:
            await ctx.respond('Please provide source and target language codes')
        elif source_lang not in LANGUAGES or target_lang not in LANGUAGES:
            await ctx.respond('Invalid language code')
        else:
            bot.auto_translate = True
            bot.source_lang = source_lang
            bot.target_lang = target_lang
            await ctx.respond('Automatic translation enabled')
    elif mode == 'off':
        bot.auto_translate = False
        await ctx.respond('Automatic translation disabled')
    else:
        await ctx.respond('Invalid mode')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.auto_translate and message.guild and message.guild.id in bot.auto_translate_guilds:
        try:
            translated = translator.translate(message.content, src=bot.source_lang, dest=bot.target_lang).text
            await message.channel.create_webhook(name='Translation').send(translated)
            await message.delete()
        except ValueError:
            pass

    await bot.process_commands(message)

@bot.slash_command(name='help', description='List available commands')
async def help(ctx):
    commands = '\n'.join([f'/{command.name} - {command.description}' for command in bot.commands])
    await ctx.respond(f'Available commands:\n{commands}')

bot.run('your_token_here')
