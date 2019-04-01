# SlimPyNES

A Simple NES Emulator for Study

Originally, This project intends to implement a simple NES Emulater via pure
python. The aim is to study python programing skill.

This emulater is not designed originally. For the most part, it copys from
LameNES, https://github.com/joeyloman/lamenes.git, which is implemented via C
Programming Language. Don't ask me why is LameNES. Just because it's easy to
get and simple enough. Based on LameNES, I did optimize ppu with numpy array
operation.

Currently, as a NES Emulator, this is a failure project. Due to the inefficient
weekness of python, it runs too slow. The framerate is less than 2. Without
ppu optimization with array operation, it's even more slow. The framerate is
less then 1. Maybe after optimizing cpu with Cython or sth else, this emulator
is becoming playable in the future.
