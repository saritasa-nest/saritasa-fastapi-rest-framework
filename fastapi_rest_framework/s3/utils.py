import urllib.parse


def extract_key_from_url(url: str, bucket: str) -> str:
    """Extract key for s3 url."""
    return (
        urllib.parse.urlparse(
            url=urllib.parse.unquote_plus(url),
        )
        .path.replace(
            f"/{bucket}/",
            "",
            1,
        )
        .lstrip("/")
    )
