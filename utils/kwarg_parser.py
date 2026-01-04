import ast
from typing import List, Any

def parse_value(kwarg_str: str) -> List[Any] | None:
    kwarg_str = kwarg_str.strip()
    
    # Check for the equals sign first
    if "=" not in kwarg_str:
        print(f"⚠️  Skipping malformed pair: '{kwarg_str}' (missing '=')")
        return None 

    # Split exactly once at the first equals sign
    key, val_str = kwarg_str.split("=", 1)
    
    # Clean up and parse the value
    try:
        value = ast.literal_eval(val_str.strip())
    except (ValueError, SyntaxError):
        value = val_str.strip()
        
    return [key.strip(), value]