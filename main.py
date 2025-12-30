import argparse

from api_server import run_server
from cli import TaskCLI


def main():
    """Main entry point for the task management application.

    Parses command-line arguments to determine whether to start the API server
    or run the CLI interface. Handles mode selection and passes arguments
    to the appropriate component.
    """
    parser = argparse.ArgumentParser(description="Task Management System")
    parser.add_argument(
        "mode",
        choices=["api", "cli"],
        help="Run mode: api (start server) or cli (command-line interface)",
    )
    parser.add_argument(
        "--host", default="localhost", help="API server host (default: localhost)"
    )
    parser.add_argument(
        "--port", type=int, default=8000, help="API server port (default: 8000)"
    )

    args, remaining = parser.parse_known_args()

    if args.mode == "api":
        run_server(host=args.host, port=args.port)
    elif args.mode == "cli":
        cli = TaskCLI()
        # Pass remaining arguments to CLI
        import sys

        sys.argv = ["cli.py"] + remaining
        cli.run()


if __name__ == "__main__":
    main()
