import re

def legalize_target_name(target_name: str):
    """
    Function from Michael Knudsen via Philippe Lamy.
    Finds gwf target non-legal characters in target names and return target names legalized.
    """
    # First check if target name is legal.
    if re.match(r"^[a-zA-Z_][a-zA-Z0-9._]*$", target_name):
        return target_name
    
    # Target name is not legal. Replace illegal characters by underscores.
    result = ""

    # First character is special.
    result += target_name[0] if re.match(r"[a-zA-Z_]", target_name[0]) else "_"

    # Check remaining characters.
    for i in range(1, len(target_name)):
        result += target_name[i] if re.match(r"[a-zA-Z0-9._]", target_name[i]) else "_"

    return result
