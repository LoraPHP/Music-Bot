#COPYRIGHT Misicu Laura 2021
#!./.venv/bin/python

import discord      # base discord module
import code         # code.interact
import os           # environment variables
import inspect      # call stack inspection
import random       # dumb random number generator

from discord.ext import commands    # Bot class and utils

################################################################################
############################### HELPER FUNCTIONS ###############################
################################################################################

# log_msg - fancy print
#   @msg   : string to print
#   @level : log level from {'debug', 'info', 'warning', 'error'}
def log_msg(msg: str, level: str):
    # user selectable display config (prompt symbol, color)
    dsp_sel = {
        'debug'   : ('\033[34m', '-'),
        'info'    : ('\033[32m', '*'),
        'warning' : ('\033[33m', '?'),
        'error'   : ('\033[31m', '!'),
    }

    # internal ansi codes
    _extra_ansi = {
        'critical' : '\033[35m',
        'bold'     : '\033[1m',
        'unbold'   : '\033[2m',
        'clear'    : '\033[0m',
    }

    # get information about call site
    caller = inspect.stack()[1]

    # input sanity check
    if level not in dsp_sel:
        print('%s%s[@] %s:%d %sBad log level: "%s"%s' % \
            (_extra_ansi['critical'], _extra_ansi['bold'],
             caller.function, caller.lineno,
             _extra_ansi['unbold'], level, _extra_ansi['clear']))
        return

    # print the damn message already
    print('%s%s[%s] %s:%d %s%s%s' % \
        (_extra_ansi['bold'], *dsp_sel[level],
         caller.function, caller.lineno,
         _extra_ansi['unbold'], msg, _extra_ansi['clear']))

################################################################################
############################## BOT IMPLEMENTATION ##############################
################################################################################

# bot instantiation
bot = commands.Bot(command_prefix='!')

# on_ready - called after connection to server is established
@bot.event
async def on_ready():
    log_msg('logged on as <%s>' % bot.user, 'info')

# on_message - called when a new message is posted to the server
#   @msg : discord.message.Message
@bot.event
async def on_message(msg):
    # filter out our own messages
    if msg.author == bot.user:
        return
    
    log_msg('message from <%s>: "%s"' % (msg.author, msg.content), 'debug')

    # overriding the default on_message handler blocks commands from executing
    # manually call the bot's command processor on given message
    await bot.process_commands(msg)

# roll - rng chat command
#   @ctx     : command invocation context
#   @max_val : upper bound for number generation (must be at least 1)
@bot.command(brief='Generate random number between 1 and <arg>')
async def roll(ctx, max_val: int):
    # argument sanity check
    if max_val < 1:
        raise Exception('argument <max_val> must be at least 1')

    await ctx.send(random.randint(1, max_val))

# roll_error - error handler for the <roll> command
#   @ctx     : command that crashed invocation context
#   @error   : ...
@roll.error
async def roll_error(ctx, error):
    await ctx.send(str(error))

#scram = force bot to disconnect from voice channel
@bot.command()
async def scram(ctx):
    await ctx.send("**Bye!**")
    await ctx.voice_client.disconnect()

song_list=['Another_Way_Out.mp3', 'Playground.mp3', 'i_m_not_made_by_design.mp3']

#play = command to play a song from the song list
@bot.command()
async def play(ctx, song):
    channel = ctx.author.voice.channel
    await channel.connect()
    guild = ctx.guild
    voice_client: discord.VoiceClient = discord.utils.get(bot.voice_clients, guild=guild)
    if not voice_client.is_playing():
        if song in song_list:
            voice_client.play(discord.FFmpegPCMAudio(song))
            await ctx.send('**Now playing: **' + song)

#list = lists all the songs that are available
@bot.command()
async def list(ctx):
    await ctx.send("**Take a look at my playlist:**")
    for c in song_list:
        await ctx.send(c)

@bot.event
async def on_voice_state_update(member, before, after):
    voice_state = member.guild.voice_client
    if voice_state is None:
        return 
    if len(voice_state.channel.members) == 1:
        await voice_state.disconnect()
################################################################################
############################# PROGRAM ENTRY POINT ##############################
################################################################################

from dotenv import load_dotenv

load_dotenv()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--token", "-t", help = "Add bot_token")
    args = parser.parse_args
    if args.token:
        Bot_Token = args.task
        bot.run(Bot_Token)
    else:
        # check that token exists in environment
        if 'BOT_TOKEN' not in os.environ:
            log_msg('save your token in the BOT_TOKEN env variable!', 'error')
            exit(-1)
        # launch bot (blocking operation)
        bot.run(os.environ['BOT_TOKEN'])
