import discord
from discord.ext import commands
from dotenv import load_dotenv
import os
from langchain_core.messages import AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI
import base64
import io

import agent

load_dotenv()


def _get_image_base64(response: AIMessage) -> None:
    image_block = next(
        block
        for block in response.content
        if isinstance(block, dict) and block.get("image_url")
    )
    return image_block["image_url"].get("url").split(",")[-1]


TOKEN = os.getenv("DISCORD_BOT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    print(f"Bot connected as {bot.user}")


@bot.command()
async def create_image(ctx, *prompt):
    message = {
        "role": "user",
        "content": prompt,
    }

    llm_image = ChatGoogleGenerativeAI(
        model="models/gemini-2.0-flash-preview-image-generation"
    )

    response = llm_image.invoke(
        [message],
        generation_config=dict(response_modalities=["TEXT", "IMAGE"]),
    )

    image_base64 = _get_image_base64(response)
    image_data = base64.b64decode(image_base64)
    file = discord.File(fp=io.BytesIO(image_data), filename="icon.png")
    await ctx.channel.send(file=file)


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
