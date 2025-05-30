import os

import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException
from .terminal_utils import fetch_system_info


def _detect_project_type(cwd: str) -> str:
    """
    Determines the type of project based on specific files found in the given directory. The function inspects
    the contents of the provided directory and categorizes it as a specific project type or as a general
    directory if no specific files are detected.

    Args:
        cwd: The current working directory to inspect. Must be a valid file path.

    Returns:
        A string indicating the type of project detected. Possible values include:
        - "Node.js project detected"
        - "Python project detected"
        - "Rust project detected"
        - "Go project detected"
        - "Git repository detected"
        - "General directory"
    """

    files = os.listdir(cwd) if os.path.exists(cwd) else []

    if "package.json" in files:
        return "Node.js project detected"
    elif "requirements.txt" in files or "pyproject.toml" in files:
        return "Python project detected"
    elif "Cargo.toml" in files:
        return "Rust project detected"
    elif "go.mod" in files:
        return "Go project detected"
    elif ".git" in files:
        return "Git repository detected"
    else:
        return "General directory"


def get_enhanced_system_prompt(system_info: Dict[str, str]) -> str:
    """
    Generates an enhanced system prompt for an interactive Linux terminal AI agent,
    integrating system context and safety guidelines for command execution.

    This function assembles a detailed prompt by incorporating system information such as
    current working directory, operating system, shell, and user. The prompt outlines the
    capabilities, response guidelines, and safety rules the AI agent should adhere to, thereby
    ensuring secure and efficient interaction.

    Args:
        system_info (Dict[str, str]): A dictionary containing system-related keys and values. Expected
            keys include:
                - 'current_dir': The current working directory.
                - 'os': The operating system in use.
                - 'shell': The shell runtime environment.
                - 'user': The user executing the agent, where it defaults to "unknown" if not provided.

    Returns:
        str: The formatted prompt string incorporating system information and operational guidelines.
    """

    base_prompt: str = f"""
        You are an interactive Linux terminal AI agent with direct command execution capabilities.
        
        CURRENT CONTEXT:
        - Working Directory: {system_info['current_dir']}
        - OS: {system_info['os']}
        - Shell: {system_info['shell']}
        - User: {system_info.get('user', 'unknown')}
        
        CAPABILITIES:
        - Execute shell commands safely
        - Analyze file contents and directory structures
        - Provide system administration guidance
        - Assist with development workflows
        - Monitor system resources and processes
        
        RESPONSE GUIDELINES:
        1. Be concise but thorough
        2. Always explain what commands do before suggesting them
        3. For potentially destructive operations, ask for explicit confirmation
        4. Provide alternatives when possible
        5. Use code blocks for commands: ```bash\ncommand here\n```
        
        SAFETY RULES:
        - Never execute commands that could damage the system
        - Always warn about destructive operations (rm -rf, format, etc.)
        - Prefer safer alternatives (mv to trash vs rm, etc.)
        - Ask before modifying system files or configurations
        
        Current project context: {_detect_project_type(system_info['current_dir'])}
    """
    return base_prompt


def fetch_response(query: str, config: Dict[str, Any]) -> str:
    """
    Sends a query to a Groq API and returns the AI's response.

    Args:
        query: The user's query to send to the AI.
        config: A dictionary containing API configuration (key, model, base URL)
                and settings (max_tokens).

    Returns:
        A string containing the AI's response, or an error message if the
        API request fails.
    """
    api_key: str = config["API"]["api_key"]
    model = config["API"]["model"]
    api_base = config["API"].get("api_base", "https://api.groq.com/openai/v1")
    max_tokens: int = int(config["SETTINGS"].get("max_tokens", "2048"))

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": model,
        "messages": [
            {
                "role": "system",
                "content": get_enhanced_system_prompt(fetch_system_info()),
            },
            {"role": "user", "content": query},
        ],
        "max_tokens": max_tokens,
        "temperature": 0.7,  # Adjust temperature for response variability
        "top_p": 0.95,  # Use top-p sampling
        "reasoning_format": "parsed"
    }

    try:
        response = requests.post(
            f"{api_base}/chat/completions", headers=headers, json=payload
        )
        response.raise_for_status()  # Raise exception for HTTP errors (4xx or 5xx)
        result: Dict[str, Any] = response.json()
        return result["choices"][0]["message"]["content"]
    except RequestException as e:  # Catch specific requests exceptions
        return f"API Request Error: {str(e)}"
    except KeyError as e:  # Catch potential errors from accessing JSON structure
        return f"API Response Error: Unexpected structure in API response - missing {str(e)}"
    except Exception as e:  # Catch any other unexpected errors
        return f"An unexpected error occurred: {str(e)}"


def parse_command_blocks(response: str) -> list[str]:
    """
    Parses command blocks enclosed in backticks from a given string.

    This function iterates through the provided string, detects code blocks
    enclosed by triple backticks, and extracts their contents. It maintains
    a state to track whether the current line lies inside a code block.
    Lines outside code blocks are ignored.

    Args:
        response (str): The input string potentially containing code blocks.

    Returns:
        list[str]: A list of strings, where each string is the content of a
        code block extracted from the input.
    """
    command_blocks = []
    current_block = []
    in_code_block = False

    for line in response.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            if not in_code_block and current_block:
                command_blocks.append("\n".join(current_block))
                current_block.clear()
        elif in_code_block:
            current_block.append(line)
    return command_blocks
