import re
import urllib
import urllib.request
import discord
from yt_dlp import YoutubeDL
import os
from discord.ext import commands
import random
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import yaml

with open("tokens.yaml", "r") as stream:
    tokens = yaml.safe_load(stream)

auth_manager = SpotifyClientCredentials(client_id=tokens['spotifyClient'], client_secret=tokens['spotifySecret'])
sp = spotipy.Spotify(auth_manager=auth_manager)
queue = list()
try:
    f = open('idkanalumuzycznego.txt')
    lines = f.readlines()
    kanalmid = lines[0]
    kanalw = int(lines[1])
except Exception as e:
    print(e)

nowplaying = []
voice = None
video_thumbnail = ""
video_title = ""

embed = discord.Embed(
    colour=discord.Colour.blue()
)
YDL_OPTIONS = {
    'format': 'bestaudio/best',
    'outtmpl': 'audioFile.mp3',
}

class MusicCog(commands.Cog):
    def __init__(self, client):
        self.client = client
        client.loop.create_task(self.prepare())

    async def editkolej(self):
        message = ""
        for index, x in enumerate(queue):
            message += f"{index + 1}. {x[1]} \n"
        kanal = await self.client.get_channel(int(kanalmid)).history(limit=2).flatten()
        for index, mess in enumerate(kanal):
            if int(mess.id) == kanalw:
                 await mess.edit(content="**Kolejka: \n**" + message)

    async def editaktu(self):
        global nowplaying
        global queue

        kanal = await self.client.get_channel(int(kanalmid)).history(limit=2).flatten()
        for index, mess in enumerate(kanal):
            if int(mess.id) == kanalw:
                try:
                    url = f"https://img.youtube.com/vi/{nowplaying[2]}/0.jpg"
                    embed.set_image(url=url)
                    embed.set_author(name="Aktualna piosenka: " + str(nowplaying[1]))
                except:
                    embed.set_image(url="")
                    embed.set_author(name="Aktualna piosenka: ")
                try:
                    await mess.edit(embed=embed)
                except:
                    pass

    async def prepare(self):
        await self.client.wait_until_ready()
        try:
            await self.editkolej()
            await self.editaktu()
        except:
            pass

    def nextsong(self, *args):
        global voice
        global nowplaying
        global queue
        global YDL_OPTIONS
        if len(queue) == 0:
            nowplaying = ""
            self.client.loop.create_task(self.editaktu())
        if queue:
            if not voice.is_playing():
                nowplaying = queue[0]
                self.client.loop.create_task(self.editaktu())
                try:
                    os.remove('audioFile.mp3')
                except:
                    pass
                with YoutubeDL(YDL_OPTIONS) as ydl:
                    ydl.download([queue[0][0]])
                    voice.play(discord.FFmpegPCMAudio(source='audioFile.mp3'), after=self.nextsong)
                    voice.is_playing()
                    self.client.loop.create_task(self.editkolej())
                    queue.remove(queue[0])
            else:
                return

    @commands.Cog.listener()
    async def on_message(self, message):
        try:
            if message.channel.id == int(kanalmid) and str(message.author) != "Stefano#5343":
                global voice
                global queue
                global nowplaying
                global loop
                channel = self.client.get_channel(int(kanalmid))
                await channel.purge(limit=1)
                try:
                    if voice.is_connected():
                        pass
                except:
                    guild = message.author.guild
                    VoiceChannel = message.author.voice.channel
                    await VoiceChannel.connect()
                    voice = discord.utils.get(self.client.voice_clients, guild=guild)
                if message.content.lower() == "leave":
                    try:
                        await voice.disconnect()
                        queue = []
                        nowplaying = ""
                        voice = None
                        await self.editkolej()
                        await self.editaktu()
                    except:
                        await channel.send("Nie mogę wyjść z kanału", delete_after=3)

                elif message.content.lower() == "pause":
                    try:
                        await voice.pause()
                    except:
                        await channel.send("Piosenka nie może być zatrzymana", delete_after=3)

                elif message.content.lower() == "resume":
                    try:
                        await voice.resume()
                    except:
                        await channel.send("Piosenka nie może być wznowiona", delete_after=3)

                elif message.content.lower() == "skip":
                    try:
                        await voice.stop()
                    except:
                        pass
                elif message.content[0:6].lower() == "remove":
                   try:
                       queue.remove(queue[int(message.content[7:])-1])
                       await self.editkolej()
                       await self.editaktu()
                   except:
                       await channel.send("Ta pozycja nie może być usunięta", delete_after=3)
                elif message.content.lower() == "shuffle":
                    try:
                        random.shuffle(queue)
                        await self.editkolej()
                    except:
                        await channel.send("Kolejka nie może być pomieszana", delete_after=3)
                elif message.content.lower() == "clear":
                    try:
                        queue = []
                        nowplaying = ""
                        voice = None
                        await self.editkolej()
                        await self.editaktu()
                    except:
                        await channel.send("Nie mozna wyczyscic kolejki", delete_after=3)
                elif message.content[0:4].lower() == "move":
                    try:
                        pos1, pos2 = (int(message.content[5])-1), (int(message.content[7])-1)
                        temp = queue[pos1]
                        queue[pos1] = queue[pos2]
                        queue[pos2] = temp
                        
                        await self.editkolej()
                    except:
                        await channel.send("Nie mozna zamienic piosenek", delete_after=3)
                else:
                    if message.content[0:22] == "https://soundcloud.com":
                        url = message.content
                    else:
                        if message.content[0:30] == "https://open.spotify.com/track":
                            info = sp.track(message.content[31:53])
                            message.content = u' '.join((info['name'], info['artists'][0]['name'])).encode('ascii', 'ignore').decode('ascii')
                        html = urllib.request.urlopen("https://www.youtube.com/results?search_query="+ message.content.replace(" ", "+"))
                        video_ids = re.findall(r"watch\?v=(\S{11})", html.read().decode())
                        url = "https://www.youtube.com/watch?v=" + video_ids[0]

                    with YoutubeDL(YDL_OPTIONS) as ydl:
                        info = ydl.extract_info(url, download=False)
                        video_title = info.get('title', None)
                        video_thumbnail = info.get('id', None)

                    queue.append([str(url), video_title, video_thumbnail])

                    self.nextsong()
                    await self.editkolej()
        except Exception as e:
            print(e)

    @commands.command()
    async def musicsetup(self, ctx):
        global kanalmid
        global kanalw
        if not discord.utils.get(ctx.guild.channels, name="stefano-music"):
            guild = ctx.message.guild
            await guild.create_text_channel('stefano-music')
            channel = discord.utils.get(ctx.guild.channels, name="stefano-music")
            file = open("idkanalumuzycznego.txt", "w")
            file.write(str(channel.id) + "\n")

            kanalmid = channel.id


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
            kanal = self.client.get_channel(int(kanalmid))
            kanal = await kanal.history(limit=2).flatten()
            file.write(str(kanal[0].id) + "\n")
            kanalw = kanal[0].id

        else:
            await ctx.send("Kanał już istnieje!")


def setup(client):
    client.add_cog(MusicCog(client))
