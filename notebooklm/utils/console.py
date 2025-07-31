"""
Console output utilities with color support
"""
import sys
from colorama import init, Fore, Style

# Initialize colorama for cross-platform color support
init()

def print_error(msg):
    """Print error message in red"""
    print(f"{Fore.RED}[ERROR]{Style.RESET_ALL} {msg}", file=sys.stderr)

def print_info(msg):
    """Print info message in green"""
    print(f"{Fore.GREEN}[INFO]{Style.RESET_ALL} {msg}")

def print_progress(msg):
    """Print progress message in cyan"""
    print(f"{Fore.CYAN}[*]{Style.RESET_ALL} {msg}")

def print_warning(msg):
    """Print warning message in yellow"""
    print(f"{Fore.YELLOW}[WARNING]{Style.RESET_ALL} {msg}")

def print_header(title):
    """Print a formatted header"""
    width = 60
    print("\n" + "=" * width)
    print(f"{Fore.CYAN}{title.center(width)}{Style.RESET_ALL}")
    print("=" * width + "\n")
