from urllib.parse import parse_qs, quote, urlparse


def get_youtube_embed_url(url: str) -> str:
    parsed = urlparse(url)

    hostname = (parsed.hostname or "").lower()

    if hostname in ("youtube.com", "www.youtube.com"):

        if parsed.path == "/watch":
            video_id = parse_qs(parsed.query).get("v", [None])[0]
            if video_id:
                return f"https://www.youtube.com/embed/{video_id}"

        if parsed.path.startswith("/shorts/"):
            video_id = parsed.path.split("/shorts/")[1].split("/")[0]
            return f"https://www.youtube.com/embed/{video_id}"

        if parsed.path.startswith("/embed/"):
            return url

        if parsed.path.startswith("/live/"):
            video_id = parsed.path.split("/live/")[1].split("/")[0]
            return f"https://www.youtube.com/embed/{video_id}"

    elif hostname == "youtu.be":
        video_id = parsed.path.lstrip("/").split("/")[0]
        return f"https://www.youtube.com/embed/{video_id}"

    return url


def get_facebook_embed_url(url: str) -> str:
    parsed = urlparse(url)

    hostname = (parsed.hostname or "").lower()

    if hostname in (
        "facebook.com",
        "www.facebook.com",
        "fb.watch",
    ):

        if parsed.path.startswith("/plugins/video.php"):
            return url

        if hostname == "fb.watch":
            url = f"https://www.facebook.com{parsed.path}"

        encoded = quote(url, safe="")

        return (
            "https://www.facebook.com/plugins/video.php"
            f"?href={encoded}"
            "&show_text=false"
            "&width=1280"
        )

    return url