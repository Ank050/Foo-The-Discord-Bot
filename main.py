import asyncio
import random
import discord
import os
import requests
from discord.utils import get
from tinydb import Query, TinyDB
import yt_dlp as youtube_dl
import openai

client = discord.Client(intents=discord.Intents.all())
client.message_content = True
db = TinyDB("points.json")
table = db.table("points_table")
User = Query()
api_key = "APIKEY"
openai.api_key = api_key


def messageSend(prompt):
    messages = [
        {
            "role": "system",
            "content": "You are a dog and act like a dog, dont answer not related questions and answer in 30 words.",
        },
        {"role": "user", "content": prompt},
    ]

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages,
        max_tokens=40,
    )

    return response.choices[0].message["content"]


def download_audio(query):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": "Music/" + query + ".mp3",
        "verbose": True,
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        search_results = ydl.extract_info(f"ytsearch1:{query}", download=False)
        video_title = search_results["entries"][0]["title"]
        video_url = search_results["entries"][0]["webpage_url"]
        ydl.download([video_url])


async def play_lofi_in_loop(message):
    if vc is None:
        await message.channel.send(
            "I am not currently connected to any voice channel Woof"
        )
        return

    voice_channel = get(client.voice_clients, guild=message.guild)
    if not voice_channel:
        await message.channel.send(
            "I am not currently in a voice channel. Use `foo join` to make me join Woof"
        )
        return
    async with message.channel.typing():
        await message.channel.send("Playing **LOFI** in a loop ..... Woof")

    folder_path = "./lofi"
    music_files = [
        os.path.join(folder_path, file)
        for file in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, file))
    ]

    while True:
        for file_name in music_files:
            voice_channel.stop()
            voice_channel.play(discord.FFmpegPCMAudio(file_name))
            while voice_channel.is_playing():
                await asyncio.sleep(1)


@client.event
async def on_ready():
    print("{0.user} is ready!!".format(client))


@client.event
async def on_message(message):
    global vc
    if message.author == client.user:
        return
    if message.content.startswith("foo"):
        if message.content == "foo joke pls":
            async with message.channel.typing():
                limit = 1
                api_url = f"https://api.api-ninjas.com/v1/jokes?limit={limit}"
                response = requests.get(
                    api_url,
                    headers={"X-Api-Key": "hLNwH+ZEK1VLGJLM2s9vlw==PFTXCCCr3nFIgBZt"},
                )
                if response.status_code == requests.codes.ok:
                    data = response.json()
                    joke = data[0]["joke"]
                    await message.channel.send(joke + " Woof")
                else:
                    await message.channel.send(
                        f"Error: {response.status_code} {response.text}"
                    )
                await asyncio.sleep(2)

        elif message.content == "foo fact pls":
            async with message.channel.typing():
                limit = 1
                api_url = "https://api.api-ninjas.com/v1/facts?limit={}".format(limit)
                response = requests.get(
                    api_url,
                    headers={"X-Api-Key": "hLNwH+ZEK1VLGJLM2s9vlw==PFTXCCCr3nFIgBZt"},
                )
                if response.status_code == requests.codes.ok:
                    data = response.json()
                    fact = data[0]["fact"]
                    await message.channel.send(fact + " Woof")
                else:
                    await message.channel.send(
                        f"Error: {response.status_code} {response.text}"
                    )
                await asyncio.sleep(2)

        elif message.content == "foo join":
            connected = message.author.voice
            if not connected:
                await message.channel.send(
                    "You need to be connected in a voice channel to use this command!, Woof"
                )
                return
            vc = await connected.channel.connect()

        elif message.content == "foo leave":
            if vc is None:
                await message.channel.send(
                    "I am not currently connected to any voice channel Woof"
                )
                return
            await vc.disconnect()
            vc = None
            remove_file()

        elif message.content.startswith("foo play lofi"):
            await play_lofi_in_loop(message)

        elif message.content.startswith("foo play"):
            if vc is None:
                await message.channel.send(
                    "I am not currently connected to any voice channel Woof"
                )
                return
            voice_channel = get(client.voice_clients, guild=message.guild)
            if not voice_channel:
                await message.channel.send(
                    "I am not currently in a voice channel. Use `foo join` to make me join Woof"
                )
                return
            async with message.channel.typing():
                command_parts = message.content.split(" ")
                if len(command_parts) < 3:
                    await message.channel.send(
                        "Please provide a valid file name to play Woof"
                    )
                    return
                query = " ".join(command_parts[2:])
                print(query)
                download_audio(query)
                file_name = "Music/" + query + ".mp3"
                if not os.path.isfile(file_name):
                    await message.channel.send("The specified file does not exist Woof")
                    return

                embed = discord.Embed(
                    title="**Doggo Music Player** :musical_note:",
                    description=f"Now playing : **{query}**",
                    color=discord.Color.yellow(),
                )
                await message.channel.send(embed=embed)
                voice_channel.stop()

                def remove_file(error):
                    if os.path.isfile(file_name):
                        print("Removing " + file_name)
                        os.remove(file_name)

                voice_channel.play(discord.FFmpegPCMAudio(file_name), after=remove_file)
                await asyncio.sleep(2)

        elif message.content.startswith("foo pet lb"):
            embed = discord.Embed(
                title="Pet Leaderboard",
                color=discord.Color.red(),
            )
            embed.set_thumbnail(
                url="https://images.freeimages.com/images/large-previews/cd5/baby-dog-1404283.jpg"
            )

            records_sorted = sorted(
                table.all(), key=lambda x: x["Points"], reverse=True
            )
            for record in records_sorted:
                userid = record["userID"]
                user = client.get_user(userid)
                embed.add_field(name=user, value=record["Points"], inline=False)

            await message.channel.send(embed=embed)
            await asyncio.sleep(2)

        elif message.content.startswith("foo pet"):
            userid = message.author.id
            record = table.search(User["userID"] == userid)

            if record:
                current_points = record[0]["Points"]
                np = random.randint(1, 20)
                new_points = current_points + np
                table.update(
                    {"Points": new_points},
                    User["userID"] == userid,
                )
            else:
                table.insert({"userID": userid, "Points": random.randint(1, 20)})

            user = client.get_user(userid)
            embed = discord.Embed(
                title=f"Pet by {user.name}",
                color=discord.Color.yellow(),
            )
            embed.add_field(
                name="Thanks for petting me :)", value=f"You got {np} point :dog:"
            )
            await message.channel.send(embed=embed)
            await asyncio.sleep(2)

        elif message.content == "foo help":
            embed = discord.Embed(
                title="Bot Commands",
                description="Here are the available commands:",
                color=discord.Color.yellow(),
            )

            commands = [
                ("```foo joke pls```", "Get a random joke"),
                ("```foo fact pls```", "Get a random fact"),
                ("```foo join```", "Join the voice channel"),
                ("```foo leave```", "Leave the voice channel"),
                ("```foo play lofi```", "Play LOFI music in a loop"),
                ("```foo play [song name]```", "Play a specified song"),
                ("```foo [your message]```", "Chat with the bot"),
                ("```foo pet lb```", "Show the pet leaderboard"),
                ("```foo pet```", "Pet the bot and earn points"),
            ]

            for command, description in commands:
                embed.add_field(name=command, value=description, inline=False)

            await message.channel.send(embed=embed)

        elif message.content.startswith("foo "):
            async with message.channel.typing():
                command_parts = message.content.split(" ")
                if len(command_parts) < 3:
                    await message.channel.send("Yes? Woof Woof")
                    return
                query = " ".join(command_parts[2:])
                ans = messageSend(query)
                await message.channel.send(ans + " :dog:")
            await asyncio.sleep(2)

        else:
            async with message.channel.typing():
                await message.channel.send("Woof Woof :dog:")
                await asyncio.sleep(1)


async def run_bot():
    try:
        await client.start(
            "TOKEN"
        )
    except KeyboardInterrupt:
        await client.close()


if __name__ == "__main__":
    asyncio.run(run_bot())
