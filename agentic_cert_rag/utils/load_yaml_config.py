import yaml
from pathlib import Path
from typing import Union, Dict, Any

def load_yaml_config(file_path: Union[str, Path]) -> Dict[str, Any]:
    """Load and parse a YAML configuration file.

    Args:
        file_path: Path to the YAML file.

    Returns:
        Parsed YAML content as a dictionary.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        raise FileNotFoundError(f"YAML config not found as {file_path}")
    
    try:
        with open(file_path, "r", encoding='utf-8') as file:
            return yaml.safe_load(file)
    except yaml.YAMLError as e:
        raise yaml.YAMLError(f"Error parsing YAML file, check the syntax in the file: {e}") from e
    except IOError as e:
        raise IOError(f"Error reading YAML file, try again: {e}") from e
