### Last Lines

This Python script emulates the behavior of the UNIX `tac` command: it prints the lines
of one or more files in reverse order (last line first). It reads files by memory-mapping
them and scanning backwards in configurable-sized chunks, yielding one line at a
time. Lines are decoded as UTF-8, with invalid sequences replaced. The script accepts
one or more file paths as command-line arguments and an optional buffer size.


#### Usage

```bash
$ cat log.txt
log line 1
log line 2

$ python last_lines.py log.txt
log line 2
log line 1\n
```

```python
# run project's example input
$ python last_lines.py inp/example.txt
# or with a maximum buffer size
$ python last_lines.py inp/example.txt --bufsize 16
```

#### Extra

`last_lines`: One implementation using `mmap`: simpler, more idiomatic and easier to read.
`faster_last_lines`: One implementation using UNIX file operations "primitives" to improve memory utilization
