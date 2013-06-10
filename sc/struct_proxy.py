from struct import FunctionBase, ProgramBase

class FunctionProxy(FunctionBase):

    def __init__(self, _id):
        #super(FunctionProxy, self).__init__()
        self._id = _id
        self._numbers_of_controls = []
        self._sequence_of_controls = []
        self._numbers_of_arguments = []
        self._numbers_of_local_vars = []

    def get_id(self):
        return self._id

    def set_numbers_of_controls(self, numbers):
        self._numbers_of_controls = numbers

    def get_numbers_of_controls(self):
        return self._numbers_of_controls

    def set_sequence_of_controls(self, sequence):
        self._sequence_of_controls = sequence

    def get_sequence_of_controls(self):
        return self._sequence_of_controls

    def set_numbers_of_arguments(self, numbers):
        self._numbers_of_arguments = numbers

    def get_numbers_of_arguments(self):
        return self._numbers_of_arguments

    def set_numbers_of_local_vars(self, numbers):
        self._numbers_of_local_vars = numbers

    def get_numbers_of_local_vars(self):
        return self._numbers_of_local_vars

class ProgramProxy(ProgramBase):
    def __init__(self, _id):
        super(ProgramProxy, self).__init__()
        self._id = _id
        self._numbers_of_headers = []
        self._numbers_of_global_vars = []
        self._numbers_of_controls = []
        self._numbers_of_local_vars = []
        self._count_of_controls = 0

    def get_id(self):
        return self._id

    def set_numbers_of_headers(self, numbers):
        self._numbers_of_headers = numbers

    def get_numbers_of_headers(self):
        return self._numbers_of_headers

    def set_numbers_of_global_vars(self, numbers):
        self._numbers_of_global_vars = numbers

    def get_numbers_of_global_vars(self):
        return self._numbers_of_global_vars

    def set_numbers_of_controls(self, numbers):
        self._numbers_of_controls = numbers

    def get_numbers_of_controls(self):
        return self._numbers_of_controls

    def set_numbers_of_local_vars(self, numbers):
        self._numbers_of_local_vars = numbers

    def get_numbers_of_local_vars(self):
        return self._numbers_of_local_vars

    def set_count_of_controls(self, count):
        self._count_of_controls = count

    def get_count_of_controls(self):
        return self._count_of_controls
