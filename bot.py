import os
from dotenv import load_dotenv
import nextcord
from nextcord.ext import commands
import random
import json

load_dotenv()
BOT_TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_ID = int(os.getenv('GUILD_ID'))

intents = nextcord.Intents.default()
intents.message_content = True
bot = commands.Bot(intents=intents)
WATCHLISTFILENAME = "watchlist.json"
# Called once bot is ready for further action.
@bot.event
async def on_ready():
    print(f'Logged in as {bot.user}')

@bot.slash_command(guild_ids=[GUILD_ID], name="ping", description="pongs the user")
async def ping(interaction: nextcord.Interaction):
    await interaction.response.send_message("Pong!")

@bot.slash_command(guild_ids=[GUILD_ID], name="popcorn", description="scoop some popcorn!")
async def popcorn(interaction: nextcord.Interaction):
    popcorn = random.randint(1, 100)
    kernels = random.randint(0, popcorn)
    response = f"{interaction.user.display_name} scooped {popcorn} bits of popcorn, "
    if kernels == 0:
        response += "and no kernels! :popcorn:"
        if popcorn == 100:
            response += " NOW THAT'S A BUTTERY BUCKET :butter:"
    elif kernels == popcorn:
        response += "but ALL OF THEM ARE JUST KERNELS :skull:"
    else:
        response += f"but {kernels} of them are just kernels!"
    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_see_all", description="see all watchlists")
async def watchlist_see_all(interaction: nextcord.Interaction):

    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    if len(watchlist_data["watchlists"]) == 0: #Respond if there are no watchlists
        response = "You have no watchlists right now, create a watchlist with /watchlist_create and you will see it here!"
    else:
        response = "Here are all of your watchlists!\n\n"
        for watchlist in watchlist_data["watchlists"]: #Print every watchlist
            name = watchlist["name"]
            response += f"{name}\n"
            if len(watchlist["media"]) == 0: #Respond if watchlist has no media
                response += "- There are no items in this watchlist right now\n"
            else:
                for media in watchlist["media"]: #Print every media item
                    response += f"- {media}\n"
            response += "\n\n"

    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_create", description="create a new watchlist")
async def watchlist_create(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    #write in the new watchlist to the json
    watchlist_data["watchlists"].append({'name': watchlist_name, 'media': [], 'participants': []})
    watchlist_file = open(WATCHLISTFILENAME, 'w')
    watchlist_file.write(json.dumps(watchlist_data))
    watchlist_file.close()

    response = f"Created a new watchlist named {watchlist_name}. Add movies and shows to your new watchlist!"
    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_delete", description="delete an existing watchlist")
async def watchlist_delete(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    if len(watchlist_data["watchlists"]) == 0:
        response = f"Watchlist named {watchlist_name} does not exist."
    else:
        found = 0
        for i in range(len(watchlist_data)):
            if watchlist_data["watchlists"][i]["name"] == watchlist_name:
                watchlist_data["watchlists"].pop(i)
                found = 1
                break

        if found:
            watchlist_file = open(WATCHLISTFILENAME, 'w')
            watchlist_file.write(json.dumps(watchlist_data))
            watchlist_file.close()
            response = f"Removed watchlist named {watchlist_name}."
        else: 
            response = f"Watchlist named {watchlist_name} does not exist."
    await interaction.response.send_message(response)

@bot.slash_command(guild_ids=[GUILD_ID],
                   name="watchlist_add",
                   description="add a movie or show to a watchlist")
async def watchlist_add(interaction: nextcord.Interaction, media_name, watchlist_name):
    """
    Adds a movie or show to a specified watchlist.

    Parameters:
    interaction (nextcord.Interaction): The interaction object representing the command invocation.
    media_name (str): The name of the movie or show to be added.
    watchlist_name (str): The name of the watchlist to which the movie or show will be added.

    Returns:
    None
    """
    # Read the JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    # Check if the watchlist exists
    watchlist_exists = False
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            watchlist_exists = True
            # Check if media already exists in watchlist
            if media_name not in watchlist["media"]:
                watchlist["media"].append(media_name)
                response = f"Added *{media_name}* to the **{watchlist_name}** watchlist!"
            else:
                response = f"*{media_name}* is already in the **{watchlist_name}** watchlist!"
            break

    if not watchlist_exists:
        response = f"The **{watchlist_name}** watchlist does not exist! \nYou can create it with `/watchlist_create {watchlist_name}`"

    # Write the updated JSON data
    watchlist_file = open(WATCHLISTFILENAME, 'w')
    watchlist_file.write(json.dumps(watchlist_data))
    watchlist_file.close()

    await interaction.response.send_message(response)
    
@bot.slash_command(guild_ids=[GUILD_ID], name="watchlist_join", description="join an existing watchlist")
async def watchlist_join(interaction: nextcord.Interaction, watchlist_name):
    #read the json to get all watchlist list
    watchlist_file = open(WATCHLISTFILENAME, 'r')
    watchlist_data = json.load(watchlist_file)
    watchlist_file.close()

    #add participant to watchlist
    user_id = interaction.user.id
    found = 0
    for watchlist in watchlist_data["watchlists"]:
        if watchlist["name"] == watchlist_name:
            found = 1
            #check duplication
            if (user_id in watchlist["participants"]):
                response = "You are already in this watchlist."
                break
            else:
                watchlist["participants"].append(user_id)
                #write the change to json
                watchlist_file = open(WATCHLISTFILENAME, 'w')
                watchlist_file.write(json.dumps(watchlist_data))
                watchlist_file.close()
                response = f"You have joined the {watchlist_name} watchlist."
                break

    if not found:
        response = f"Watchlist named {watchlist_name} does not exist"
    await interaction.response.send_message(response)

bot.run(BOT_TOKEN)