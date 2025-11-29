def get_integer(prompt: str, min_val: int, max_val: int) -> int:
    """
    Prompt the user for an integer between min_val and max_val (inclusive).

    Re-prompts until a valid integer in range is entered.
    """
    while True:
        try:
            value_str = input(prompt)
            value = int(value_str)
            if value < min_val or value > max_val:
                print(f"Please enter a number between {min_val} and {max_val}.")
                continue
            return value
        except ValueError:
            print("Invalid input. Please enter a whole number.")
