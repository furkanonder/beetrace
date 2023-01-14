import argparse

from psutil import Process, pid_exists
from rich import print

from beetrace.beetrace import BeeTrace


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Trace your python process line by line with low overhead!"
    )
    parser.add_argument("-v", "--version", action="version", version="0.0.1")
    parser.add_argument("-p", "--pid", type=int, help="Process Id")
    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        default="l",
        help="Trace Mode. For line-by-line -m line or -m l. For function call hierarchy -m func-call or -m f.",
    )
    args = parser.parse_args()

    if args.pid:
        if pid_exists(args.pid):
            if args.mode == "l" or args.mode == "line":
                mode = "line"
            elif args.mode == "f" or args.mode == "func-call":
                mode = "func"
            else:
                print(f"Invalid mode: {args.mode}")
                return
            process = Process(args.pid)
            BeeTrace(mode, process).listen()
        else:
            print(f"Process PID not found! | pid={args.pid}")
    else:
        print("You need to enter the PID!")


if __name__ == "__main__":
    main()
