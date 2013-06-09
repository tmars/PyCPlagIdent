import ConfigParser, os
from libs.singleton import Singleton

config_filename = 'config/config.ini'
#include_dir = 'include'
include_dir = 'libs/pycparser/utils/fake_libc_include'
error_log = '/data/log.dat'

@Singleton
class ConfigCont(object):
    def scan_header(self, directory, headers = [], prefix = ''):
        for name in os.listdir(directory):
            fullname = os.path.join(directory, name)
            if os.path.isfile(fullname):
                headers.append(prefix + name)
            elif os.path.isdir(fullname):
                self.scan_header(fullname, headers, name + '/')

        return headers

    def __init__(self):
        self._container = {}

        config = ConfigParser.RawConfigParser()
        config.read(config_filename)

        self._container['version'] = "0.2"

        self._container['max_pointer_count'] = config.getint('DataType', 'max_pointer_count')
        self._container['max_array_count'] = config.getint('DataType', 'max_array_count')
        self._container['max_func_pointer_count'] = config.getint('DataType', 'max_func_pointer_count')

        self._container['detailed.ctrl_type_power'] = config.getfloat('Detailed.FunctionSim', 'ctrl_type_power')
        self._container['detailed.ctrl_seq_power'] = config.getfloat('Detailed.FunctionSim', 'ctrl_seq_power')
        self._container['detailed.loc_vars_power'] = config.getfloat('Detailed.FunctionSim', 'loc_vars_power')
        self._container['detailed.ret_type_power'] = config.getfloat('Detailed.FunctionSim', 'ret_type_power')
        self._container['detailed.args_vars_power'] = config.getfloat('Detailed.FunctionSim', 'args_vars_power')

        self._container['detailed.glob_vars_power'] = config.getfloat('Detailed.ProgramSim', 'glob_vars_power')
        self._container['detailed.headers_power'] = config.getfloat('Detailed.ProgramSim', 'headers_power')
        self._container['detailed.funcs_power'] = config.getfloat('Detailed.ProgramSim', 'funcs_power')

        self._container['fast.func_ctrl_type_power'] = config.getfloat('Fast.FunctionSim', 'func_ctrl_type_power')
        self._container['fast.func_loc_vars_power'] = config.getfloat('Fast.FunctionSim', 'func_loc_vars_power')

        self._container['fast.ctrl_type_power'] = config.getfloat('Fast.ProgramSim', 'ctrl_type_power')
        self._container['fast.headers_power'] = config.getfloat('Fast.ProgramSim', 'headers_power')
        self._container['fast.loc_vars_power'] = config.getfloat('Fast.ProgramSim', 'loc_vars_power')
        self._container['fast.glob_vars_power'] = config.getfloat('Fast.ProgramSim', 'glob_vars_power')

        self._container['standart_headers'] = self.scan_header(include_dir)
        self._container['include_dir'] = include_dir
        self._container['error_log'] = error_log

    def get(self, key):
        return self._container[key] if self._container.has_key(key) else None

Config = ConfigCont.Instance()