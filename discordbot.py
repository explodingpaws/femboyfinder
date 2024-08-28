import nextcord
import requests
import random
from e621 import E621  # use ver. 0.0.6
from dotenv import load_dotenv
import os

load_dotenv()

api = E621()
session = requests.session()
intents = nextcord.Intents.default()

botMain = nextcord.Client(intents=intents, activity=nextcord.Game(name='find femboys with /find'))

token = os.getenv('botToken')
tags = os.getenv('tagList')

defaultTaglist = [
    "rating:explicit",
    "~femboy",
    "~gay",
    "-shota",
    "-fnaf",
    "-loli",
    "-vore",
    "-fart",
    "-scat",
    "-guro",
    "-diaper",
    "-watersports",
    "-poop",
    "-vomit",
    "-morbidly_obese",
    "-fart",
    "-prolapse",
    "-cub",
    "-gore",
    "-incest",
    "-nazi",
    "-zoophilia"
    "-disembowelment",
    "-young",
    "-feral",
    "-undertale_(series)",
    "-five_nights_at_freddy's",
    "-nintendo",
    "-pokemon",
    "-my_little_pony",
    "-sonic_the_hedgehog_(series)",
    "-buff"
]

# all whitelist/blacklist items must be separated by commas and put into quotation marks
# all filters and tags can be found at the cheatsheet link below
# https://e621.net/help/cheatsheet

@botMain.slash_command(name="find", description="find femboys", dm_permission=True)
async def find(interaction=nextcord.Interaction,
               videos_only: bool = nextcord.SlashOption(description="Require posts to be video", required=False),
               minimum_score: int = nextcord.SlashOption(description="Minimum score value", required=False),
               tags: str = nextcord.SlashOption(description="Custom tags (seperate with commas)", required=False)
               ):
    scoreRequirement = 200  # arbitrarily set this based on a lot of content being more eh as it goes down
    if interaction.guild is None or (interaction.channel and interaction.channel.is_nsfw()):
        if minimum_score is not None:
            scoreRequirement = minimum_score
        scoreString = "score:>=" + str(scoreRequirement)

        tagList = [
            scoreString,
            "order:random"
        ]
        if tags is not None:
            tagsAdded = [
                tags
            ]
            tagList.extend(tagsAdded)
        if videos_only is not None:
            tagsAdded = [
                "video"
            ]
            tagList.extend(tagsAdded)
            # Video only filter (webm, mp4, mov)

        tagList.extend(defaultTaglist)

        postSearch = api.posts.search(tagList, ignore_pagination=True, limit=50)
        # adds the tag lists and searches through api. USE PACKAGE 0.0.6 OF THE API.
        # the other versions are broken for whatever reason.
        # do not post issues regarding that please

        maxPosts = len(postSearch)
        if maxPosts == 0:
            print("no posts found")
            await interaction.response.send_message("no posts found")
        else:
            randomPost = postSearch[random.randrange(0, maxPosts)]
            if videos_only:
                for count in range(maxPosts):
                    if randomPost.file.ext == "webm" or randomPost.file.ext == "mov" or randomPost.file.ext == "mp4":
                        url = "https://e621.net/posts/" + str(randomPost.id)
                        embedLink = "[Link To Video](" + url + ")"
                        await interaction.response.send_message(embedLink)
                        break
                    else:
                        randomPost = postSearch[random.randrange(0, maxPosts)]
                    if count == maxPosts:
                        await interaction.response.send_message("no videos could be found")
                # repeats loop a few times since sometimes people label other file formats as "video"
                # gifs can be posted as regular embeds
            else:
                for count in range(maxPosts):
                    if randomPost.file.ext != "webm" or randomPost.file.ext != "mov" or randomPost.file.ext != "mp4":
                        url = "https://e621.net/posts/" + str(randomPost.id)
                        embedLink = "[Link To Image](" + url + ")"
                        artist = randomPost.tags.artist[0]
                        if randomPost.tags.artist[0] == "conditional_dnp":
                            artist = randomPost.tags.artist[1]
                        embedObj = nextcord.Embed(title="Artist: " + artist,
                                                  description=embedLink + "\n Score of: " + str(randomPost.score.total),
                                                  color=0x00549E)
                        embedObj.set_image(url=randomPost.file.url)
                        embedObj.set_footer(text="Post from e621",
                                            icon_url="https://static.wikia.nocookie.net/logopedia/images/0/0b/Logo_transparent.svg/revision/latest/scale-to-width-down/300?cb=20181119223528g")
                        await interaction.response.send_message(embed=embedObj) # includes a little footer image, artist (if valid) and score
                        break
                    if count == maxPosts:
                        await interaction.response.send_message("no valid images could be found")
                        break
                    randomPost = postSearch[random.randrange(0, maxPosts)]
    else:
        await interaction.response.send_message("not an nsfw channel")


@botMain.event
async def on_ready():
    print(f'Logged in as {botMain.user} (ID: {botMain.user.id})')
    print('------------------------------------------------')
    print("Ready!")
    await botMain.sync_application_commands()
# logs in the bot


botMain.run(token)
