import os
import subprocess
import platform
from typing import Dict


def execute_command(command: str) -> str:
    """
    Executes a shell command and captures the output or error message.

    This function runs a specified shell command using the subprocess module. It
    returns the standard output from the command if it executes successfully, or an
    error message if the command fails.

    Args:
        command: str
            The shell command to be executed.

    Returns:
        str
            The standard output captured from the executed command if successful, or
            an error message string if the command fails.

    Raises:
        subprocess.CalledProcessError
            If the executed process returns a non-zero exit status. The error is
            captured and its output is provided in the return value.
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            text=True,
            capture_output=True,
            stderr=subprocess.STDOUT,
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        return f"Error: {e.output}"


def fetch_system_info() -> Dict[str, str]:
    """
    Fetch system information including current directory, operating system, and shell.

    This function retrieves information about the system environment, such as the
    current working directory, the operating system in use, and the user's shell.
    If an error occurs during the retrieval of this information, it returns an
    error message instead.

    Returns:
        Dict[str, str]: Dictionary containing system information or an error message.
    """
    try:
        return {
            "current_dir": os.getcwd(),
            "os": platform.system(),
            "shell": os.environ.get("SHELL", "unknown"),
            "user": os.environ.get("USER", "unknown"),
        }
    except OSError as e:
        return {"error": str(e)}
