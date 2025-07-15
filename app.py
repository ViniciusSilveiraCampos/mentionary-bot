import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()


TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


messages = [
    (
        "system",
        "You are Mentionary, an AI on the discord platform, created to help, play and answer questions from server members.",
    )
]


llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0,
    max_tokens=4 * 1024,
    timeout=None,
    max_retries=2,
)


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        if message.reference:
            try:

                ref_msg = await message.channel.fetch_message(
                    message.reference.message_id
                )
                if ref_msg:
                    mention = (
                        "mention_message",
                        {ref_msg.author.name: ref_msg.content},
                    )
                    messages.append(
                        (
                            "human",
                            f" {mention} \n {message.author.name}:{message.content}",
                        )
                    )

                    response = llm.invoke(messages)

                    print(messages)

            except Exception as e:
                print(e)

        await message.channel.send(response.content)

    await bot.process_commands(message)


bot.run(TOKEN)
