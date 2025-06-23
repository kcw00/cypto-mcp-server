from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from typing import Any
import os
import httpx
import re
from datetime import datetime, timedelta, timezone

# constants
load_dotenv()
YT_KEY = os.getenv("YOUTUBE_API_KEY")
YT_API = "https://www.googleapis.com/youtube/v3"
USER_AGENT = "youtube-coin-app/1.0"

# MCP server instance
mcp = FastMCP("cryptoMCPServer")


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


# parse videos duration string to total seconds
def parse_duration_to_seconds(duration: str) -> int:
    """Parse ISO 8601 duration string (e.g., PT5M10S) to total seconds."""
    match = re.match(r"PT(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?", duration)
    if not match:
        return 0
    hours = int(match.group(1) or 0)
    minutes = int(match.group(2) or 0)
    seconds = int(match.group(3) or 0)
    return hours * 3600 + minutes * 60 + seconds


# to get the videos from the last two weeks
def get_two_weeks_ago_iso() -> str:
    two_weeks_ago = datetime.now(timezone.utc) - timedelta(days=14)
    return two_weeks_ago.isoformat()


@mcp.tool()
async def analyze_coin_videos(symbol: str, max_results: int = 5) -> str:
    """Fetch recent cypto-related YouTube videos.

    Args:
        symbol: Cryptocurrency symbol to search for (e.g., "BTC", "ETH").
        max_results: Number of videos to inspect (default = 5)
    """
    try:
        # search for videos on YouTube
        search = await yt_request(
            "search",
            {
                "q": symbol,
                "type": "video",
                "part": "id",
                "order": "date",
                "maxResults": min(max_results * 4, 50),
                "publishedAfter": get_two_weeks_ago_iso(),
            },
        )

        if not search or not search.get("items"):
            return "No search results."

        video_ids = ",".join(item["id"]["videoId"] for item in search["items"])

        # get statistics & snippet for each video
        details = await yt_request(
            "videos",
            {
                "part": "snippet,statistics,contentDetails",
                "id": video_ids,
            },
        )

        if not details:
            return "Failed to fetch video details. Please check your API key and network connection."

        if "error" in details:
            return f"YouTube API Error: {details.get('error', {}).get('message', 'Unknown error')}"

        if not details or not details.get("items"):
            return "No video details found in the response."

        # filter videos over 5 minutes long and only english language
        filtered_videos = []
        for v in details["items"]:
            duration_str = v["contentDetails"]["duration"]
            duration_secs = parse_duration_to_seconds(duration_str)

            # if less than 5 minutes, skip
            if duration_secs < 300:
                continue

            # if not english language, skip
            lang = v["snippet"].get("defaultAudioLanguage", "")
            if lang and not lang.startswith("en"):
                continue

            # after filtering, add to the list
            filtered_videos.append(v)

        # sort videos by view count
        sorted_videos = sorted(
            filtered_videos,
            key=lambda v: int(v["statistics"].get("viewCount", "0")),
            reverse=True,
        )

        video_data: list[str] = []
        for v in sorted_videos:
            vid = v["id"]
            snip = v["snippet"]
            stats = v["statistics"]
            title = snip["title"]
            channel = snip["channelTitle"]
            views = int(stats.get("viewCount", "0"))
            published = snip["publishedAt"][:10]

            video_data.append(
                f"• **{title}**  \n  Channel: {channel} | "
                f"Views: {views:,} | Date: {published} | "
                f"[Watch here](https://www.youtube.com/watch?v={vid})"
            )

        # create the report
        report = "\n\n".join(video_data)
        return {
            "report": {
                "type": "markdown",
                "content": f"### Recent YouTube Videos for {symbol}\n\n{report}",
            }
        }
    except Exception as e:
        return f"Error fetching data: {str(e)}. Please check your API key and network connection."


# run the MCP server
if __name__ == "__main__":
    mcp.run(transport="stdio")
