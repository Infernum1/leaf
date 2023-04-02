def shorten_text(text: str, to: int) -> str:
    if len(text) > to:
            return text[: to - 1] + "..."

    return text