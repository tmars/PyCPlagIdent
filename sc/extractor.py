#coding=utf8

from libs.pycparser import c_ast, c_parser, c_generator
from config_container import Config
import os
from parser import SCParser

class FuncVisitor(c_ast.NodeVisitor):
    def __init__(self, func_name):
        self.generator = c_generator.CGenerator()
        self.func_name = func_name
        self.func_body = ""

    def visit_FuncDef(self, node):
        if node.decl.name == self.func_name:
            generator = c_generator.CGenerator()
            self.func_body = self.generator.visit(node)

class SCExtractor(object):

    @staticmethod
    def ast_from_sc(source_code):
        filename = "sc.c"
        f = open(filename, "w")
        f.write(source_code)
        f.close()

        ast = SCParser.parse_to_ast(filename)

        os.remove(filename)

        return ast

    @staticmethod
    def extract_program(source_code):
        ast = SCExtractor.ast_from_sc(source_code)
        generator = c_generator.CGenerator()
        return generator.visit(ast)

    @staticmethod
    def extract_function(source_code, func_name):
        ast = SCExtractor.ast_from_sc(source_code)
        scanner = FuncVisitor(func_name)
        scanner.visit(ast)

        return scanner.func_body