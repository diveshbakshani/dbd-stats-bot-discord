#dbd stats bot discord
import random
#use disnake and steam dead by daylight api
import disnake

#call api and get data
from this import d
import requests
import json
import os
import sqlite3
import datetime

BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")

API_KEY = os.environ.get('STEAM_API_KEY')

#print(API_KEY)

# data = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=381210&key={API_KEY}&steamid={STEAM_ID}").json()

# bloodpoints = data['playerstats']['stats'][0]['value']

#load database
conn = sqlite3.connect('dbd.db')
c = conn.cursor()
print("Opened database successfully")

# #insert test data into database
# c.execute("INSERT INTO DIS_STEAM_CONN (DISCORDID,STEAMID) \
#       VALUES (123456789, 76561198388046956)");

# #select and print data from database
# cursor = c.execute("SELECT DISCORDID, STEAMID from DIS_STEAM_CONN")
# for row in cursor:
#    print("DISCORDID = ", row[0])
#    print("STEAMID = ", row[1], )

# #delete test data from database
# c.execute("DELETE from DIS_STEAM_CONN where DISCORDID=123456789;")
# conn.commit()
# print("Total number of rows deleted :", conn.total_changes)


from pathlib import Path
from urllib.parse import urlparse, unquote

#steamurl to steam name
def steamurltosteamname(steamurl):
    steamurl = steamurl.rstrip('/')
    # print(steamurl)
    steamname = steamurl.split('/')[-1]
    return steamname

#numtorank
def numtorank(number):
    if number == 4:
        return 1
    elif number == 3:
        return 2
    elif number == 2:
        return 3
    else:
        return 4


#calculate rank
def rankcalc(rawrank):

    if rawrank >= 6+24+40:
        color = 0xff1000
        rank = "Iridescent"
        number = int((rawrank-70)/4)
        number = numtorank(number)
    
    elif rawrank >= 6+24+20:
        color = 0xffe310
        rank = "Gold"
        number = int((rawrank-50)/4)
        number = numtorank(number)

    elif rawrank >= 6+24+0:
        color = 0xe9f5ff
        rank = "Silver"
        number = int((rawrank-30)/4)
        number = numtorank(number)
    
    elif rawrank >= 6+8+0:
        color = 0xcd7f32
        rank = "Bronze"
        number = int((rawrank-14)/4)
        number = numtorank(number)

    else:
        color = 0xabb8c3
        rank = "Ash"
        number = int(rawrank/4)
        number = numtorank(number)
    
    return rank, number, color





from disnake.ext import commands

description = """An example bot to showcase the disnake.ext.commands extension
module.
There are a number of utility commands being showcased here."""

intents = disnake.Intents.default()
intents.members = True
intents.message_content = True

bot = commands.Bot(
    command_prefix=commands.when_mentioned_or("/"), description=description, intents=intents, test_guilds=[1010174014582435870, 727807488002621470]
)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user} (ID: {bot.user.id})")
    print("------")


# @bot.command()
# async def add(ctx, left: int, right: int):
#     """Adds two numbers together."""
#     await ctx.send(left + right)


# @bot.command()
# async def roll(ctx, dice: str):
#     """Rolls a dice in NdN format."""
#     try:
#         rolls, limit = map(int, dice.split("d"))
#     except Exception:
#         await ctx.send("Format has to be in NdN!")
#         return

#     result = ", ".join(str(random.randint(1, limit)) for r in range(rolls))
#     await ctx.send(result)


# @bot.command(description="For when you wanna settle the score some other way")
# async def choose(ctx, *choices: str):
#     """Chooses between multiple choices."""
#     await ctx.send(random.choice(choices))


# @bot.command()
# async def repeat(ctx, times: int, content="repeating..."):
#     """Repeats a message multiple times."""
#     for i in range(times):
#         await ctx.send(content)


# @bot.command()
# async def joined(ctx, member: disnake.Member):
#     """Says when a member joined."""
#     await ctx.send(f"{member.name} joined in {member.joined_at}")

@bot.command()
async def returnid(ctx, user: disnake.User = None):
    """Returns user id."""
    if user is None:
        await ctx.send(f"{ctx.author.id}")
    else:
        await ctx.send(f"{user.id}")

@bot.slash_command()
async def register(ctx, steamurl: str):
    """ Registers a steamid to a discordid and name and stores in database"""

    if steamurl != None:
        #get discordid
        discordid = ctx.author.id
        #get username
        username = ctx.author.name
        # print(username)
        # print(discordid)
        #get steamid

        # if steamurl has full url:
        if steamurl.startswith("https://steamcommunity.com"):
            steamurl = steamurltosteamname(steamurl)

        # print(steamurl)
        steamid = requests.get(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={steamurl}").json()
        steamid = steamid['response']['steamid']
        # print(steamid)
        #steamid to int
        steamid = int(steamid)

        #insert discordid, steamid, username into database
        c.execute("INSERT INTO DIS_STEAM_CONN (DISCORDID,STEAMID,USERNAME) \
            VALUES (?,?,?)", (discordid, steamid, username));
        conn.commit()
        print("Total number of rows inserted :", conn.total_changes)

        #mention user and tell them they are registered
        await ctx.send(f"Registered {ctx.author.mention} with steamid {steamid} and discordid {discordid}")

    else:
        await ctx.send(f"Please enter a steam url")


@bot.command()
async def gens_completed(ctx):
    """Returns gens completed for a user"""
    #get discordid
    discordid = ctx.author.id
    #get steamid from database
    cursor = c.execute("SELECT STEAMID from DIS_STEAM_CONN where DISCORDID=?", (discordid,))
    for row in cursor:
        steamid = row[0]
    #get data from api
    data = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=381210&key={API_KEY}&steamid={steamid}").json()
    #get gens completed
    gens_completed = data['playerstats']['stats'][0]['value']
    #mention user and tell them how many gens they have completed
    await ctx.send(f"{ctx.author.mention} has completed {gens_completed} gens")



#get dbd grade
@bot.slash_command(name = "rank", description = "Returns dbd rank for a user")
async def rank(ctx, steamurl: str = None):
    """Returns dbd grade for a user"""
    if steamurl == None:
        #get discordid
        discordid = ctx.author.id
        #get steamid from database
        cursor = c.execute("SELECT STEAMID from DIS_STEAM_CONN where DISCORDID=?", (discordid,))
        for row in cursor:
            steamid = row[0]
    else:
        #convert steamurl to steamname
        print(steamurl)
        if steamurl.startswith("https://steamcommunity.com"):
            steamurl = steamurltosteamname(steamurl)
        
        # print(steamurl)
        #get steamid
        steamid = requests.get(f"http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/?key={API_KEY}&vanityurl={steamurl}").json()
        steamid = steamid['response']['steamid']
        # print(steamid)
        #steamid to int
        steamid = int(steamid)

    #get data from api
    data = requests.get(f"http://api.steampowered.com/ISteamUserStats/GetUserStatsForGame/v0002/?appid=381210&key={API_KEY}&steamid={steamid}").json()
    # #get survrank = 
    # survrank = data['playerstats']['stats'][1]['value']
    # survrank = rankcalc(survrank)
    # survcolor = survrank[2]
    # survrank = survrank[0] + " " + str(survrank[1])
    # #get killer rank
    # killerrank = data['playerstats']['stats'][0]['value']
    # killerrank = rankcalc(killerrank)
    # killercolor = killerrank[2]
    # killerrank = killerrank[0] + " " + str(killerrank[1])
    # kills = data['playerstats']['stats'][2]['value']
    # sacrifices = data['playerstats']['stats'][3]['value']
    # total_pips = data['playerstats']['stats'][37]['value']
    # highest_prestige = data['playerstats']['stats'][17]['value']
    # surv_full_games = data['playerstats']['stats'][31]['value']
    # killer_full_games = data['playerstats']['stats'][32]['value']
    # total_bp_spent = data['playerstats']['stats'][14]['value']
    # perfect_surv_games = data['playerstats']['stats'][15]['value']
    # perfect_killer_games = data['playerstats']['stats'][16]['value']
    # bp_on_one = data['playerstats']['stats'][29]['value']

    # loop through all stats to identify and add to embed

    # get number of hours played
    hours_played = 0
    prof_data = requests.get(f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/?key={API_KEY}&steamid={steamid}&format=json").json()
    for game in prof_data['response']['games']:
        if game['appid'] == 381210:
            hours_played = game['playtime_forever']
            hours_played = hours_played / 60
            hours_played = round(hours_played, 2)
            break
    
    #initialize all variables to 0 
    survrank = 0
    killerrank = 0
    kills = 0
    sacrifices = 0
    total_pips = 0
    highest_prestige = 0
    surv_full_games = 0
    killer_full_games = 0
    total_bp_spent = 0
    perfect_surv_games = 0
    perfect_killer_games = 0
    bp_on_one = 0
    

    for i in range(len(data['playerstats']['stats'])):
        if data['playerstats']['stats'][i]['name'] == "DBD_CamperSkulls":
            survrank = data['playerstats']['stats'][i]['value']
            survrank = rankcalc(survrank)
            survcolor = survrank[2]
            survrank = survrank[0] + " " + str(survrank[1])
        elif data['playerstats']['stats'][i]['name'] == "DBD_KillerSkulls":
            killerrank = data['playerstats']['stats'][i]['value']
            killerrank = rankcalc(killerrank)
            killercolor = killerrank[2]
            killerrank = killerrank[0] + " " + str(killerrank[1])
        elif data['playerstats']['stats'][i]['name'] == "DBD_KilledCampers":
            kills = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_SacrificedCampers":
            sacrifices = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_UnlockRanking":
            total_pips = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_BloodwebMaxPrestigeLevel":
            highest_prestige = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_CamperFullLoadout":
            surv_full_games = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_SlasherFullLoadout":
            killer_full_games = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_BloodwebPoints":
            total_bp_spent = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_CamperMaxScoreByCategory":
            perfect_surv_games = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_SlasherMaxScoreByCategory":
            perfect_killer_games = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_MaxBloodwebPointsOneCategory":
            bp_on_one = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_GeneratorPct_float":
            gens_completed = data['playerstats']['stats'][i]['value']
            gens_completed = round(gens_completed, 2)
        elif data['playerstats']['stats'][i]['name'] == "DBD_HealPct_float":
            heals = data['playerstats']['stats'][i]['value']
            heals = round(heals, 2)
        elif data['playerstats']['stats'][i]['name'] == "DBD_UnhookOrHeal":
            unhook = data['playerstats']['stats'][i]['value']
        elif data['playerstats']['stats'][i]['name'] == "DBD_UnhookOrHeal_PostExit":
            unhook_endgame = data['playerstats']['stats'][i]['value']
        

    total_unhooks = unhook + unhook_endgame
        
    
    steamdata = requests.get(f"http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/?key={API_KEY}&steamids={steamid}").json()
    personaname = steamdata['response']['players'][0]['personaname']
    avatar = steamdata['response']['players'][0]['avatarfull']
    # print(avatar)


    embed = disnake.Embed(
        title = "Ranks: " + survrank + " | " + killerrank,
        description = "Playtime: " + str(hours_played) + " hours",
        color = survcolor,
        timestamp = datetime.datetime.utcnow(),
    )

    embed.set_author(name=personaname, icon_url=avatar)

    embed.add_field(name="5K Surv Games", value=perfect_surv_games, inline=True)
    embed.add_field(name="Survivor Games", value=surv_full_games, inline=True)
    embed.add_field(name="WinRate", value=round(perfect_surv_games/surv_full_games, 2) if surv_full_games!=0 else 0, inline=True)
    

    embed.add_field(name="5K Killer Games", value=perfect_killer_games, inline=True)
    embed.add_field(name="Killer Games", value=killer_full_games, inline=True)
    embed.add_field(name="WinRate", value=round(perfect_killer_games/killer_full_games, 2) if killer_full_games!=0 else 0, inline=True)

    embed.add_field(name="Total Piss", value=total_pips, inline=True)
    embed.add_field(name="Highest Pisstige", value=highest_prestige, inline=True)
    embed.add_field(name="GenRush", value=round(gens_completed/surv_full_games, 2) if surv_full_games!=0 else 0, inline=True)

    embed.add_field(name="Altruist", value=round(heals/surv_full_games, 2) if surv_full_games!=0 else 0, inline=True)
    embed.add_field(name="Unhooker", value=round(total_unhooks/surv_full_games, 2) if surv_full_games!=0 else 0, inline=True)
    embed.add_field(name="SpendRate\\hr", value=f"{round(total_bp_spent/hours_played, 2) if hours_played!=0 else 0:,}", inline=True)

    # embed.add_field(name="Total Sacrifices", value=sacrifices, inline=True)
    # embed.add_field(name="Total Kills", value=kills, inline=True)

    # embed.add_field(name="Total BP Spent", value=f"{total_bp_spent:,}", inline=True)
    # embed.add_field(name="Max BP on One Surv", value=f"{bp_on_one:,}", inline=True)
    
    await ctx.send(embed=embed)


    #invoke message command




@bot.group()
async def cool(ctx):
    """Says if a user is cool.
    In reality this just checks if a subcommand is being invoked.
    """
    if ctx.invoked_subcommand is None:
        await ctx.send(f"No, {ctx.subcommand_passed} is not cool")


@cool.command(name="bot")
async def bot_(ctx):
    """Is the bot cool?"""
    await ctx.send("Yes, the bot is cool.")


bot.run(BOT_TOKEN)