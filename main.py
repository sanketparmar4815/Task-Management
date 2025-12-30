
"""Main entry point for Task Management application."""
import sys
import argparse
from api_server import run_server



def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Task Management System')
    parser.add_argument(
        'mode',
        choices=['api', 'cli'],
        help='Run mode: api (start server) or cli (command-line interface)'
    )
    parser.add_argument(
        '--host',
        default='localhost',
        help='API server host (default: localhost)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8000,
        help='API server port (default: 8000)'
    )
    
    args, remaining = parser.parse_known_args()
    
    if args.mode == 'api':
        run_server(host=args.host, port=args.port)
    


if __name__ == '__main__':
    main()

