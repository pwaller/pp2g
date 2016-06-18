#! /usr/bin/env python3

import ast
import sys

import translate


def load(file: str):
    with open(file) as fd:
        src = fd.read()
    module_node = ast.parse(src, file)
    return module_node


def main():
    """
    Convert python code to a go skeleton
    """
    files = sys.argv[1:]

    for file in files:
        module_node = load(file)
        translate.module(file, module_node)


if __name__ == "__main__":
    main()
