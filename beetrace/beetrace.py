import json
import os
import shlex
import subprocess
import sys
from time import sleep
from typing import Final, Iterator

from psutil import Process
from rich.console import Console

LOGO: Final = r"""
___  ____ ____ ___ ____ ____ ____ ____ 
|__] |___ |___  |  |__/ |__| |    |___ 
|__] |___ |___  |  |  \ |  | |___ |___ 
"""

REQUIRED_USDT_PROBES: Final = {"function__entry", "function__return", "line"}
CODE: Final = '{printf("*mode*|%s|%d|%s", str(arg0), arg2, str(arg1))}'
LINE_LIMIT: Final = 40

console = Console()


class BeeTrace:
    def __init__(self, mode: str, process: Process) -> None:
        self.mode = mode
        self.process = process

        if self.mode == "line":
            self.program = (
                f"usdt:{process.exe()}:line {CODE.replace('*mode*', 'line')}"
            )
        elif self.mode == "func":
            self.program = (
                f"usdt:{process.exe()}:function__entry {CODE.replace('*mode*', 'entry')}"
                f"usdt:{process.exe()}:function__return {CODE.replace('*mode*', 'return')}"
            )

    def run_cmd(self, cmd: str) -> Iterator[str]:
        args = shlex.split(f"bpftrace -f json {cmd} -p {self.process.pid}")
        p = subprocess.Popen(
            args,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True,
        )

        try:
            yield from iter(p.stdout.readline, "")
            p.stdout.close()
            p.wait()
            if p.returncode:
                console.print(p.stderr.read(), style="bold red")
                p.stderr.close()
                sys.exit(p.returncode)
            p.stderr.close()
        except KeyboardInterrupt:
            p.stdout.close()
            p.stderr.close()
            p.wait()

    def get_header(self) -> None:
        os.system(r'printf "\e[2J\e[3J\e[H"')
        console.print(
            f"{LOGO}\nPID: {self.process.pid} | Tracing from: ", end=""
        )
        console.print(*self.process.cmdline(), style="green")
        console.print("\nPress Control-C to quit.\n", style="italic bold red")
        console.print(
            f"{'Path': <50} {'File:Line': <50} {'Function': <50}",
            style="bright_blue",
        )

    def usdt_exists(self) -> bool:
        usdt_probes = set()

        for output in self.run_cmd("-l usdt:*"):
            usdt_probe = output.split("python:")[-1].replace("\n", "")
            usdt_probes.add(usdt_probe)

        if REQUIRED_USDT_PROBES.issubset(usdt_probes):
            return True
        else:
            console.print("USDT probes not found!", style="bold red")
            return False

    def listen(self) -> None:
        if self.usdt_exists():
            self.get_header()
            line_count = 0

            for output in self.run_cmd(f"-e '{self.program}'"):
                if output == "\n":
                    break
                data = json.loads(output)
                if data["type"] == "printf":
                    probe, loc, line_no, func_name = data["data"].split("|")
                    path, file_name = os.path.split(loc)
                    file_no = f"{file_name}:{line_no}"

                    if probe == "entry":
                        console.print(
                            f"{path:<50} => {file_no:<50} {func_name:<50}"
                        )
                    elif probe == "return":
                        console.print(
                            f"{path:<50} <= {file_no:<50} {func_name:<50}"
                        )
                    else:
                        console.print(
                            f"{path:<50} {file_no:<50} {func_name:<50}"
                        )

                    if line_count > LINE_LIMIT:
                        self.get_header()
                        line_count = 0

                    line_count += 1
                    sleep(0.1)
