### General imports:
from datetime import datetime


def validate_int(value_name: str, value_from: int, value_to: int, indentation_lvl: int = 0) -> tuple:
    indent = "\t" * indentation_lvl
    value_name = value_name.lower()
    while True:
        try:
            value = int(input(f"{indent}Enter {value_name} ({value_from}-{value_to}): "))
            if value >= value_from and value <= value_to:
                return value, False
            else:
                print(f"{value_name.capitalize()} must be between: {value_from}-{value_to}")
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return None, True
        except:
            print(f"{indent}Please enter a number with the {value_name}")


def create_time(indentation_lvl: int = 0) -> tuple:
    current_year = datetime.now().year
    
    # Get year first to validate month/day properly
    year, cancelled = validate_int(value_name="year", value_from=current_year, value_to=current_year + 10, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
        
    month, cancelled = validate_int(value_name="month", value_from=1, value_to=12, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
    
    # Determine max days for the given month/year
    if month in [1, 3, 5, 7, 8, 10, 12]:  # 31-day months
        max_days = 31
    elif month in [4, 6, 9, 11]:  # 30-day months
        max_days = 30
    else:  # February
        # Check for leap year
        if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0):
            max_days = 29
        else:
            max_days = 28
    
    date, cancelled = validate_int(value_name="date of month", value_from=1, value_to=max_days, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
        
    hour, cancelled = validate_int(value_name="hour", value_from=0, value_to=23, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
        
    minutes, cancelled = validate_int(value_name="minutes", value_from=0, value_to=59, indentation_lvl=indentation_lvl)
    if cancelled:
        return None, True
    
    formated_time = f"{year}-{month}-{date} {hour}:{minutes}"
    deadline = datetime.strptime(formated_time, "%Y-%m-%d %H:%M")
    return deadline, False
