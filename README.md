# Simple Math parser

This simple math parser was made as an assignment for compilers course.
It's able to parse and evaluate math statements.

The language supports variables as well as simple math functions such as `sin`, `cos`, `log2`.

## Running

```shell
python3 ./src/math_parser.py

# a = 3
# a = 3.0
#
# log2(a)
# 1.584962500721156
#
# b = 3
# a = 4.0
# b = 3.0
#
# log2(a) + b - 1
# 4.0
```

## Implemented

The following operations are supported:

- [x] Sum, subtract
- [x] Division, multiplication
- [x] Pow, exponential
- [x] Variables, identifiers

## Grammar

The context-free grammar used to create the parser.

```
# EA -> E | ASSIGN (NEW_LINE EA)*
# E -> T (S T)*
# T -> TE (MDIV TE)* 
# TE -> F (^ F)*
# FU -> FUNCTION ( E )
# ASSIGN -> IDENTIFIER EQUAL E
# F -> ( E )
#      | N
#      | FU
#      | IDENTIFIER
#
# NEW_LINE -> \n
# IDENTIFIER -> [a-zA-Z_]+([a-zA-Z0-9_])*
# FUNCTION -> [a-zA-Z]+
# MDIV -> / | *
# EQUAL -> =
# S -> + | -
# N -> [+-]?([0-9][0-9]*(\.[0-9]*)?|\.[0-9][0-9]*)(e[0-9][0-9]*)?
```

# References

References used to create this simple parser

* https://docs.python.org/3/library/re.html#writing-a-tokenizer
* https://developpaper.com/python-technique-implement-simple-recursive-descent-parser/
* https://www.booleanworld.com/building-recursive-descent-parsers-definitive-guide/