from strands import tool


@tool
def calculator(expression: str) -> str:
    """Evaluate a mathematical expression and return the result."""
    try:
        allowed_names = {"__builtins__": None}
        result = eval(expression, allowed_names)
        return str(result)
    except Exception as e:
        return f"Evaluation error: {e}"
