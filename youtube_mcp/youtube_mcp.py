from typing import Any
import os
import httpx
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# constants
load_dotenv()
YT_KEY = os.getenv("YOUTUBE_API_KEY")
YT_API = "https://www.googleapis.com/youtube/v3"
USER_AGENT = "youtube-coin-app/1.0"

# MCP server instance
mcp = FastMCP("youtube-bitcoin")


# call YouTube Data API
async def yt_request(endpoint: str, params: dict[str, Any]) -> dict[str, Any] | None:
    params["key"] = YT_KEY
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                f"{YT_API}/{endpoint}", headers=headers, params=params, timeout=20.0
            )
            response.raise_for_status()
            return response.json()
        except Exception:
            return None


@mcp.tool()
async def analyze_bitcoin_videos(max_results: int = 5) -> str:
    """Fetch recent Bitcoin-related YouTube videos.

    Args:
        max_results: Number of videos to inspect (default = 5)
    """
    try:
        # 1. search for Bitcoin videos on YouTube
        search = await yt_request(
            "search",
            {
                "q": "bitcoin",
                "type": "video",
                "part": "id",
                "order": "date",
                "maxResults": max_results,
            },
        )

        if not search or not search.get("items"):
            return "No search results."

        video_ids = ",".join(item["id"]["videoId"] for item in search["items"])

        # 2. get statistics & snippet for each video
        details = await yt_request(
            "videos",
            {
                "part": "snippet,statistics",
                "id": video_ids,
            },
        )

        if not details or not details.get("items"):
            return "No video details."

        lines: list[str] = []
        for v in details["items"]:
            snip = v["snippet"]
            stats = v["statistics"]
            title = snip["title"]
            channel = snip["channelTitle"]
            views = int(stats.get("viewCount", "0"))
            published = snip["publishedAt"][:10]

            lines.append(
                f"• **{title}**  \n  Channel: {channel} | Views: {views:,} | Date: {published}"
            )

        report = "\n\n".join(lines)
        return "**Latest Bitcoin videos on YouTube**\n\n" f"{report}\n\n"
    except Exception as e:
        return f"Error fetching data: {str(e)}. Please check your API key and network connection."


# run the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
