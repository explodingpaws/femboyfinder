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

hardTags = [
    "rating:explicit",
    "-shota",
    "-loli",
    "-vore",
    "-feral",
    "-vomit",
    "-scat",
    "-guro",
    "-diaper",
    "-cub",
    "-zoophilia",
    "-disembowelment",
    "-incest",
    "-fart",
    "-prolapse",
    "-gore"
]

# all whitelist/blacklist items must be separated by commas and put into quotation marks
# all filters and tags can be found at the cheatsheet link below
# https://e621.net/help/cheatsheet

@botMain.event
async def on_ready():
    print(f'Logged in as {botMain.user} (ID: {botMain.user.id})')
    print('------------------------------------------------')
    print("Ready!")


# logs in the bot
@botMain.slash_command(name="find", description="find femboys")
async def find(interaction=nextcord.Interaction,
               sexualpreference: int = nextcord.SlashOption(description="Sexual Preference (defaults to any)",
                                                            required=False, choices={"Gay" : 1,
                                                                                     "Straight" : 2,
                                                                                     "Lesbian" : 3,
                                                                                     "Futa" : 4,
                                                                                     }),
               videoonly: bool = nextcord.SlashOption(description="Require posts to be video", required=False),
               minscore: int = nextcord.SlashOption(description="Minimum score value", required=False),
               extratags: str = nextcord.SlashOption(description="Custom tags (seperate with commas)", required=False)
               ):
    scoreRequirement = 40  # arbitrarily set this based on a lot of content being more eh as it goes down

    scoreString = "score:>=" + str(scoreRequirement)

    tagList = [
        scoreString,
        "order:random"
    ]

    if interaction.channel.is_nsfw():
        if minscore is not None:
            scoreRequirement = minscore

        if sexualpreference == 1:
            tagsAdded = [
                "gay"
            ]
            tagList.extend(tagsAdded)
        elif sexualpreference == 2:
            tagsAdded = [
                "straight"
            ]
            tagList.extend(tagsAdded)
        elif sexualpreference == 3:
            tagsAdded = [
                "Lesbian"
            ]
            tagList.extend(tagsAdded)
        elif sexualpreference == 4:
            tagsAdded = [
                "Futa"
            ]
            tagList.extend(tagsAdded)

        if extratags is not None:
            tagsAdded = [
                tags
            ]
            tagList.extend(tagsAdded)
            # Additional tags
        if videoonly is not None:
            tagsAdded = [
                "video"
            ]
            tagList.extend(tagsAdded)
            # Video only filter (webm, mp4, mov)

        tagList.extend(hardTags)

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
            if videoonly:
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
                            artist = "n/a"
                        embedObj = nextcord.Embed(title="Artist: " + artist,
                                                  description=embedLink + "\n Score of: " + str(randomPost.score.total),
                                                  color=0x00549E)
                        embedObj.set_image(url=randomPost.file.url)
                        embedObj.set_footer(text="Post from e621",
                                            icon_url="https://static.wikia.nocookie.net/logopedia/images/0/0b/Logo_transparent.svg/revision/latest/scale-to-width-down/300?cb=20181119223528g")
                        await interaction.response.send_message(
                            embed=embedObj)  # includes a little footer image, artist (if valid) and score
                        break
                    if count == maxPosts:
                        await interaction.response.send_message("no valid images could be found")
                        break
                    randomPost = postSearch[random.randrange(0, maxPosts)]
                    # Loops through the post search incase no images are found, which it will exit if so


botMain.run(token)
