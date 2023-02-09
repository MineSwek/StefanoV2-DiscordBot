import discord
from discord.ext import commands
import yaml

startup_extensions = ["music"]

client = commands.Bot(
    command_prefix='>',
    help_command=None,
    case_insensitive=True
)

with open("tokens.yaml", "r") as stream:
    tokens = yaml.safe_load(stream)

embed = discord.Embed(
    colour=discord.Colour.blue()
)

@client.event
async def on_ready():
    print("Im Ready!")
    for extension in startup_extensions:
        try:
            client.load_extension(extension)
        except Exception as e:
            print(e)


### ----------------------------------- KOMENDY DLA WSZYSTKICH ----------------------------------- ###
@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@client.command()
async def help(ctx):
    global embed
    embed.set_image(url="")
    embed.set_author(name='Aktualne komendy!')

    embed.add_field(name=">help", value="Wyświetla informacje o komendach")
    embed.add_field(name=">ping", value="Pokazuje czas reakcji bota")
    embed.add_field(name=">clear {liczba}", value="Usuwa podaną liczbę wiadomości od dołu (tylko ranga Mems)")
    await ctx.send(f"Cześć! {ctx.message.author.mention} Oto co mogę zrobić dla ciebie: ", embed=embed)


### ---------------------------------------------------------------------------------------------- ###


### ----------------------------------- KOMENDY RANGI ADMIN ----------------------------------- ###
@client.command()
@commands.has_role('ADMIN')
async def clear(ctx, number):
    await ctx.channel.purge(limit=int(number) + 1)


### ------------------------------------------------------------------------------------------ ###


client.run(tokens['token'])