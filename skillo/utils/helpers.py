def format_score(score: float, as_percentage: bool = True) -> str:
    """
    Format a score for display.

    Args:
        score: Score value (0.0 to 1.0)
        as_percentage: Whether to display as percentage

    Returns:
        Formatted score string
    """
    if as_percentage:
        return f"{score:.1%}"
    return f"{score:.3f}"


def truncate_text(
    text: str, max_length: int = 100, suffix: str = "..."
) -> str:
    """
    Truncate text to specified length.

    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix
