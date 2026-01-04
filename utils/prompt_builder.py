from typing import Dict, Any, List, Union, Optional

def format_prompt_section(lead_in: str, value: Union[str, List[str]]) -> str:
    """Formats a prompt section by joining a lead-in with content.

    Args:
        lead_in: Introduction sentence for the section.
        value: Section content, as a string or list of strings.

    Returns:
        A formatted string with the lead-in followed by the content.
    """
    if isinstance(value, list):
        formatted_value = "\n".join(f"- {item}" for item in value)
    else:
        formatted_value = value
    return f"{lead_in}\n{formatted_value}"


def build_prompt(config: Dict[str, Any], context: Optional[List[str]]=None, strategy: Optional[str]=None) -> str:
    prompt_parts = []

    role = config.get("role", "Helpful assistant that answers questions about Aya Healthcare")
    
    prompt_parts.append(f"You are a {role}")

    instructions = config.get('instructions')
    if not instructions:
        raise ValueError("Missing the 'instructions' field, this bot needs direction")
    
    prompt_parts.append(instructions)
    
    if categories := config.get("categories"):
        prompt_parts.append(
            format_prompt_section(
                "Organizational Categories:", categories
            )
        )
    
    if constraints := config.get('constraints'):
        prompt_parts.append(
            format_prompt_section(
                "Output constraints:", constraints
            )
        )
    
    if tools := config.get("tools"):
        prompt_parts.append(
            format_prompt_section(
                "Tools:", tools
            )
        )

    if tone := config.get("tone"):
        prompt_parts.append(
            format_prompt_section(
                "Communication Style:", tone
            )
        )

    if format := config.get("format"):
        prompt_parts.append(
            format_prompt_section(
                "Output Format:", format
            )
        )

    if goal := config.get("goal"):
        prompt_parts.append(f"The goal of this interaction is: {goal}")

    if strategy != None:
        if reasoning_strategy := config.get("reasoning_strategies"):
            prompt_parts.append(reasoning_strategy[strategy])
            
    if context != None:
        context_string = "\n".join(f"-{item}" for item in context)
        prompt_parts.append(
            "Here is additional context to help with your answers\n\n"
            "=== ADDITONAL CONTEXT ===\n"
            f"{context_string}\n"
            "=== END ADDITIONAL CONTEXT ===\n\n"
            "=== PREVIOUS CONVERSATION HISTORY ===\n"
        )

    return "\n\n".join(prompt_parts)