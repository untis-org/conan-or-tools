# Ortools as conan package

This repo contains a [conan](https://conan.io/) recipe for googles [or-tools](https://github.com/google/or-tools) optimization library. 

This is meant to "just work", not to be beautiful. The many dependencies of or-tools make it difficult to find a neat way of producing this conan-package.

**Note**:

- only version 9.8 of or-tools has been ported to work as conan package so far
- several patches had to be added in order to compile on windows in every configuration we needed
- under linux a custom linker-script had to be written as the consumer of this package would otherwise link the many dependencies of or-tools in an arbitrary order, which does not work
- we did not try to conanize every package or-tools has as dependency such as cbc, zlib, etc., but every dependency is bundled within this package
- if you use any of or-tools dependencies in other places this could result in doubly defined symbols and/or differing versions of the same library in the same project - to overcome this, there is only one (admittedly ugly) way we are aware of: include or-tools in a shared library and link against that from the rest of your project.

