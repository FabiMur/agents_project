from strands import tool


@tool
def get_current_date() -> str:
    """Return the current date in a human-readable format. DD/MM/YYYY."""
    from datetime import datetime

    now = datetime.now()
    return now.strftime("%d/%m/%Y")
