import os
import argparse
import json
from rich.console import Console
from rich.markdown import Markdown

from .config import (CONFIG_FILE, HISTORY_FILE, setup_config,
                            load_config, save_to_history)
from .core import get_ai_response
from .interactive import interactive_mode

console = Console()

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
    response = get_ai_response(query, config)
    console.print(Markdown(response))
    save_to_history(query, response)

def main():
    parser = argparse.ArgumentParser(description="Shell Shocked: Wire an LLM Directly into Your Linux Terminal")
    parser.add_argument('query', nargs='*', help='query LLM integrated terminal')
    parser.add_argument('-i', '--interactive', action='store_true', help='Start interactive mode')
    parser.add_argument('--history', action='store_true', help='Show query history')
    parser.add_argument('--setup', action='store_true', help='Run setup process')
    args = parser.parse_args()

    if args.setup:
        handle_setup()
        return

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
        parser.print_help()

