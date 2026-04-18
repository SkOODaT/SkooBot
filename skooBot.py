import discord
from discord.ext import commands
import typing
from datetime import datetime
import logging

import configparser
config = configparser.ConfigParser()
config.read('config.ini')

logging.basicConfig(
    format = f'[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] %(message)s',
    level = logging.INFO
)
console_info = False

# Intents are required to tell Discord what events your bot wants to receive.
intents = discord.Intents.default()
# Allows the bot to read message content.
intents.message_content = True
# because were not running cogs need this to name help category.
help_command = commands.DefaultHelpCommand(no_category='General Commands')
# The command_prefix defines what character triggers a command. (e.g., !ping)
bot = commands.Bot(command_prefix='!', intents=intents, help_command=help_command)

import os
import sys
import glob
from pathlib import Path

from pythonnet import load
load('coreclr')

import clr
from System import Array, Byte, Memory

os.path.abspath('PKHeX.Core.dll')
clr.AddReference('PKHeX.Core')

from PKHeX.Core import (
    PKM,
    PK7,
    PB7,
    PK8,
    PA8,
    PB8,
    PK9,
    PA9,
    Gender,
    Ball,
    Ability,
    Nature,
    Species,
    Move,
    MoveType,
    LanguageID,
    SaveFile,
    LegalityAnalysis
)

targets = [
    'pk7',
    'pb7',
    'pk8',
    'pa8',
    'pb8',
    'pk9'
]


@bot.event
async def on_ready():
    logging.info(f'Logged in as {bot.user} (ID: {bot.user.id})')
    print('------------------')

@bot.command(help='Just upload a file.', brief='How to use bot.')
@commands.has_role(int(config['Discord']['role_id']))
async def start(ctx):
    await ctx.send('Start by uploading a PKHeX pokemon file, Supported generations are all of 7/8/9.')

@bot.listen()
async def on_message(message):
    # Ignore messages sent by the bot itself
    if message.author == bot.user:
        return
    # Only listen to the specific channel and ignore other bots
    if message.channel.id != int(config['Discord']['channel_id']) or message.author.bot:
        return
    if not message.author.get_role(int(config['Discord']['role_id'])):
        return
    # Ensure the target directory exists
    save_path = 'downloads'
    if not os.path.exists(save_path):
        os.makedirs(save_path)
        
    # Check if the message has any attachments
    if message.attachments:
        for attachment in message.attachments:
            # Define the full path including the original filename
            file_destination = os.path.join(save_path, attachment.filename)
            # Save the file using its original filename
            await attachment.save(file_destination)
            logging.info(f'Saved: {attachment.filename} to {save_path}')
            await message.channel.send(f'Successfully Received: {attachment.filename}.')
            
            loadfile = attachment.filename
            ctarget = str
            for t in targets:
                index = loadfile.find(t)
                if index != -1:
                    ctarget = t

            pk = load_pk(ctarget, file_destination)
            summary = summarise_pk(ctarget, pk)
            legality = check_legality(pk)

            await discord_alert_pokemon(loadfile, summary, legality, message)

            if legality['valid']:
                await message.channel.send(':white_check_mark: Pokemon is **LEGAL**')
            else:
                await message.channel.send(':x: Pokemon is **ILLEGAL**')

@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        await ctx.send('Command not found.')
    elif isinstance(error, commands.MissingPermissions):
        await ctx.send('You lack permissions to run this.')
    else:
        await ctx.send(f'{error}')
        logging.info(f'Unhandled error: {error}')

async def discord_alert_pokemon(loadfile: str, summary: dict, legality: dict, message: str):
    # 1. Set the initial embed
    discord_colour = discord.Color.green()
    s = summary
    iv = s['ivs'];  ev = s['evs']
    status = '✅ LEGAL' if legality['valid'] else '❌ ILLEGAL'
    string = (
        f'{status}  {loadfile}\n'
        f'Nickname  : {s['nickname']}\n'
        f'OT        : {s['ot']}  TID={s['tid']}  SID={s['sid']}\n'
        f'HT        : {s['ht']}\n'
        f'Nature    : {s['nature']}\n'
        f'Ability   : {s['ability']}\n'
        f'Ball      : {s['ball']} Ball  Held: {s['held_item']}\n'
        f'Met       : Lv.{s['met_level']} @ {s['met_location']}\n'
        f'IVs       : HP={iv['HP']:2} Atk={iv['Atk']:2} Def={iv['Def']:2}'
        f'SpA={iv['SpA']:2} SpD={iv['SpD']:2} Spe={iv['Spe']:2}\n'
        f'EVs       : HP={ev['HP']:3} Atk={ev['Atk']:3} Def={ev['Def']:3}'
        f'SpA={ev['SpA']:3} SpD={ev['SpD']:3} Spe={ev['Spe']:3}\n'
        f'Moves     : {' / '.join(m for m in s['moves'] if m)}\n'
        f'Pokerus   : State {s['pokerus_state']} Days {s['pokerus_days']} Strain {s['pokerus_strain']}' 
    )

    if not legality['valid']:
        flag = False
        info = ''
        for ident, Valid, judgement, Result in legality['checks']:
            if judgement != 'Valid':
                flag = True
                info += f'[{ident}] {judgement} {Result}\n'
        if flag == True:
            console_output(f'\n⚠ Legality issues: {loadfile}')
            console_output(info)
            string += (
                f'\n\n:warning: **Legality Issues:**'
                #f'\nLegality  : {legality['valid']}'
                f'\n{info}'
            )
            discord_colour = discord.Color.red()    

    embed = discord.Embed(
        title = f'\n  :parking:  **Pokemon Summery:** {loadfile}',
        description = string,
        color = discord_colour
    )
    # 2. Add content fields
    #embed.add_field(name = 'Member Count', value=message.guild.member_count, inline=True)
    #embed.add_field(name = 'Owner', value=message.guild.owner, inline=True)
    image_url = config['Discord']['pokemon_image_url'] + f'{summary['species']}' + config['Discord']['pokemon_image_type']
    # 3. Set visual elements
    embed.set_footer(text = 'Requested by ' + message.author.name)
    embed.set_thumbnail(url = image_url if image_url else None)
    await message.channel.send(embed=embed)


def load_pk(ctarget: str, path: str) -> PKM:
    '''Load a .pk9 file into a PKHeX PK9 object.'''
    data = Path(path).read_bytes()
    byte_array = bytearray(data)
    net_array = Array[Byte](byte_array)
    dotnet_memory = Memory[Byte](net_array)
            
    pk = str
    if ctarget == 'pk7':
        pk = PK7(dotnet_memory)
    elif ctarget == 'pb7':
        pk = PB7(dotnet_memory)
    elif ctarget == 'pk8':
        pk = PK8(dotnet_memory)
    elif ctarget == 'pa8':
        pk = PA8(dotnet_memory)
    elif ctarget == 'pb8':
        pk = PB8(dotnet_memory)
    elif ctarget == 'pk9':
        pk = PK9(dotnet_memory)
 
    return pk

def check_legality(pk: PKM) -> dict:
    '''Run PKHeX legality analysis and return a summary dict.'''
    la = LegalityAnalysis(pk)
    #report = la.Report(verbose=True)   # full human-readable report
    return {
        'valid':   la.Valid,
        'report':  str(la.Parsed),
        'checks':  [(str(list.Identifier), list.Valid, str(list.Judgement), str(list.Result))
                    for list in la.Results],
    }

def summarise_pk(ctarget: str, pk: PKM) -> dict:
    '''Extract key fields from a PKM object.'''
    return {
        'species':       int(pk.Species),
        'species_name':  str(Species(int(pk.Species))),         # e.g. 'Charizard'
        'nickname':      str(pk.Nickname),
        'level':         int(pk.CurrentLevel),
        'pid':           f'{int(pk.PID):#010x}',
        'tid':           int(pk.TID16),
        'sid':           int(pk.SID16),
        'ot':            str(pk.OriginalTrainerName),
        'ht':            str(pk.HandlingTrainerName),
        #'hid':           int(pk.HandlingTrainerID),
        'gender':        int(pk.Gender),               # 0=M 1=F 2=Unknown
        'nature':        str(pk.Nature),               # e.g. 'Timid'
        'stat_nature':   str(pk.StatNature),           # after mints
        'ability':       str(Ability(int(pk.Ability))),
        #'tera_type':     str(pk.TeraType),             # SV-exclusive
        #'tera_orig':     str(pk.TeraTypeOriginal),
        'held_item':     str(pk.HeldItem),       # item name
        'ball':          str(Ball(int(pk.Ball))),
        'met_level':     int(pk.MetLevel),
        'met_location':  str(pk.MetLocation),         # location name
        'is_egg':        bool(pk.IsEgg),
        #'shiny':         bool(pk.IsvShiny),
        #'shiny_type':    'Star' if pk.ShinyXor == 1 else
        #                 'Square' if pk.IsShiny else 'None',
        'ivs': {
            'HP':  int(pk.IV_HP),  'Atk': int(pk.IV_ATK),
            'Def': int(pk.IV_DEF), 'SpA': int(pk.IV_SPA),
            'SpD': int(pk.IV_SPD), 'Spe': int(pk.IV_SPE),
        },
        'evs': {
            'HP':  int(pk.EV_HP),  'Atk': int(pk.EV_ATK),
            'Def': int(pk.EV_DEF), 'SpA': int(pk.EV_SPA),
            'SpD': int(pk.EV_SPD), 'Spe': int(pk.EV_SPE),
        },
        'moves': [
            str(Move(int(pk.Move1))), str(Move(int(pk.Move2))),
            str(Move(int(pk.Move3))), str(Move(int(pk.Move4))),
        ],
        'pokerus_state':  str(pk.PokerusState),
        'pokerus_days':  str(pk.PokerusDays),
        'pokerus_strain':  str(pk.PokerusStrain)
        #'ribbons': int(pk.RibbonCount),
    }

def print_result(ctarget: str, path: str, summary: dict, legality: dict):
    status = '✅ LEGAL' if legality['valid'] else '❌ ILLEGAL'
    print(f'\n{'─'*55}')
    print(f'  {status}  {path}')
    print(f'{'─'*55}')
    s = summary
    #print(f'  Species   : #{s['species']} {s['species_name']}'
         # f'  Lv.{s['level']}  {'★ ' if s['shiny'] else ''}'
         # f'{s['shiny_type']}')
    print(f'  Nickname  : {s['nickname']}')
    print(f'  OT        : {s['ot']}  TID={s['tid']}  SID={s['sid']}')
    print(f'  Nature    : {s['nature']}'
          + (f'  (stat: {s['stat_nature']})' if s['stat_nature'] != s['nature'] else ''))
    print(f'  Ability   : {s['ability']}')
    #print(f'  Tera Type : {s['tera_type']}'
    #      + (f'  (orig: {s['tera_orig']})' if s['tera_orig'] != s['tera_type'] else ''))
    print(f'  Ball      : {s['ball']} Ball  Held: {s['held_item']}')
    print(f'  Met       : Lv.{s['met_level']} @ {s['met_location']}')
    iv = s['ivs'];  ev = s['evs']
    print(f'  IVs       : HP={iv['HP']:2} Atk={iv['Atk']:2} Def={iv['Def']:2}'
          f' SpA={iv['SpA']:2} SpD={iv['SpD']:2} Spe={iv['Spe']:2}')
    print(f'  EVs       : HP={ev['HP']:3} Atk={ev['Atk']:3} Def={ev['Def']:3}'
          f' SpA={ev['SpA']:3} SpD={ev['SpD']:3} Spe={ev['Spe']:3}')
    print(f'  Moves     : {' / '.join(m for m in s['moves'] if m)}')

    flag = False
    info = ''
    for ident, Valid, judgement, Result in legality['checks']:
        if judgement != 'Valid':
            flag = True
            info += f'     [{ident}] {judgement} {Result} \n'
    if flag == True:
        print('\n  ⚠  Legality issues:')
        print(info, end='')

def console_output(output: str):
    if console_info == True:
        try:
            print(output)
        except Exception as e:
            logging.info(f'\n  ERROR {e}') 

bot.run(config['Discord']['token'])