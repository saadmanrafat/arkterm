import os
import yaml
import json
import sys
from typing import Dict, Any, List, TypedDict

from rich.console import Console

from .palette import GITHUB_DARK_THEME

console = Console(theme=GITHUB_DARK_THEME)

CONFIG_FILE: str = os.path.expanduser("~/.aiterm/config.yaml")  # Changed to .yaml
HISTORY_FILE: str = os.path.expanduser("~/.aiterm/history.json")


# Define TypedDicts for a more precise default config structure
class _ApiConfig(TypedDict):
    api_key: str
    model: str
    api_base: str


class _SettingsConfig(TypedDict):
    allow_command_execution: bool
    max_tokens: int


class DefaultConfig(TypedDict):
    API: _ApiConfig
    SETTINGS: _SettingsConfig


# Helper to define default config structure
def get_default_config_data() -> DefaultConfig:
    """
    Returns the default configuration structure for the application.

    Returns:
        DefaultConfig: An object representing the default configuration structure,
                       with defined API and SETTINGS sections.
    """
    return {
        "API": {
            "api_key": "YOUR_GROQ_API_KEY_HERE",  # Placeholder
            "model": "llama3-8b-8192",
            "api_base": "https://api.groq.com/openai/v1",
        },
        "SETTINGS": {
            "allow_command_execution": False,  # Native boolean
            "max_tokens": 2048,  # Native integer
        },
    }


def setup_config(console: Any) -> None:
    """
    Creates the configuration directory and YAML file if they don't exist.
    If the config file is created, it prints a message and exits,
    prompting the user to add their API key.

    Args:
        console (Any): The rich console object for printing messages.

    Raises:
        SystemExit: If there's an error creating the config directory,
                    writing the config file, or serializing YAML data.
    """
    config_dir = os.path.dirname(CONFIG_FILE)
    try:
        os.makedirs(config_dir, exist_ok=True)
    except OSError as e:
        console.print(
            f"[bold red]Error: Could not create config directory {config_dir}: {e}. Check permissions.[/bold red]"
        )
        sys.exit(1)

    if not os.path.exists(CONFIG_FILE):
        default_config = get_default_config_data()
        try:
            with open(CONFIG_FILE, "w") as f:
                yaml.dump(default_config, f, sort_keys=False, default_flow_style=False)
            console.print(
                f"Created YAML config file at {CONFIG_FILE}. Please edit it to add your Groq API key."
            )
            sys.exit(1)  # Exit after creating, user needs to add API key
        except OSError as e:  # Changed from IOError to OSError
            console.print(
                f"[bold red]Error: Could not write config file to {CONFIG_FILE}: {e}. Check permissions.[/bold red]"
            )
            sys.exit(1)
        except (
            yaml.YAMLError
        ) as e:  # Added 'as e' for consistency, though message doesn't use it yet
            console.print(
                f"[bold red]Error: Could not write YAML config file to {CONFIG_FILE} due to YAML error: {e}.[/bold red]"
            )
            sys.exit(1)


def load_config() -> Dict[str, Any]:
    """
    Loads configuration from the YAML config file.
    Exits if the file is not found, empty, not a valid dictionary structure,
    corrupted, or unreadable.

    Returns:
        Dict[str, Any]: The configuration data loaded from the YAML file.

    Raises:
        SystemExit: If there's an error loading, parsing, or validating the config file.
    """
    if not os.path.exists(CONFIG_FILE):
        print(
            f"[bold red]Error: Config file {CONFIG_FILE} not found. Run with --setup to create it.[/bold red]",
            file=sys.stderr,
        )
        sys.exit(1)

    try:
        with open(CONFIG_FILE, "r") as f:
            config_data: Any = yaml.safe_load(f)  # Read as Any first

            if config_data is None:  # File is empty or contains only comments/null
                print(
                    f"[bold red]Error: Config file {CONFIG_FILE} is empty or invalid (parses to null). "
                    f"Delete it and run with --setup to recreate.[/bold red]",
                    file=sys.stderr,
                )
                sys.exit(1)

            if not isinstance(config_data, dict):
                print(
                    f"[bold red]Error: Config file {CONFIG_FILE} does not contain a valid dictionary structure. "
                    f"Please ensure it is a YAML mapping. Delete it and run with --setup to recreate if unsure.[/bold red]",
                    file=sys.stderr,
                )
                sys.exit(1)

            return config_data  # Now known to be a dict

    except yaml.YAMLError as e:
        print(
            f"[bold red]Error: Config file {CONFIG_FILE} is corrupted: {e}. "
            f"Please fix it or delete it and run with --setup.[/bold red]",
            file=sys.stderr,
        )
        sys.exit(1)
    except OSError as e:  # Changed from IOError to OSError
        print(
            f"[bold red]Error: Could not read config file {CONFIG_FILE}: {e}. "
            f"Check permissions.[/bold red]",
            file=sys.stderr,
        )
        sys.exit(1)


def save_config(config_data: Dict[str, Any]) -> None:
    """
    Saves configuration data to the YAML config file.

    Args:
        config_data (Dict[str, Any]): The configuration data to save.

    Raises:
        OSError: If the directory for the config file cannot be created,
                 or if the config file cannot be opened or written to.
        yaml.YAMLError: If there's an error during YAML serialization (this is generally unexpected).
    """
    try:
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(config_data, f, sort_keys=False, default_flow_style=False)
    except OSError:  # Changed from IOError to OSError for modern Python style
        # Let the caller handle this and inform the user via console
        raise
    except yaml.YAMLError:
        # This would be unexpected with yaml.dump
        raise


def save_to_history(query: str, response: str) -> None:
    """
    Saves a query and its corresponding response to the history file.
    The history is stored as a list of JSON objects, each containing a query-response pair.
    If the history file is corrupted, unreadable, or unwritable, an error is printed to stderr.

    Args:
        query (str): The user's query.
        response (str): The AI's response.
    """
    try:
        os.makedirs(os.path.dirname(HISTORY_FILE), exist_ok=True)
    except OSError as e:
        print(
            f"[bold red]Error: Could not create directory for history file {HISTORY_FILE}: {e}. History will not be saved.[/bold red]",
            file=sys.stderr,
        )
        return

    history: List[Dict[str, str]] = []
    if os.path.exists(HISTORY_FILE):
        try:
            # Attempt to open and read the history file
            with open(HISTORY_FILE, "r") as f:
                # Check if file is empty before attempting to load JSON
                if os.path.getsize(HISTORY_FILE) > 0:
                    history = json.load(f)
                # else: file exists but is empty, so history remains []
        except json.JSONDecodeError:
            print(
                f"[yellow]Warning: History file {HISTORY_FILE} was corrupted or invalid. Starting with new history.[/yellow]",
                file=sys.stderr,
            )
            # history remains [], effectively starting a new one
        except IOError as e:
            print(
                f"[bold red]Error: Could not read history file {HISTORY_FILE}: {e}. Proceeding with new history for this session.[/bold red]",
                file=sys.stderr,
            )
            # history remains [], effectively starting a new one for this session's save

    history.append({"query": query, "response": response})

    try:
        with open(HISTORY_FILE, "w") as f:
            json.dump(history, f, indent=2)
    except IOError as e:
        print(
            f"[bold red]Error: Could not write to history file {HISTORY_FILE}: {e}.[/bold red]",
            file=sys.stderr,
        )
