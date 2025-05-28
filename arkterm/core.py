import requests
from typing import Dict, Any, Optional
from requests.exceptions import RequestException
from .terminal_utils import fetch_system_info


def get_ai_response(
    query: str, config: Dict[str, Any], with_system_info: bool = True
) -> str:
    """
    Sends a query to a Groq API and returns the AI's response.

    Args:
        query: The user's query to send to the AI.
        config: A dictionary containing API configuration (key, model, base URL)
                and settings (max_tokens).
        with_system_info: If True, includes system information (OS, shell, CWD)
                          in the prompt to the AI. Defaults to True.

    Returns:
        A string containing the AI's response, or an error message if the
        API request fails.
    """
    api_key: str = config["API"]["api_key"]
    model = config["API"]["model"]
    api_base = config["API"].get("api_base", "https://api.groq.com/openai/v1")
    max_tokens: int = int(config["SETTINGS"].get("max_tokens", "2048"))

    system_message: str = """
                You are an AI assistant integrated into a Linux terminal.

                You can execute commands and provide concise, accurate responses.
                If the user asks for help, provide a brief overview of available commands.
                If the user asks for system information, provide details about the current
                working directory, operating system, and shell. When appropriate, suggest
                commands that can help solve the user's problem.

                Before executing any command, ensure it is safe and appropriate for the user's context.
                Ask the user for confirmation if the command could potentially modify system state or data.

                Here are the main areas you can assist with:

                1. Project Management:
                •  Initialize new projects
                •  Setup development environments
                •  Manage project dependencies
                •  Configure build tools

                2. System Operations:
                •  Monitor processes
                •  View system information
                •  Manage services
                •  Handle network operations

                3. Package Management:
                •  Install and update packages
                •  Manage dependencies
                •  Handle version conflicts

                4. Version Control (Git):
                •  View and manage commits
                •  Branch operations
                •  Handle merges and conflicts
                •  Review changes
                •  Manage remote repositories

                5. File and Directory Operations:
                •  Navigate directories
                •  Create, read, modify, and delete files
                •  Search for files and content
                •  Manage file permissions

                6. Command Execution:
                You can execute commands and provide concise, accurate responses.
                If the user asks for help, provide a brief overview of available commands.
                If the user asks for system information, provide details about the current
                working directory, operating system, and shell. When appropriate, suggest
                commands that can help solve the user's problem.
"""

    if with_system_info:
        system_info: Dict[str, str] = fetch_system_info()
        system_message += f"""
            Current context:
            - Working directory: {system_info['current_dir']}
            - Operating system: {system_info['os']}
            - Shell: {system_info['shell']}
            """

    headers: Dict[str, str] = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    payload: Dict[str, Any] = {
        "model": model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ],
        "max_tokens": max_tokens,
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
    """Parses a response string and extracts shell command blocks.

    Command blocks are identified by triple backticks, optionally followed by
    language identifiers (e.g., 'bash', 'python').

    Args:
        response: The string to parse, which may contain command blocks.

    Returns:
        A list of strings, where each string is a command block found in the
        response. Returns an empty list if no command blocks are found.
    """
    lines: list[str] = response.split("\n")
    in_code_block: bool = False
    command_blocks: list[str] = []
    current_block: list[str] = []

    for line in lines:
        stripped_line = line.strip()
        if stripped_line.startswith("```"):
            if not in_code_block:  # Opening fence
                in_code_block = True
                # current_block is implicitly empty from previous block's close or initialization
            else:  # Closing fence
                in_code_block = False
                if current_block:  # If there was content
                    command_blocks.append("\n".join(current_block))
                current_block = (
                    []
                )  # Reset for the next potential block or if this block was empty
        elif in_code_block:
            current_block.append(line)  # Add content lines

    return command_blocks
