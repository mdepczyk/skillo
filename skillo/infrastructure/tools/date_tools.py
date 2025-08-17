from datetime import datetime

from langchain.tools import tool


@tool
def get_current_date_tool() -> str:
    """Get the current date and year as a string."""
    try:
        now = datetime.now()
        return f"Current date: {now.strftime('%Y-%m-%d')}, Current year: {now.year}"
    except Exception as e:
        return f"Error getting current date: {str(e)}"


@tool
def calculate_years_between_tool(
    start_date: str, end_date: str = "current"
) -> str:
    """Calculate years between two dates."""
    try:
        current_year = datetime.now().year
        current_month = datetime.now().month

        if "." in start_date:
            month, year = start_date.split(".")
            start_year = int(year)
            start_month = int(month)
        elif "-" in start_date:
            year, month = start_date.split("-")[:2]
            start_year = int(year)
            start_month = int(month)
        else:
            start_year = int(start_date)
            start_month = 1

        if end_date.lower() in ["current", "obecnie", "present"]:
            end_year = current_year
            end_month = current_month
        elif "." in end_date:
            month, year = end_date.split(".")
            end_year = int(year)
            end_month = int(month)
        elif "-" in end_date:
            year, month = end_date.split("-")[:2]
            end_year = int(year)
            end_month = int(month)
        else:
            end_year = int(end_date)
            end_month = 12

        years = end_year - start_year
        months = end_month - start_month
        total_years = years + (months / 12.0)

        return f"Years between {start_date} and {end_date}: {total_years:.1f} years"

    except Exception as e:
        return f"Error calculating years: {str(e)}"
