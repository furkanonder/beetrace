<div align="center">
  <img src="/assets/logo/beetrace.png" width=500px />
  <h2>Trace your python process line by line with low overhead!</h2>
</div>

_beatrace_ allows you to trace a Python process line by line or the functions' entries
and returns. It uses USDT(User Statically-Defined Tracing) probes with
[bpftrace](https://github.com/iovisor/bpftrace/).

## Dependencies

- This package is only available for Linux and requires bpftrace. You can look at the
  bpftrace installation
  [here](https://github.com/iovisor/bpftrace/blob/master/INSTALL.md).

- CPython must be
  [configured with the --with-dtrace option](https://docs.python.org/3/using/configure.html#cmdoption-with-dtrace).

## Installation

```bash
pip install beetrace
```

## Usage & Example

To trace the Python process, use the -p parameter to pass the pid value.

```bash
beetrace -p {pid of process}
```

Let's take a look at the quick example.

---

```bash
$ cat -n example.py
1 import os
2 from time import sleep
3
4
5 def c():
6     x = 1
7
8 def b():
9     y = 2
10    c()
11
12
13 def a():
14     z = 1
15     b()
16
17
18 while True:
19     print(f"PID of program: {os.getpid()}")
20     sleep(1)
21     print("Sleep 1 second")
22     a()
```

Output:

```bash
PID of program: 17988
Sleep 1 second
PID of program: 17988
Sleep 1 second
PID of program: 17988
Sleep 1 second
PID of program: 17988
...
...
...
```

```bash
$ beetrace -p 17988
___  ____ ____ ___ ____ ____ ____ ____
|__] |___ |___  |  |__/ |__| |    |___
|__] |___ |___  |  |  \ |  | |___ |___

PID: 17988 | Tracing from: python3 example.py

Press Control-C to quit.

Path                                   File:Line                                          Function
/tmp                                   example.py:18                                      <module>
/tmp                                   example.py:19                                      <module>
/tmp                                   example.py:20                                      <module>
/tmp                                   example.py:21                                      <module>
/tmp                                   example.py:22                                      <module>
/tmp                                   example.py:14                                      a
/tmp                                   example.py:15                                      a
/tmp                                   example.py:9                                       b
/tmp                                   example.py:10                                      b
/tmp                                   example.py:6                                       c
/tmp                                   example.py:18                                      <module>
/tmp                                   example.py:19                                      <module>
/tmp                                   example.py:20                                      <module>
/tmp                                   example.py:21                                      <module>
/tmp                                   example.py:22                                      <module>
/tmp                                   example.py:14                                      a
/tmp                                   example.py:15                                      a
/tmp                                   example.py:9                                       b
/tmp                                   example.py:10                                      b
/tmp                                   example.py:6                                       c
/tmp                                   example.py:18                                      <module>
/tmp                                   example.py:19                                      <module>
/tmp                                   example.py:20                                      <module>
...                                    ...                                                ...
...                                    ...                                                ...
...                                    ...                                                ...
...                                    ...                                                ...
```
