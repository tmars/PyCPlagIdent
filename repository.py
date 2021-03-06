#coding=utf8
import sqlite3, os
import cPickle
from sc.struct_proxy import *

class Repository(object):

    def __init__(self, db_path):
        self.db_path = db_path

        if not os.path.exists(self.db_path):
            self.__conn = sqlite3.connect(self.db_path)
            self.__deploy()
        else:
            self.__conn = sqlite3.connect(self.db_path)

        self.__conn.text_factory = str

    def __del__(self):
        self.__conn.close()

    def __unpack_prog_data(self, data):
        return ProgramProxy(
            _id = data[0],
            name = data[1],
            source_code = data[2],
            count_of_control_blocks = data[3],
            num_of_headers = cPickle.loads(str(data[4])),
            num_of_control_types = cPickle.loads(str(data[5])),
            num_of_global_variables = cPickle.loads(str(data[6])),
            num_of_local_variables = cPickle.loads(str(data[7])),
        )

    def __deploy(self):

        c = self.__conn.cursor()

        # programs
        c.execute('''CREATE TABLE program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            source_code TEXT,
            added_date INTEGER,
            count_of_control_blocks INTEGER,
            num_of_headers TEXT,
            num_of_control_types TEXT,
            num_of_global_variables TEXT,
            num_of_local_variables TEXT
        )''')
        self.__conn.commit()

         # functions
        c.execute("CREATE TABLE function (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            program_id INTEGER,\
            name TEXT,\
            ret_type TEXT,\
            num_of_local_variables TEXT,\
            num_of_arguments_variables TEXT,\
            seq_of_control_types TEXT,\
            num_of_control_types TEXT,\
            FOREIGN KEY(program_id) REFERENCES program(id)\
        )")

        self.__conn.commit()

    def clear(self):
        if os.path.exists(self.db_path):
            print self.db_path
            self.__conn.close()
            os.remove(self.db_path)
            self.__conn = sqlite3.connect(self.db_path)
            self.__deploy()

    def info(self):
        c = self.__conn.cursor()

        prog_count = c.execute('''SELECT COUNT(id) FROM program''').fetchone()[0]
        func_count =c.execute('''SELECT COUNT(id) FROM function''').fetchone()[0]

        return u'В базе данных сохранено:\r\n\t - программ %d\r\n\t - функций %d' %(prog_count, func_count)

    def insert_program(self, program):
        c = self.__conn.cursor()
        c.execute('''INSERT INTO program (
            name,
            source_code,
            count_of_control_blocks,
            num_of_headers,
            num_of_control_types,
            num_of_global_variables,
            num_of_local_variables
        ) VALUES (?,?,?,?,?,?,?)''', (
            program.name,
            program.source_code,
            program.count_of_control_blocks(),
            cPickle.dumps(program.num_of_headers()),
            cPickle.dumps(program.num_of_control_types()),
            cPickle.dumps(program.num_of_global_variables()),
            cPickle.dumps(program.num_of_local_variables())
        ))

        functions = []
        for function in program.functions:
            functions.append((
                c.lastrowid,
                function.name,
                cPickle.dumps(function.ret_type),
                cPickle.dumps(function.num_of_local_variables()),
                cPickle.dumps(function.num_of_arguments_variables()),
                cPickle.dumps(function.seq_of_control_types()),
                cPickle.dumps(function.num_of_control_types()),
            ))
        c.executemany('''INSERT INTO function (
            program_id,
            name,
            ret_type,
            num_of_local_variables,
            num_of_arguments_variables,
            seq_of_control_types,
            num_of_control_types
        ) VALUES (?,?,?,?,?,?,?)''', functions)

        self.__conn.commit()

    def get_program(self, prog_id):
        c = self.__conn.cursor()

        c.execute('''SELECT
            id,
            name,
            source_code,
            count_of_control_blocks,
            num_of_headers,
            num_of_control_types,
            num_of_global_variables,
            num_of_local_variables FROM program WHERE id = ?''', (prog_id,)
        )

        return self.__unpack_prog_data(c.fetchone())

    def get_programs(self):
        c = self.__conn.cursor()

        c.execute('''SELECT
            id,
            name,
            source_code,
            count_of_control_blocks,
            num_of_headers,
            num_of_control_types,
            num_of_global_variables,
            num_of_local_variables FROM program'''
        )

        programs = []
        for data in c.fetchall():
            programs.append(self.__unpack_prog_data(data))

        return programs

    def get_functions(self, prog_id = None):
        c = self.__conn.cursor()

        if (prog_id):
            c.execute('''SELECT
                id,
                program_id,
                name,
                ret_type,
                num_of_local_variables,
                num_of_arguments_variables,
                seq_of_control_types,
                num_of_control_types FROM function WHERE program_id = ?''', (prog_id,)
            )
        else:
            c.execute('''SELECT
                id,
                program_id,
                name,
                ret_type,
                num_of_local_variables,
                num_of_arguments_variables,
                seq_of_control_types,
                num_of_control_types FROM function'''
            )

        functions = []
        for data in c.fetchall():
            functions.append(FunctionProxy(
                _id = data[0],
                prog_id = data[1],
                name = data[2],
                ret_type = cPickle.loads(str(data[3])),
                num_of_local_variables = cPickle.loads(str(data[4])),
                num_of_arguments_variables = cPickle.loads(str(data[5])),
                seq_of_control_types = cPickle.loads(str(data[6])),
                num_of_control_types = cPickle.loads(str(data[7])),
            ))
        return functions