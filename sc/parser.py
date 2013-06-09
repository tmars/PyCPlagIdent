#coding=utf8
import sys, re, os
from struct import DataType, BlockType, Block, Function, Program
from libs.pycparser import c_parser, c_ast, parse_file, c_generator
from config_container import Config

def parse_to_ast(filename):
    ast = parse_file(filename=filename,
        use_cpp = True,
        #cpp_path='cpp',
        cpp_path='libs/pycparser/utils/cpp.exe',
        cpp_args=r'-Ilibs/pycparser/utils/fake_libc_include'
    )
    return ast

def scan_for_programs(dir, programs = []):
    names = os.listdir(dir)
    for name in names:
        fullname = os.path.join(dir, name)
        fn = dir + '/' + name
        if (    os.path.isfile(fullname) and
                fullname.split('.')[-1].lower() in ('c')):
            program = parse_program(fn)
            programs.append(program)

        elif os.path.isdir(fullname):
            scan_for_programs(fn)

    return programs

def parse_program(filename):

    ast = parse_to_ast(filename)

    scanner = SourceCodeParser()
    scanner.visit(ast)

    headers = parse_headers(filename)

    generator = c_generator.CGenerator()
    source_code = generator.visit(ast)

    program = Program(filename, source_code, headers, scanner.functions, scanner.global_variables)
    return program

def parse_headers(filename):
    headers = []
    f = open(filename)
    content = f.readlines()
    for line in content:
        if line.strip().startswith('#include'):
            s = line.find('<')
            if s == -1:
                s = line.find('"')
                f = line.find('\"', s+1)
            else:
                f = line.find('>')
            header = line[s+1:f]
            if header in Config.get('standart_headers'):
                headers.append(header)
    return headers

class SourceCodeParser(c_ast.NodeVisitor):

    def __init__(self):
        self.functions = []
        self.global_variables = []
        self.typedefs = {}

    def visit_FuncDef(self, node):
        return_type = self.explain_type(node.decl.type.type)

        if node.decl.type.args:
            args = [self.explain_type(arg) for arg in node.decl.type.args.params]
        else:
            args = []

        block = self.build_block(BlockType.FUNCTION, node.body.block_items)

        func = Function(node.decl.name, return_type, args, block)
        self.functions.append(func)

    def visit_Decl(self, node):
        data_type = self.explain_type(node)
        self.global_variables.append(data_type)

    def visit_Typedef(self, node):
        data_type = self.explain_type(node.type.type)
        self.typedefs[node.name] = data_type

    def explain_type(self, decl, data_type = None):
        """ Recursively explains a type decl node
        """

        if data_type == None:
            data_type = DataType()

        typ = type(decl)

        if typ == c_ast.TypeDecl:
            data_type.names.extend(decl.quals)
            return self.explain_type(decl.type, data_type)

        elif typ == c_ast.Typename or typ == c_ast.Decl:
            return self.explain_type(decl.type, data_type)

        elif typ == c_ast.IdentifierType:
            if len(decl.names) == 1 and self.typedefs.has_key(decl.names[0]):
                data_type = self.typedefs[decl.names[0]]
            else:
                data_type.names.extend(decl.names)
            return data_type

        elif typ == c_ast.PtrDecl:
            data_type.pointer_count += 1
            data_type.names.extend(decl.quals)
            return self.explain_type(decl.type, data_type)

        elif typ == c_ast.ArrayDecl:
            data_type.array_count += 1
            return self.explain_type(decl.type, data_type)

        elif typ == c_ast.FuncDecl:
            data_type.func_pointer_count += 1
            return self.explain_type(decl.type, data_type)

        elif typ == c_ast.Struct:
            data_type.is_struct = True
            return data_type

        elif typ == c_ast.Union:
            data_type.is_union = True
            return data_type

        elif typ == c_ast.Enum:
            data_type.is_enum = True
            return data_type

        else:
            print 'Type Error = %s' % typ
            return data_type

    def build_blocks_tree(self, decl, vars = []):
        typ = type(decl)
        blocks = []

        if typ == list:
            for block in decl:
                blocks.extend(self.build_blocks_tree(block))

        elif typ == c_ast.Switch:
            blocks.append(self.build_block(BlockType.SWITCH, decl.stmt))

        elif typ == c_ast.Case:
            blocks.append(self.build_block(BlockType.CASE, decl.stmts))

        elif typ == c_ast.Default:
            blocks.append(self.build_block(BlockType.DEFAULT, decl.stmts))

        elif typ == c_ast.If:
            blocks.append(self.build_block(BlockType.IF, decl.iftrue))
            if decl.iffalse:
                blocks.append(self.build_block(BlockType.ELSE, decl.iffalse))

        elif typ == c_ast.DoWhile:
            blocks.append(self.build_block(BlockType.DO_WHILE, decl.stmt))

        elif typ == c_ast.For:
            blocks.append(self.build_block(BlockType.FOR, decl.stmt))

        elif typ == c_ast.While:
            blocks.append(self.build_block(BlockType.WHILE, decl.stmt))

        elif typ == c_ast.Label:
            childs = self.build_blocks_tree(decl.stmt)
            blocks.append(Block(BlockType.LABEL, [], childs))

        elif typ == c_ast.Goto:
            blocks.append(Block(BlockType.GOTO))

        elif typ == c_ast.InitList:
            blocks.append(Block(BlockType.INIT_LIST))

        elif typ == c_ast.Assignment:
            childs = []
            if not isinstance(decl.lvalue, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.lvalue))
            if not isinstance(decl.rvalue, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.rvalue))
            blocks.append(Block(BlockType.ASSIGNMENT, [], childs))

        elif typ == c_ast.Return:
            childs = []
            if decl.expr and not isinstance(decl.expr, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.expr))
            blocks.append(Block(BlockType.RETURN, [], childs))

        elif typ == c_ast.Cast:
            childs = []
            if not isinstance(decl.expr, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.expr))
            blocks.append(Block(BlockType.CAST, [], childs))

        elif typ == c_ast.UnaryOp:
            childs = []
            if not isinstance(decl.expr, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.expr))
            blocks.append(Block(BlockType.UNARY_OP, [], childs))

        elif typ == c_ast.BinaryOp:
            childs = []
            if not isinstance(decl.left, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.left))
            if not isinstance(decl.right, c_ast.ID):
                childs.extend(self.build_blocks_tree(decl.right))
            blocks.append(Block(BlockType.BINARY_OP, [], childs))

        elif typ == c_ast.TernaryOp:
            blocks.append(self.build_block(BlockType.TERNARY_OP, decl.iftrue))
            if decl.iffalse:
                blocks.append(self.build_block(BlockType.TERNARY_OP, decl.iffalse))

        elif typ == c_ast.FuncCall:
            childs = []
            if decl.args and decl.args.exprs:
                childs.extend(self.build_blocks_tree(decl.args.exprs))
            blocks.append(Block(BlockType.FUNC_CALL, [], childs))

        elif typ == c_ast.ArrayRef:
            blocks.append(Block(BlockType.ARRAY_REF))

        elif typ == c_ast.StructRef:
            blocks.append(Block(BlockType.STRUCT_REF))

        elif typ == c_ast.Typename:
            blocks.append(Block(BlockType.TYPENAME))

        elif typ == c_ast.Break:
            blocks.append(Block(BlockType.BREAK))

        elif typ == c_ast.Continue:
            blocks.append(Block(BlockType.CONTINUE))

        elif typ == c_ast.EmptyStatement:
            blocks.append(Block(BlockType.EMPTY_STATEMENT))

        elif typ == c_ast.ID or typ == c_ast.Constant:
            pass

        elif typ == c_ast.ExprList:
            childs = self.build_blocks_tree(decl.exprs)
            blocks.append(Block(BlockType.EXPR_LIST, [], childs))

        elif typ == c_ast.Compound:
            blocks.extend(self.build_blocks_tree(decl.block_items))

        elif typ == c_ast.Decl:
            vars.append(self.explain_type(decl))
            if decl.init:
                blocks.extend(self.build_blocks_tree(decl.init))
            pass

        else:
            print 'Block Error = %s' % typ
            #decl.show()

        return blocks

    def build_block(self, typ, blocks):
        loc_vars = []
        childs = []

        if isinstance(blocks, c_ast.Compound):
            blocks = blocks.block_items
        elif not isinstance(blocks, list):
            blocks = [blocks]
        if not(blocks == None):
            for block in blocks:
                if isinstance(block, c_ast.Decl):
                    loc_vars.append(self.explain_type(block))
                    if block.init:
                        childs.extend(self.build_blocks_tree(block.init))
                else:
                    childs.extend(self.build_blocks_tree(block, loc_vars))
        return Block(typ, loc_vars, childs)