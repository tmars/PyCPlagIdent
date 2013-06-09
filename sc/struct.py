#coding=utf8
"""
Классы для хранения структуры программы
"""

import sys, inspect
from config_container import Config
from struct_interface import FunctionBase, ProgramBase

class Node(object):
    """ Базовый класс от которого наследуются все структуры программы
    """

    def children(self):
        pass

    def show(self, buf = sys.stdout, offset = 0, show_name = True):
        """ Используется для вывода структуры программы с учетом вложенности
        """
        lead = ' ' * offset
        if show_name:
            buf.write(lead + self.__class__.__name__ + '\r\n')
        for name,prop in self._attr_names.items():
            val = eval('self.'+prop)
            if val:
                if isinstance(val, str):
                    buf.write(lead + '%s: %s\r\n' % (name, val));
                elif isinstance(val, list):
                    buf.write(lead + name + ':\r\n')
                    for v in val:
                        if isinstance(v, Node):
                            v.show(buf, offset+1, False)
                elif isinstance(val, Node):
                    buf.write(lead + name + ':\r\n')
                    val.show(buf, offset+1, False)

class DataType(Node):

    _attr_names = {'type': 'code()'}

    UNKNOW_TYPE = 0

    TYPES = {
        'char': 1,
        'signed_char': 2,
        'unsigned_char': 3,

        'short_int': 4,
        'short': 4,

        'unsigned_int': 5,
        'unsigned': 5,

        'signed_int': 6,
        'signed': 6,

        'long_int': 7,
        'long': 7,

        'int': 8,

        'long_long_int': 9,
        'unsigned_long_long_int': 10,
        'unsigned_long': 11,

        'float': 12,
        'double': 13,
        'long_double': 14,

        '_Bool': 15,
        'bool': 15,

        'void': 16
    }
    __max_types_count = 17

    def __init__(self):
        self.pointer_count = 0
        self.array_count = 0
        self.func_pointer_count = 0
        self.names = []
        self.is_struct = False
        self.is_union = False
        self.is_enum = False

    def code(self):
        typ = '_'.join(self.names)
        return "%d%d%d%d%d%d%02d" % (
            min(self.pointer_count, Config.get('max_pointer_count')),
            min(self.func_pointer_count, Config.get('max_func_pointer_count')),
            min(self.array_count, Config.get('max_array_count')),
            self.is_struct,
            self.is_union,
            self.is_enum,
            self.TYPES[typ] if self.TYPES.has_key(typ) else self.UNKNOW_TYPE
        )


    """
    @staticmethod
    def get_codes():
        codes = []
        for pc in range(0, Config.get('max_pointer_count') + 1):
            for fpc in range(0, Config.get('max_func_pointer_count') + 1):
                for ac in range(0, Config.get('max_array_count') + 1):
                    for is_s in range(0, 2):
                        for is_u in range(0, 2):
                            for is_e in range(0, 2):
                                for tc in range(0, DataType.__max_types_count + 1):
                                    codes.append("%d%d%d%d%d%d%02d" % (pc, fpc, ac, is_s, is_u, is_e, tc))
        return codes
    """

class BlockType():
    GOTO = 0
    ARRAY_REF = 1
    STRUCT_REF = 2
    TYPENAME = 3
    INIT_LIST = 4
    EXPR_LIST = 5
    IF = 6
    UNARY_OP = 7
    ELSE = 8
    SWITCH = 9
    FUNCTION = 10
    CASE = 11
    DEFAULT = 12
    ASSIGNMENT = 13
    RETURN = 14
    BINARY_OP = 15
    CAST = 16
    TERNARY_OP = 17
    FUNC_CALL = 18
    DO_WHILE = 19
    FOR = 20
    EMPTY_STATEMENT = 21
    WHILE = 22
    BREAK = 23
    CONTINUE = 24
    LABEL = 25

    """
    @staticmethod
    def get_codes(codes = range(0, 26)):
        return codes
    """

class Block(Node):

    _attr_names = {
        'ControlType': 'control_type',
        'LocalVariabes': 'local_variables',
        'Children': 'childs'
    }

    def __init__(self, ctrl_type, loc_vars = [], childs = []):
        self.control_type = ctrl_type
        self.local_variables = loc_vars
        self.childs = childs

    def num_of_control_types(self, types = None):
        types = {} if types == None else types

        if types.has_key(self.control_type):
            types[self.control_type] += 1
        else:
            types[self.control_type] = 1

        for child in self.childs:
            child.num_of_control_types(types)

        return types

    def seq_of_control_types(self, types = None):
        types = [] if types == None else types

        types.append(self.control_type)

        for child in self.childs:
            child.seq_of_control_types(types)

        return types

    def num_of_local_variables(self, variables = None):
        variables = {} if variables == None else variables

        for var in self.local_variables:
            if variables.has_key(var.code()):
                variables[var.code()] += 1
            else:
                variables[var.code()] = 1

        for child in self.childs:
            child.num_of_local_variables(variables)

        return variables

class Function(Node, FunctionBase):

    _attr_names = {
        'Name': 'name',
        'ReturnType': 'ret_type',
        'Arguments': 'args',
        'Block':'block'
    }

    def __init__(self, name, ret_type, args, block):
        self.name = name
        self.ret_type = ret_type
        self.args = args
        self.block = block

    def name(self):
        return self.name

    def ret_type(self):
        return self.ret_type

    def num_of_control_types(self, types = None):
        return self.block.num_of_control_types(types)

    def seq_of_control_types(self, types = None):
        return self.block.seq_of_control_types(types)

    def num_of_local_variables(self, variables = None):
        return self.block.num_of_local_variables(variables)

    def num_of_arguments_variables(self, variables = None):
        variables = {} if variables == None else variables

        for var in self.args:
            if var:
                if variables.has_key(var.code()):
                    variables[var.code()] += 1
                else:
                    variables[var.code()] = 1

        return variables

class Program(Node, ProgramBase):

    _attr_names = {
        'Name': 'name',
        'GlobalVariables': 'global_variables',
        'Functions': 'functions'
    }

    def __init__(self, name, source_code, headers = [], funcs = [], glob_vars = []):
        self.name = name
        self.source_code = source_code
        self.headers = headers
        self.functions = funcs
        self.global_variables = glob_vars

    def name(self):
        return self.name

    def source_code(self):
        return self.source_code

    def functions(self):
        return self.functions

    def num_of_headers(self):
        heads = {}

        for head in self.headers:
            heads[head] = 1

        return heads

    def num_of_global_variables(self):
        variables = {}

        for var in self.global_variables:
            if variables.has_key(var.code()):
                variables[var.code()] += 1
            else:
                variables[var.code()] = 1

        return variables

    def num_of_control_types(self):
        types = {}

        for func in self.functions:
            func.num_of_control_types(types)

        return types


    def num_of_local_variables(self):
        variables = {}

        for func in self.functions:
            func.num_of_local_variables(variables)

        return variables

    def count_of_control_blocks(self):
        count = 0

        for func in self.functions:
            count += len(func.seq_of_control_types())

        return count