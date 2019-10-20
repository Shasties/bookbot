# bot.py
import os
import requests
import json
import random

from datetime import datetime
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
token = os.getenv('DISCORD_TOKEN')

bot = commands.Bot(command_prefix='!')

async def send_message(ctx,msg):
    bot_channel = False
    for guild in bot.guilds:
        for channel in guild.channels:
            if channel.name == "bot":
                bot_channel = True
                await channel.send(msg)
    if not bot_channel:
        await ctx.send("There is no bot channel, I am scared")

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command(name='new', help="!new <book> adds a new book to your currently reading")
async def add_book(ctx, title: str):
    title = " ".join(ctx.message.content.split(" ")[1:])
    with open("data.json.txt","r") as f:
        data = json.load(f)
    author = str(ctx.message.author)
    # first time init
    if author not in data.keys():
        data[author] = {}
        data[author]["current_reading"] = {}
        data[author]["completed"] = 0
    # new book
    if title not in data[author]["current_reading"].keys():
        date_time = datetime.now().strftime("%m/%d/%Y, %H:%M:%S")
        data[author]["current_reading"][title] = date_time
        msg = author+" has started reading: "+title
    else:
        msg = "You are already reading "+title+" "+author
    # Update file
    with open("data.json.txt","w") as f:
        json.dump(data,f)
    await send_message(ctx,msg)

@bot.command(name='finished', help="!finished <book> removes a book from your currently reading and increases your count")
async def finished_book(ctx,title:str):
    title = " ".join(ctx.message.content.split(" ")[1:])
    with open("data.json.txt","r") as f:
        data = json.load(f)
    author = str(ctx.message.author)
    # first time init
    if author not in data.keys():
        data[author] = {}
        data[author]["current_reading"] = {}
        data[author]["completed"] = 0
    # not in current reading
    if title not in data[author]["current_reading"].keys():
        msg = "Start reading a book before finishing it "+author+" must"
    else:
        msg = author+" has finished reading: "+title
        del data[author]["current_reading"][title]
        data[author]["completed"] = data[author]["completed"] +1
    # Update file
    with open("data.json.txt","w") as f:
        json.dump(data,f)
    await send_message(ctx,msg)
	
@bot.command(name='count', help="!count <user>#<number> lists how many books a user has completed")
async def count(ctx, user: str):
    with open("data.json.txt","r") as f:
        data = json.load(f)
    matches = []
    if user not in data.keys():
        # Did the author forget to type user # ?
        for u in data.keys():
            if user in u:
                matches.append(u)
        if len(matches) == 0:
            msg = "That user has not read anything."
        else:
            msg = "No user matches that name - did you mean: "+" ".join(matches)
    else:
        msg = user+" has read: "+str(data[user]['completed'])+" books"
    await send_message(ctx,msg)

@bot.command(name='list', help="!list <user>#<number> displays a user's currently reading")
async def list(ctx, user: str):
    with open("data.json.txt","r") as f:
        data = json.load(f)
    matches = []
    if user not in data.keys():
        # Did the author forget to type user # ?
        for u in data.keys():
            if user in u:
                matches.append(u)
        if len(matches) == 0:
            msg = "That user has not read anything."
        else:
            msg = "No user matches that name - did you mean: "+" ".join(matches)
    else:
        msg = user+" has been reading the following: "+" / ".join(data[user]['current_reading'].keys())
    await send_message(ctx,msg)
	
@bot.command(name='listall', help="!listall displays all users currently reading")
async def list_all(ctx):
    with open("data.json.txt","r") as f:
        data = json.load(f)
    big_list = []
    for user in data.keys():
        big_list.append("\n"+user+" has been reading the following:\n "+" \n ".join(data[user]['current_reading'].keys()))
    msg = "".join(big_list)
    await send_message(ctx,msg)
        
@bot.command(name='drop', help="!drop <book> removes a book from your currently reading")
async def drop_book(ctx, title: str):
    title = " ".join(ctx.message.content.split(" ")[1:])
    with open("data.json.txt","r") as f:
        data = json.load(f)
    author = str(ctx.message.author)
    # first time init
    if author not in data.keys():
        data[author] = {}
        data[author]["current_reading"] = {}
        data[author]["completed"] = 0
    # not in current reading
    if title not in data[author]["current_reading"].keys():
        msg = "Start reading a book before dropping it "+author+" must"
    else:
        msg = author+" has dropped: "+title
        del data[author]["current_reading"][title]
    # Update file
    with open("data.json.txt","w") as f:
        json.dump(data,f)
    await send_message(ctx,msg) 

@bot.command(name='prompt', help='!prompt lists a noun, a verb, and an adjective you should use in a short story')
async def prompt(ctx):
    files = ["nouns.txt","adjectives.txt","verbs.txt"]
    words = []
    for f in files:
        with open(f) as word_file:
            words.append(random.choice(word_file.read().split()))
    msg = "Try to write a short story using the following words: "+" ".join(words)
    await send_message(ctx,msg)

@bot.command(name='rec', help="!rec <book> adds a book into the recommendation pool")
async def make_rec(ctx,title: str):
    title = " ".join(ctx.message.content.split(" ")[1:])
    with open("data.json.txt","r") as f:
        data = json.load(f)
    author = str(ctx.message.author)
    # first time init
    if "recommendations" not in data[author].keys():
        data[author]["recommendations"] = []
    if title not in data[author]["recommendations"]:
        data[author]["recommendations"].append(title)
        msg = author+" added: "+title+" to their recommendations"
        with open("data.json.txt","w") as f:
            json.dump(data,f)
    else:
        msg = "You have already recommended that book!"
    await send_message(ctx,msg)

@bot.command(name="delrec", help="!delrec <book> removes a book from your recommendations")
async def del_rec(ctx,title: str):
    title = " ".join(ctx.message.content.split(" ")[1:])
    with open("data.json.txt","r") as f:
        data = json.load(f)
    author = str(ctx.message.author)
    # first time init
    if "recommendations" not in data[author].keys():
        data[author]["recommendations"] = []
    if title not in data[author]["recommendations"]:
        msg = title+" is not currently in your recommendations"    
    else:
        data[author]["recommendations"].remove(title)
        msg = author+" has removed: "+title+" from their recommendations"
        with open("data.json.txt","w") as f:
            json.dump(data,f)
    await send_message(ctx,msg)

@bot.command(name='getrec', help="!getrec displays a random recommended book. If <user> is defined, limits search to that user")
async def get_rec(ctx):
    rUser = None
    rRec = None
    msg = ""
    # if author defined a specific user
    if len(ctx.message.content.split(" ")) > 1:
        rUser = ctx.message.content.split(" ")[1]
    # import data
    with open("data.json.txt","r") as f:
        data = json.load(f)
    # search if user exists
    if rUser and rUser not in data.keys():
        # Did the author forget to type user # ?
        matches = []
        for u in data.keys():
            if rUser in u:
                matches.append(u)
        if len(matches) == 0:
            msg = "That user has not recommended anything."
        else:
            msg = "No user matches that name - did you mean: "+" ".join(matches)
    # display if user has any recs
    elif rUser:
        if "recommendations" not in data[rUser].keys() or len(data[rUser]["recommendations"])==0:
            msg = "That user has not recommended anything"
        else:
            rRec = random.choice(data[rUser]["recommendations"])
            msg = rUser+" has recommended: "+rRec
    # display random rec from random user
    else:
        validUsers = []
        for u in data.keys():
            if "recommendations" in data[u].keys():
                if len(data[u]["recommendations"])>0:
                    validUsers.append(u)
        if len(validUsers) > 0:
            rUser = random.choice(validUsers)
            rRec = random.choice(data[rUser]["recommendations"])
            msg = rUser+" has recommended: "+rRec
        else:
            msg = "No one has any recommendations :("
    await send_message(ctx,msg)

bot.run(token)


