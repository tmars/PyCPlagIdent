#coding=utf8
import sys, re, os
from struct import DataType, BlockType, Block, Function, Program
from libs.pycparser import c_parser, c_ast, parse_file, c_generator
import libs.chardet as chardet
from config_container import Config
import codecs

class SCParser(object):

    @staticmethod
    def prepare_file(filename):
        f = open(filename)
        data = f.read()
        f.close()

        e = chardet.detect(data)

        if (e['confidence'] == 0.99 and e['encoding'] == 'windows-1251'):
            data = data.decode('cp1251').encode('utf-8')
        elif (e['confidence'] == 1.0 and e['encoding'] == 'UTF-8'):
            data = data.decode('utf-8-sig').encode('utf-8')

        new_line = '\r\n\r\n'
        if not data.endswith(new_line):
            data += new_line

        f = open(filename, 'w')
        f.write(data)
        f.close()

    @staticmethod
    def parse_to_ast(filename):
        SCParser.prepare_file(filename)
        ast = parse_file(filename = filename,
            use_cpp = True,
            cpp_path='libs/pycparser/utils/cpp.exe',
            cpp_args=r'-Ilibs/pycparser/utils/fake_libc_include'
        )
        return ast

    @staticmethod
    def make_tree(dir):
        tree = []
        names = os.listdir(dir)
        for name in names:
            #fullname = os.path.join(dir, name)
            fn = dir + '/' + name
            if os.path.isfile(fn):
                ext = fn.split('.')[-1].lower()
                if ext == 'c':
                    SCParser.prepare_file(fn)
                    tree.append(fn)
                elif ext == 'h':
                    SCParser.prepare_file(fn)

            elif os.path.isdir(fn):
                tree.extend(SCParser.make_tree(fn))

        return tree

    @staticmethod
    def scan_for_programs(dir, prefix = ''):
        filenames = SCParser.make_tree(dir)
        programs = []
        for fn in filenames:
            try:
                program = SCParser.parse_program(fn, prefix)
                programs.append(program)
            except Exception as e:
                print u'Ошибка при разборе файла %s' % (e)
        return programs

    @staticmethod
    def parse_program(filename, prefix = ''):

        ast = SCParser.parse_to_ast(filename)

        scanner = AstVisitor()
        scanner.visit(ast)

        headers = SCParser.parse_headers(filename)

        generator = c_generator.CGenerator()
        source_code = generator.visit(ast)

        program = Program()
        program.set_name(filename[len(prefix):])
        program.set_source_code(source_code)
        for header in headers:
            program.add_header(header)
        for function in scanner.functions:
            program.add_function(function)
        for var in scanner.global_vars:
            program.add_global_var(var)
        return program

    @staticmethod
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

class AstVisitor(c_ast.NodeVisitor):

    def __init__(self):
        self.functions = []
        self.global_vars = []
        self.typedefs = {}

    def visit_FuncDef(self, node):
        return_type = self.explain_type(node.decl.type.type)

        if node.decl.type.args:
            args = [self.explain_type(arg) for arg in node.decl.type.args.params]
        else:
            args = []

        block = self.build_block(BlockType.FUNCTION, node.body.block_items)

        func = Function(block)
        func.set_name(node.decl.name)
        func.set_return_type(return_type)
        for arg in args:
            func.add_argument(arg)
        self.functions.append(func)

    def visit_Decl(self, node):
        data_type = self.explain_type(node)
        self.global_vars.append(data_type)

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
            block = Block(BlockType.LABEL)
            block.add_child(self.build_blocks_tree(decl.stmt))
            blocks.append(block)

        elif typ == c_ast.Goto:
            blocks.append(Block(BlockType.GOTO))

        elif typ == c_ast.InitList:
            blocks.append(Block(BlockType.INIT_LIST))

        elif typ == c_ast.Assignment:
            block = Block(BlockType.ASSIGNMENT)
            if not isinstance(decl.lvalue, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.lvalue))
            if not isinstance(decl.rvalue, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.rvalue))
            blocks.append(block)

        elif typ == c_ast.Return:
            block = Block(BlockType.RETURN)
            if decl.expr and not isinstance(decl.expr, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.expr))
            blocks.append(block)

        elif typ == c_ast.Cast:
            block = Block(BlockType.CAST)
            if not isinstance(decl.expr, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.expr))
            blocks.append(block)

        elif typ == c_ast.UnaryOp:
            block = Block(BlockType.UNARY_OP)
            if not isinstance(decl.expr, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.expr))
            blocks.append(block)

        elif typ == c_ast.BinaryOp:
            block = Block(BlockType.BINARY_OP)
            if not isinstance(decl.left, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.left))
            if not isinstance(decl.right, c_ast.ID):
                block.add_child(self.build_blocks_tree(decl.right))
            blocks.append(block)

        elif typ == c_ast.TernaryOp:
            blocks.append(self.build_block(BlockType.TERNARY_OP, decl.iftrue))
            if decl.iffalse:
                blocks.append(self.build_block(BlockType.TERNARY_OP, decl.iffalse))

        elif typ == c_ast.FuncCall:
            block = Block(BlockType.FUNC_CALL)
            if decl.args and decl.args.exprs:
                block.add_child(self.build_blocks_tree(decl.args.exprs))
            blocks.append(block)

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
            block = Block(BlockType.EXPR_LIST)
            block.add_child(self.build_blocks_tree(decl.exprs))
            blocks.append(block)

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

    def build_block(self, typ, decls):
        local_vars = []
        children = []

        if isinstance(decls, c_ast.Compound):
            decls = decls.block_items
        elif not isinstance(decls, list):
            decls = [decls]
        if not(decls == None):
            for decl in decls:
                if isinstance(decl, c_ast.Decl):
                    local_vars.append(self.explain_type(decl))
                    if decl.init:
                        children.extend(self.build_blocks_tree(decl.init))
                else:
                    children.extend(self.build_blocks_tree(decl, local_vars))
        block = Block(typ)
        for child in children:
            block.add_child(children)
        for var in local_vars:
            block.add_local_var(var)
        return block