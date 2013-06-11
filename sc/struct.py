#coding=utf8
"""
Классы для хранения структуры программы
"""

import sys, inspect
from config_container import Config
from abc import ABCMeta, abstractmethod, abstractproperty

class Node(object):
    """ Базовый класс от которого наследуются все структуры программы
    """

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

class Block(Node):

    _attr_names = {
        'ControlType': 'get_control_type()',
        'LocalVariabes': 'get_local_vars()',
        'Children': 'get_children()'
    }

    def __init__(self, control_type):
        self._control_type = control_type
        self._local_vars = []
        self._children = []

    def get_control_type(self):
        return self._control_type

    def add_local_var(self, var):
        self._local_vars.append(var)

    def add_local_vars(self, vars):
        self._local_vars.extend(vars)

    def get_local_vars(self):
        return self._local_vars

    def add_child(self, child):
        if isinstance(child, list):
            self._children.extend(child)
        else:
            self._children.append(child)

    def get_children(self):
        return self._children

    def get_numbers_of_controls(self, types = None):
        types = {} if types == None else types
        control_type = self.get_control_type()
        if types.has_key(control_type):
            types[control_type] += 1
        else:
            types[control_type] = 1
        for child in self.get_children():
            child.get_numbers_of_controls(types)
        return types

    def get_sequence_of_controls(self, types = None):
        types = [] if types == None else types
        types.append(self.get_control_type())
        for child in self.get_children():
            child.get_sequence_of_controls(types)
        return types

    def get_numbers_of_local_vars(self, variables = None):
        variables = {} if variables == None else variables
        for var in self.get_local_vars():
            if variables.has_key(var.code()):
                variables[var.code()] += 1
            else:
                variables[var.code()] = 1
        for child in self.get_children():
            child.get_numbers_of_local_vars(variables)
        return variables

class FunctionBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._name = 'unknow'
        self._return_type = DataType()

    def set_program(self, program):
        pass
        #self._program = program

    def get_program(self):
        return self._program

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_return_type(self, return_type):
        self._return_type = return_type

    def get_return_type(self):
        return self._return_type

    @abstractmethod
    def get_numbers_of_controls(self):
        """ Количество блоков каждого типа управления """

    @abstractmethod
    def get_sequence_of_controls(self):
        """ Последовательность кодов типов управления как в программе """

    @abstractmethod
    def get_numbers_of_local_vars(self):
        """ Количество локальных переменных по типам """

    @abstractmethod
    def get_numbers_of_arguments(self):
        """ Количество аргументов по типам """

class ProgramBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self._name = 'unknow'
        self._source_code = ''
        self._functions = []

    def set_name(self, name):
        self._name = name

    def get_name(self):
        return self._name

    def set_source_code(self, source_code):
        self._source_code = source_code

    def get_source_code(self):
        return self._source_code

    def add_function(self, function):
        #function.set_program(self)
        self._functions.append(function)

    def get_functions(self):
        return self._functions

    @abstractmethod
    def get_numbers_of_headers(self):
        """ Присутствие стандартных хедеровпо названию """

    @abstractmethod
    def get_numbers_of_global_vars(self):
        """ Количество глобальных переменных по типам """

    @abstractmethod
    def get_numbers_of_controls(self):
        """ Количество блоков каждого типа управления """

    @abstractmethod
    def get_numbers_of_local_vars(self):
        """ Количество локальных переменных по типам """

    @abstractmethod
    def get_count_of_controls(self):
        """ Количество всего контрольных блоков"""

class Function(Node, FunctionBase):

    _attr_names = {
        'Name': 'name',
        'ReturnType': 'ret_type',
        'Arguments': 'args',
        'Block':'block'
    }

    def __init__(self, block):
        super(Function, self).__init__()
        self._program = Program()
        self._arguments = []
        self._block = block

    def add_argument(self, argument):
        self._arguments.append(argument)

    def get_arguments(self):
        return self._arguments

    def get_numbers_of_controls(self, types = None):
        return self._block.get_numbers_of_controls(types)

    def get_sequence_of_controls(self, types = None):
        return self._block.get_sequence_of_controls(types)

    def get_numbers_of_local_vars(self, variables = None):
        return self._block.get_numbers_of_local_vars(variables)

    def get_numbers_of_arguments(self, variables = None):
        variables = {} if variables == None else variables
        for var in self.get_arguments():
            if var:
                if variables.has_key(var.code()):
                    variables[var.code()] += 1
                else:
                    variables[var.code()] = 1
        return variables

    def get_count_of_controls(self):
        return len(self.get_sequence_of_controls())

class Program(Node, ProgramBase):

    _attr_names = {
        'Name': 'name',
        'GlobalVariables': 'global_variables',
        'Functions': 'functions'
    }

    def __init__(self):
        super(Program, self).__init__()
        self._headers = []
        self._global_vars = []

    def add_header(self, header):
        self._headers.append(header)

    def get_headers(self):
        return self._headers

    def add_global_var(self, var):
        self._global_vars.append(var)

    def get_global_vars(self):
        return self._global_vars

    def get_numbers_of_headers(self):
        heads = {}
        for head in self.get_headers():
            heads[head] = 1
        return heads

    def get_numbers_of_global_vars(self):
        variables = {}
        for var in self.get_global_vars():
            if variables.has_key(var.code()):
                variables[var.code()] += 1
            else:
                variables[var.code()] = 1
        return variables

    def get_numbers_of_controls(self):
        types = {}
        for func in self.get_functions():
            func.get_numbers_of_controls(types)
        return types


    def get_numbers_of_local_vars(self):
        variables = {}
        for func in self.get_functions():
            func.get_numbers_of_local_vars(variables)
        return variables

    def get_count_of_controls(self):
        count = 0
        for func in self.get_functions():
            count += len(func.get_sequence_of_controls())
        return count