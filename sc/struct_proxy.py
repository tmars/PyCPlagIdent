from struct_interface import FunctionBase, ProgramBase

class FunctionProxy(FunctionBase):

    def __init__(self, _id, prog_id, name, ret_type, num_of_arguments_variables, num_of_control_types, seq_of_control_types, num_of_local_variables):
        self.id = _id
        self.prog_id = prog_id
        self.name = name
        self.ret_type = ret_type
        self.__num_of_args = num_of_arguments_variables
        self.__num_of_loc_vars = num_of_local_variables
        self.__num_of_ctrl_types = num_of_control_types
        self.__seq_of_ctrl_types = seq_of_control_types

    def name(self):
        return self.name

    def ret_type(self):
        return self.ret_type

    def num_of_control_types(self):
        return self.__num_of_ctrl_types

    def seq_of_control_types(self):
        return self.__seq_of_ctrl_types

    def num_of_local_variables(self):
        return self.__num_of_loc_vars

    def num_of_arguments_variables(self):
        return self.__num_of_args

class ProgramProxy(ProgramBase):
    def __init__(self, _id, name, source_code, num_of_headers, num_of_global_variables, num_of_control_types, num_of_local_variables, count_of_control_blocks):
        self.id = _id
        self.name = name
        self.source_code = source_code
        self.functions = []
        self.__num_of_headers = num_of_headers
        self.__num_of_glob_vars = num_of_global_variables
        self.__num_of_ctrl_types = num_of_control_types
        self.__num_of_loc_vars = num_of_local_variables
        self.__num_of_ctrls = count_of_control_blocks

    def name(self):
        return self.name

    def source_code(self):
        return self.source_code

    def functions(self):
        return self.functions

    def num_of_headers(self):
        return self.__num_of_headers

    def num_of_global_variables(self):
        return self.__num_of_glob_vars

    def num_of_control_types(self):
        return self.__num_of_ctrl_types

    def num_of_local_variables(self):
        return self.__num_of_loc_vars

    def count_of_control_blocks(self):
        return self.__num_of_ctrls
