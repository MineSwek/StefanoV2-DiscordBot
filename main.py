import discord
from discord.ext import commands
import yaml

intents = discord.Intents.default()
intents.message_content = True

client = commands.Bot(
    intents=intents,
    command_prefix='>',
    help_command=None
)

with open("tokens.yaml", "r") as stream:
    tokens = yaml.safe_load(stream)

embed = discord.Embed(
    colour=discord.Colour.blue()
)

@client.event
async def on_ready():
    try:
        await client.load_extension("music")
    except Exception as e:
        print(e)

    print("Im Ready!")


### ----------------------------------- KOMENDY DLA WSZYSTKICH ----------------------------------- ###
@client.command()
async def ping(ctx):
    await ctx.send(f"Pong! {round(client.latency * 1000)}ms")

@client.command()
async def help(ctx):
    global embed
    embed.set_image(url="")
    embed.set_author(name='Aktualne komendy!')

    embed.add_field(name="/help", value="Wyświetla informacje o komendach")
    embed.add_field(name="/ping", value="Pokazuje czas reakcji bota")
    embed.add_field(name=">clear {liczba}", value="Usuwa podaną liczbę wiadomości od dołu (tylko ranga Mems)")
    await ctx.send(f"Cześć! {ctx.message.author.mention} Oto co mogę zrobić dla ciebie: ", embed=embed)


# ### ---------------------------------------------------------------------------------------------- ###


# ### ----------------------------------- KOMENDY RANGI ADMIN ----------------------------------- ###
@client.command()
@commands.has_role('ADMIN')
async def clear(ctx, number: int):
    await ctx.channel.purge(limit=int(number) + 1)


# ### ------------------------------------------------------------------------------------------ ###

@client.command()
@commands.has_role('ADMIN')
async def musicsetup(ctx):
    global kanalmid
    global kanalw
    if not discord.utils.get(ctx.guild.channels, name="stefano-music"):
        guild = ctx.message.guild
        await guild.create_text_channel('stefano-music')
        channel = discord.utils.get(ctx.guild.channels, name="stefano-music")
        file = open("idkanalumuzycznego.txt", "w")
        file.write(str(channel.id) + "\n")


        embed.set_author(name="Stefano - Komendy do korzystania z bota: ")

        embed.add_field(name="leave", value="Wyjście bota z kanału")
        embed.add_field(name="pause", value="Pauzuje aktualną muzykę")
        embed.add_field(name="resume", value="Wznawia aktualną muzykę")
        embed.add_field(name="skip", value="Pomiją aktualną muzykę")
        embed.add_field(name="remove [id]", value="Pomiją aktualną muzykę")
        embed.add_field(name="shuffle", value="Miesza playliste")
        embed.add_field(name="move [nr] [nr]", value="Zamienia piosenki miejscami")
        embed.add_field(name="Dodawanie piosenek", value="Aby dodać piosenkę do kolejki po prostu wpisz jej nazwę tutaj!", inline=False)
        await channel.send(embed=embed)
        embed.set_author(name="Aktualna piosenka")
        embed.clear_fields()
        embed.set_image(url="")
        await channel.send('**Kolejka:\n**', embed=embed)
        message = await channel.fetch_message(channel.last_message_id)
        file.write(str(message.id))
    else:
        await ctx.send("Kanał już istnieje!")

client.run(tokens['token'])