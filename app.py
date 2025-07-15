import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from langchain_core.messages import AIMessage

import agent

load_dotenv()


TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if bot.user in message.mentions:
        if message.reference:
            ref_msg = await message.channel.fetch_message(message.reference.message_id)
            mention = (
                "mention_message",
                {ref_msg.author.name: ref_msg.content},
            )
            messages_to_send = [
                (
                    "human",
                    f" {mention} \n {message.author.name}:{message.content}",
                )
            ]
        else:
            messages_to_send = [("human", f"{message.author.name}: {message.content}")]

        inputs = {"messages": messages_to_send}
        async for event in agent.graph.astream(
            inputs, stream_mode="values", config=agent.config
        ):
            response = event["messages"][-1]
            if response.id in agent.ids:
                continue

            agent.ids.add(response.id)
            match response:
                case AIMessage(content=str() as text) | AIMessage(
                    content=[{"text": text, "type": "text"}, *_]
                ):
                    await message.channel.send(text)
                case _:
                    pass

    await bot.process_commands(message)


bot.run(TOKEN)
