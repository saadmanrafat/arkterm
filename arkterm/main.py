import os
import argparse
import json
from rich.console import Console
from rich.markdown import Markdown

from .config import (CONFIG_FILE, HISTORY_FILE, setup_config,
                     load_config, save_to_history)
from .core import fetch_response
from .interactive import interactive_mode
from .palette import GITHUB_DARK_THEME

console = Console(theme=GITHUB_DARK_THEME)

def handle_setup():
    """Re-create the configuration file by running setup."""
    if os.path.exists(CONFIG_FILE):
        os.remove(CONFIG_FILE)
    setup_config(console)


def display_history():
    """Display query history from the history file."""
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, 'r') as f:
            try:
                history = json.load(f)
                for i, entry in enumerate(history):
                    console.print(f"\n[bold]--- Query {i+1} ---[/bold]")
                    console.print(f"[bold cyan]Q:[/bold cyan] {entry['query']}")
                    console.print(f"[bold green]A:[/bold green]")
                    console.print(Markdown(entry['response']))
            except json.JSONDecodeError:
                console.print("[bold red]History file is corrupted.[/bold red]")
    else:
        console.print("[yellow]No history found.[/yellow]")

def run_interactive_mode(config):
    """Launch the interactive mode."""
    interactive_mode(config, console)

def process_single_query(query, config):
    """Handle a single query input and display the response."""
    response = fetch_response(query, config)
    console.print(Markdown(response))
    save_to_history(query, response)

def display_help():
    console.print("""[bold blue]

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
    [/bold white]
    """
    )

def main():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        add_help=False
    )
    parser.add_argument('query', nargs='*')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--history', action='store_true', help='Show query history')
    parser.add_argument('--setup', action='store_true', help='Run setup process')
    parser.add_argument('-h', '--help', action='store_true', help='Show this help message')

    args = parser.parse_args()

    if args.help:
        display_help()
        return

    if args.setup:
        handle_setup()
        return

    # Setup config if not already set up
    setup_config(console)
    config = load_config()

    if args.history:
        display_history()
        return

    if args.interactive:
        run_interactive_mode(config)
        return

    if args.query:
        query = ' '.join(args.query)
        process_single_query(query, config)
    else:
        display_help()
