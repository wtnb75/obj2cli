# Install

- pip install obj2cli

# Usage(single)

```python
import sys
import obj2cli


class A:
    def __init__(self, arg1, arg2):
        self.a = arg1
        self.b = arg2

    def call1(self, c, d=None):
        print("hello {} c={}, d={}".format(self.__dict__, c, d))


if __name__ == "__main__":
    obj2cli.main_single(A, A, sys.argv[1:])
```

```
# python cmd.py --help
usage: A [-h] [--arg1 str] [--arg2 str] {call1} ...

Initialize self. See help(type(self)) for accurate signature.

positional arguments:
  {call1}
    call1

optional arguments:
  -h, --help  show this help message and exit
  --arg1 str
  --arg2 str

# python cmd.py call1 --help
usage: A call1 [-h] [-c str] [-d str]

optional arguments:
  -h, --help  show this help message and exit
  -c str
  -d str

# python cmd.py --arg1 123 --arg2 345 call1 -c hello -d world
hello {'a': '123', 'b': '345'} c=hello, d=world
```

# Usage(multi)

```python
import sys
import obj2cli


class A:
    def __init__(self, a, b):
        self.a = a
        self.b = b

    def call1(self, c, d):
        print("hello {}: {}, c={}, d={}".format(self.__class__.__name__, self.__dict__, c, d))


class B(A):
    pass


if __name__ == "__main__":
    obj2cli.main_cls({A: A, B: B}, sys.argv[1:])
```

# Usage(cli)

```
# obj2cli --module os.path --function basename -- --help
usage: basename [-h] [-p str]

Returns the final component of a pathname

optional arguments:
  -h, --help  show this help message and exit
  -p str

# obj2cli --module os.path --function basename -- -p /usr/bin/ls
ls

# obj2cli --module logging --function warning --positional -- --help
usage: warning [-h] str [str [str ...]]

Log a message with severity 'WARNING' on the root logger. If the logger has no
handlers, call basicConfig() to add a console handler with a pre-defined format.

positional arguments:
  str
  str

optional arguments:
  -h, --help  show this help message and exit
# obj2cli --module logging --function warning --positional -- "hello %s" "world"
2020-01-04 23:16:05,264 WARNING hello world
```

# Links

- [pypi](https://pypi.org/project/obj2cli/)
- [coverage](https://wtnb75.github.io/obj2cli/)
- ~~[local pypi repo](https://wtnb75.github.io/obj2cli/dist/)~~
