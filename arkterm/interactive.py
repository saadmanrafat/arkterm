"""
Interactive mode for the AI Terminal Assistant.

This module provides an interactive shell for users to interact with the AI assistant, execute commands, and manage configuration.
"""

import os
import subprocess
from rich.markdown import Markdown
from rich.console import Console
from .config import (
    CONFIG_FILE,
    load_config,
    save_to_history,
    save_config,
    DefaultConfig,
)
from .terminal_utils import execute_command
from .core import fetch_response, parse_command_blocks
from .palette import GITHUB_DARK_THEME
from textwrap import dedent


console = Console(theme=GITHUB_DARK_THEME)

HELP_TEXT = f"""
[bold blue]

    █████╗ ██████╗ ██╗  ██╗████████╗███████╗██████╗ ███╗   ███╗
   ██╔══██╗██╔══██╗██║ ██╔╝╚══██╔══╝██╔════╝██╔══██╗████╗ ████║
   ███████║██████╔╝█████╔╝    ██║   █████╗  ██████╔╝██╔████╔██║
   ██╔══██║██╔══██╗██╔═██╗    ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║
   ██║  ██║██║  ██║██║  ██╗   ██║   ███████╗██║  ██║██║ ╚═╝ ██║
   ╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝   ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝
                                                 v0.1.0-dev.2


    AI Agent for Linux Terminal
    [/bold blue]
    
    [bold white]    
    USAGE:
        $ arkterm [command]
    
    COMMANDS:
        query                             Ask a question directly
        interactive -i, --interactive     Start interactive mode
        history     --history             Display query history
        setup       --setup               Re-create the configuration file

    SUBCOMMANDS interactive -i, --interactive
        
        !help                             Show this help message
        !exec <command>                   Execute a shell command directly
        !run                              Run a command and display the output
        !config                           Show or edit configuration settings
        !model                            Show or change the AI model
        !exit                             Exit the interactive mode
    [/bold white]
    """


MODEL_LIST_TEXT = dedent(
    """
    - llama3-8b-8192 (Fast, efficient)
    - llama3-70b-8192 (More powerful)
    - mixtral-8x7b-32768 (Mixtral model)
    - gemma-7b-it (Google's Gemma model)
"""
)
AVAILABLE_MODELS = [
    "llama3-8b-8192",
    "llama3-70b-8192",
    "mixtral-8x7b-32768",
    "gemma-7b-it",
]


def _handle_help(console: Console) -> None:
    """
    Display the help message for special commands in interactive mode.

    Args:
        console (Console): The rich Console object for output.
    """
    console.print(HELP_TEXT)


def _handle_config(console: Console, config: DefaultConfig) -> DefaultConfig:
    """
    Open the config file in the user's preferred editor and reload the configuration.

    Args:
        console (Console): The rich Console object for output.
        config (DefaultConfig): The current configuration.

    Returns:
        DefaultConfig: The (possibly updated) configuration after editing.
    """
    editor = os.environ.get("EDITOR", "nano")
    try:
        subprocess.run([editor, CONFIG_FILE], check=True)
    except Exception as e:
        console.print(f"[bold red]Failed to open editor '{editor}': {e}[/bold red]")
        return config

    try:
        new_config = load_config()
        console.print(
            f"Config reloaded. Using model: [bold]{new_config['API']['model']}[/bold]"
        )
        return new_config
    except Exception as e:
        console.print(
            f"[bold red]Error reloading config: {e}. Please check config.yaml or run --setup.[/bold red]"
        )
        return config


def _handle_model(console: Console, config: DefaultConfig) -> None:
    """
    Show available models and allow the user to change the current model.

    Args:
        console (Console): The rich Console object for output.
        config (DefaultConfig): The current configuration (will be updated in-place).
    """
    console.print("\n[bold]Available Groq Models:[/bold]")
    console.print(MODEL_LIST_TEXT)
    console.print(f"\nCurrently using: [bold]{config['API']['model']}[/bold]")
    change: str = input(
        "\nChange model? (Enter model name or press Enter to keep current): "
    ).strip()
    if change:
        if change not in AVAILABLE_MODELS:
            console.print(
                f"[bold red]Model '{change}' is not in the list of available models.[/bold red]"
            )
            return
        config["API"]["model"] = change
        try:
            save_config(config)
            console.print(f"Model changed to: [bold]{change}[/bold]")
        except Exception as e:
            console.print(
                f"[bold red]Error saving model change to config: {e}[/bold red]"
            )


def _handle_exec(console: Console, cmd: str, allow_execution: bool) -> None:
    """
    Execute a shell command if allowed, and display the result or error.

    Args:
        console (Console): The rich Console object for output.
        cmd (str): The shell command to execute.
        allow_execution (bool): Whether command execution is enabled in the config.
    """
    if not cmd.strip():
        console.print("[bold red]No command provided to execute.[/bold red]")
        return
    if not allow_execution:
        console.print(
            "[bold red]Command execution is disabled.[/bold red] Enable it in config.yaml."
        )
        return
    console.print(f"[bold yellow]Executing:[/bold yellow] {cmd}")
    try:
        result: str = execute_command(cmd)
        console.print(result)
    except Exception as e:
        console.print(f"[bold red]Error executing command: {e}[/bold red]")


def _handle_command_blocks(
    console: Console, command_blocks: list[str], allow_execution: bool
) -> None:
    """
    Display command blocks from the AI response and optionally execute them if allowed.

    Args:
        console (Console): The rich Console object for output.
        command_blocks (list[str]): List of command block strings to display/execute.
        allow_execution (bool): Whether command execution is enabled in the config.
    """
    for i, cmd_block in enumerate(command_blocks):
        console.print(f"\n[bold yellow]Command block {i+1}:[/bold yellow]")
        console.print(cmd_block)
    if not allow_execution:
        return
    if len(command_blocks) == 1:
        execute = input("\nExecute this command? (y/n): ").lower().strip()
        if execute == "y":
            try:
                result = execute_command(command_blocks[0])
                console.print(result)
            except Exception as e:
                console.print(f"[bold red]Error executing command: {e}[/bold red]")
        return
    # Multiple command blocks
    while True:
        block_num = input(
            "\nEnter block number to execute (or press Enter to skip): "
        ).strip()
        if not block_num:
            return
        if block_num.isdigit() and 1 <= int(block_num) <= len(command_blocks):
            idx = int(block_num) - 1
            try:
                result = execute_command(command_blocks[idx])
                console.print(result)
            except Exception as e:
                console.print(f"[bold red]Error executing command: {e}[/bold red]")
            return
        else:
            console.print(
                f"[bold red]Invalid block number. Please enter a number between 1 and {len(command_blocks)}, or press Enter to skip.[/bold red]"
            )


def interactive_mode(config: DefaultConfig, console: Console) -> None:
    """
    Start the AI Terminal Assistant in interactive mode, providing a REPL for user interaction.

    Args:
        config (DefaultConfig): The configuration dictionary for the assistant.
        console (Console): The rich Console object for formatted output.
    """

    def _main_loop(config: DefaultConfig) -> None:
        allow_execution: bool = config["SETTINGS"]["allow_command_execution"]
        while True:

            query: str = input("\n> ")
            if not query.strip():
                continue
            if query == "!help":
                _handle_help(console)
                continue
            if query == "!exit":
                break
            if query == "!config":
                config = _handle_config(console, config)
                allow_execution = config["SETTINGS"]["allow_command_execution"]
                continue
            if query == "!model":
                _handle_model(console, config)
                continue
            if query.startswith("!exec ") and len(query) > 6:
                _handle_exec(console, query[6:], allow_execution)
                continue
            console.print("[cyan]Thinking...[/cyan]")
            try:
                response: str = fetch_response(query, config)
            except Exception as e:
                console.print(f"[bold red]Error getting AI response: {e}[/bold red]")
                continue
            console.print(Markdown(response))
            save_to_history(query, response)
            command_blocks = parse_command_blocks(response)
            if command_blocks:
                _handle_command_blocks(console, command_blocks, allow_execution)

    # Welcome banner
    console.print(
        "[bold green]AI Terminal Assistant - Interactive Mode[/bold green] ([bold]Ctrl+C[/bold] to exit)"
    )
    console.print(f"Using model: [bold]{config['API']['model']}[/bold]")
    _handle_help(console)

    try:
        _main_loop(config)
    except KeyboardInterrupt:
        console.print("\n[bold green]Exiting interactive mode.[/bold green]")
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/bold red]")
