from datetime import datetime

from langchain_core.tools import tool


@tool
async def timestamp_to_iso(timestamp: int):
    "Converter tempo para iso"
    return datetime.fromtimestamp(timestamp / 1000).isoformat()


tools = [timestamp_to_iso]
