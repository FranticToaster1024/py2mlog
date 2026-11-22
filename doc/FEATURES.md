# Features

> **Note**: Mlog code runs in a loop. As such, your python code does too.


Assignment and operators:
```py
x = 42
y = x**2
y -= 6.7
z = x < y > (4.2 if x < 123 else 6.7)
foo = a and b and c
```

> **Note**: Proper short-circuiting behaviour is not implemented.
For example:
```py
foo = False or Env.copper  # correctly returns Env.copper
assert foo == Env.copper


def f():
    print("f() was called!")


foo = False and f()  # wrongly calls f() instead of short circuiting
```
This also means chaining many BoolOps or comparisons can get quite expensive.



`If`, `elif` and `else`:
```py
if foo < 67:
    x += 10
elif foo < 100:
    x -= 20
else:
    x *= 2
```


`while` loops, `break`, `continue` and loop/`else` (these are also supported in `for` loops.):
```py
while True:
    if y > 0:
        y -= 1
        continue

    if x > 10:
        break

    x += 1
else:
    completed = True
```


`for ... range()`:
```py
result = 0
for i in range(5):
    for j in range(i, 10 * 2, 3):
        result += j
```
> **Note**: The loop iteration number can be modified directly; be wary of this. For example:
```py
for i in range(10):
    # oh no!
    i += 10
```


`for ... Env.links()`:
```py
for l in Env.links():
    l.disable()
```


`print()` with fstring support:
```py
print("Hello World!")
# compiled:
# print "Hello World!\n"
# printflush message1

print("Hello", "World", sep=" !!", end="\n\n", flush=False)
# flush is 'message1' by default
# flush=True isn't a thing though,
# you have to pass a flush target like 'message2'
# notify, toast, etc. aren't supported yet

foo = 42
bar = 67
print(f"{foo} + {bar} = {foo + bar}")
# compiled:
# op add __p2m_tmp0 foo bar
# print "{0} + {0} = {0}\n"
# format foo
# format bar
# format __p2m_tmp0
# printflush message1

print("You", "can", "chain", "any", "number", "of", "pos", "args!")
# compiled:
# print "You can chain any number of pos args!\n"
# printflush message1

foo = "\n"
print("Non-literal", "separators", "are", "allowed!", sep=foo)
# but they can get expensive quick!
# print "Non-literal{0}separators{0}are{0}allowed!\n"
# format foo
# format foo
# format foo
# printflush message1
```


Very basic python builtins, more coming soon<sup>TM</sup>.
```py
x = abs(-5)
y = ord("!")
z = max(a, b)  # only 2 args for now unfortunately
```


Most operation instructions. A few have been renamed due to ambiguity in a python context.
e.g. `op angle` is available as `vec_angle()`.
Note that some python builtins may be shadowed.
```py
x = sin(67)
x = rand(10)
x = sqrt(16)

...
```


Some mlog instructions:
```py
set_rate(5)  # setrate 5
print_char(0x41)  # printchar 65
print_raw("foo{0}bar")  # print "foo{0}bar"
format_raw(123)  # format 123
```


Raw mlog using `mlog_raw()`:
```py
mlog_raw(r"""
set x 0
l1:
    print x
    print "\n"
    op add x x 1
jump l1 lessThan x 32
printflush message1
""")
```
> **Note**: These are parsed and treated identically to compiled mlog instructions; optimizations still apply to them. In other words, what you pass to `mlog_raw()` may be different from the actual mlog output.
> **Note**: Absolute line numbers in jump instructions will be interpreted literally, not relative to the function call. Use labels whenever possible.


Non-recursive custom function definitions.
> **Note**: these functions **do not** use a call stack.
```py
def is_odd(n):
    return n % 2 == 1


sixty_seven_is_odd = is_odd(67)
```


Non-recursive custom inline function definitions using the `@inline` decorator:
```py
@inline
def func(x):
    return x * 2 + 1


y = func(42)
```
<!--these work quite beautifully but i have no idea why it works atp-->

> **Note**: **Recursive functions are unsupported!** There is a very basic check in place, but it probably doesn't cover all cases.


Imports from `py2mlog`, which don't actually do anything except please your type checker. Only the name of the module (i.e. `py2mlog`) is checked.
```py
from py2mlog import Env, Links, sin
from py2mlog import *

# type checker will complain but compiler doesn't care
from py2mlog import foobarbaz

# compiler will raise error here
from foobar import baz

# unsupported
import py2mlog
from py2mlog.Screen import flush
```
On a related note, please do let me know if i forgot to include something in the stub, or if it doesn't work properly.


Access to some mlog builtins via `Env.*`, just like pyndustric.
```py
x = Env.copper
x = Env.water
x = Env.naval_factory
x = Env.counter
```


Subscript access on arbitrary objects:
```py
x = nucleus1[Env.copper]  # sensor x nucleus1 @copper
x = nucleus1["copper"]  # sensor x nucleus1 @copper

x = "foobarbaz"["size"]  # sensor x "foobarbaz" @size

# Note:
# ❌
x = "foobarbaz"[3]  # sensor x "foobarbaz" 3
# ✅
x = Mem.read("foobarbaz", 3)  # read x "foobarbaz" 3
```


Attribute access on arbitrary objects:
```py
x = nucleus1.copper  # sensor x nucleus1 @copper
x = reactor1.heat  # sensor x reactor1 @heat

# Note:
# ❌
x = foo.bar  # sensor x foo @bar
#                           ^
# ✅
x = foo[bar]  # sensor x foo bar
```


`Links` (`Link` is supported for compatibility with pyndustric):
```py
l = Link[0]
l = Links[0]
```

Color literals:
```py
red = "%FF0000"
red = Color("%FF0000")
red = Color("FF0000")
red = Color("FF0000FF")
red = Color(0xFF0000)

red = Colors.red
red = Colors.Red
red = Colors.RED
```


All draw operations, through the `Screen.*` namespace. Any in-game operation names should work here. snake_case and whatevercasethisis variants as well as a few aliases are also available. These should be compatible with pyndustric. I'm too lazy to write an actual sample so here is a slightly modified snippet from the tests:
```py
Screen.clear(0, 127, 255)
Screen.fill(a, b, c)  # alias for 'Screen.clear()'
Screen.color(a, b, c)  # default alpha is 255
Screen.color(a, b, c, d)
Screen.col(Color("%ffffff"))
Screen.stroke(3)
Screen.line(0, 0, x2=80, y2=160)
Screen.rect(0, 0, 80, height=160)
Screen.fill_rect(a, y=b, width=c, height=d)  # alias for 'Screen.rect'
Screen.fillRect(a, y=b, width=c, height=d)  # another alias for 'Screen.rect'
Screen.linerect(0, 0, 80, 160)
Screen.poly(80, 80, 6, 40, 0)
Screen.line_poly(80, 80, 6, 40, 0)

Screen.flush()  # default is 'display1'
```


All unit operations, through the `Unit.*` namespace. Basically same thing as above; should be compatible with pyndustric. This namespace includes `ubind` as `Unit.bind()`, `uradar` as `Unit.radar()` etc. You can access unit types through the `Units.*` namespace.


All control operations, through the `Control.*` namespace, as well as method calls for control operations and `radar`:
```py
Control.enabled(reactor1, True)
Control.enable(reactor1)  # equivalent to above
Control.disable(reactor1)  # equivalent to 'Control.enabled(reactor1, False)
reactor1.disable()  # equivalent to above

Control.shoot(foo, 100, 100, True)
Control.shoot(foo, 100, 100)  # default is True
foo.shoot(100, 100)  # equivalent to above

x = turret1.radar("enemy", "flying", order=1, key="max_health")

...
```


Reading and writing to `Mem.cell[i]` (i.e. same as pyndustric), as well as `Mem.read()` and `Mem.write()`.
```py
Mem.cell1[0] = Mem.cell1[1] = 1

for i in range(2, 64):
    Mem.cell1[i] = Mem.cell1[i - 1] + Mem.cell1[i - 2]
    i += 1

print(Mem.cell1[63])
```


`assert` statements for some reason:
```py
assert False, "Oopsie!"
```