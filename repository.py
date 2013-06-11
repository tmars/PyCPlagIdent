#coding=utf8
import sqlite3, os
import cPickle
from sc.struct_proxy import FunctionProxy, ProgramProxy

class Repository(object):

    def __init__(self, db_path):
        self.db_path = db_path

        if not os.path.exists(self.db_path):
            print "deploy"
            self.__conn = sqlite3.connect(self.db_path)
            self.__deploy()
        else:
            self.__conn = sqlite3.connect(self.db_path)

        self.__conn.text_factory = str
        self.__functions = {}
        self.__programs = {}

    def __del__(self):
        self.__conn.close()

    def __unpack_prog_data(self, data):
        program = ProgramProxy(data[0])
        program.set_name(data[1])
        program.set_source_code(data[2])
        program.set_count_of_controls(data[3])
        program.set_numbers_of_headers(cPickle.loads(str(data[4])))
        program.set_numbers_of_controls(cPickle.loads(str(data[5])))
        program.set_numbers_of_global_vars(cPickle.loads(str(data[6])))
        program.set_numbers_of_local_vars(cPickle.loads(str(data[7])))
        return program

    def __deploy(self):
        c = self.__conn.cursor()
        # programs
        c.execute('''CREATE TABLE program (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            source_code TEXT,
            added_date INTEGER,
            count_of_controls INTEGER,
            numbers_of_headers TEXT,
            numbers_of_controls TEXT,
            numbers_of_global_vars TEXT,
            numbers_of_local_vars TEXT
        )''')
        self.__conn.commit()

         # functions
        c.execute("CREATE TABLE function (\
            id INTEGER PRIMARY KEY AUTOINCREMENT,\
            program_id INTEGER,\
            name TEXT,\
            ret_type TEXT,\
            numbers_of_local_vars TEXT,\
            numbers_of_arguments TEXT,\
            sequence_of_controls TEXT,\
            numbers_of_controls TEXT,\
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
            count_of_controls,
            numbers_of_headers,
            numbers_of_controls,
            numbers_of_global_vars,
            numbers_of_local_vars
        ) VALUES (?,?,?,?,?,?,?)''', (
            program.get_name(),
            program.get_source_code(),
            program.get_count_of_controls(),
            cPickle.dumps(program.get_numbers_of_headers()),
            cPickle.dumps(program.get_numbers_of_controls()),
            cPickle.dumps(program.get_numbers_of_global_vars()),
            cPickle.dumps(program.get_numbers_of_local_vars())
        ))

        functions = []
        for function in program.get_functions():
            functions.append((
                c.lastrowid,
                function.get_name(),
                cPickle.dumps(function.get_return_type()),
                cPickle.dumps(function.get_numbers_of_local_vars()),
                cPickle.dumps(function.get_numbers_of_arguments()),
                cPickle.dumps(function.get_sequence_of_controls()),
                cPickle.dumps(function.get_numbers_of_controls()),
            ))
        c.executemany('''INSERT INTO function (
            program_id,
            name,
            ret_type,
            numbers_of_local_vars,
            numbers_of_arguments,
            sequence_of_controls,
            numbers_of_controls
        ) VALUES (?,?,?,?,?,?,?)''', functions)

        self.__conn.commit()

    def get_program(self, prog_id):
        if self.__programs.has_key(prog_id):
            program = self.__programs[prog_id]
        else:
            c = self.__conn.cursor()
            c.execute('''SELECT
                id,
                name,
                source_code,
                count_of_controls,
                numbers_of_headers,
                numbers_of_controls,
                numbers_of_global_vars,
                numbers_of_local_vars FROM program WHERE id = ?''', (prog_id,)
            )
            program = self.__unpack_prog_data(c.fetchone())
            self.__programs[program.get_id()] = program

        return program

    def get_programs(self):
        c = self.__conn.cursor()

        c.execute('''SELECT
            id,
            name,
            source_code,
            count_of_controls,
            numbers_of_headers,
            numbers_of_controls,
            numbers_of_global_vars,
            numbers_of_local_vars FROM program'''
        )

        programs = []
        for data in c.fetchall():
            if self.__programs.has_key(data[0]):
                program = self.__programs[data[0]]
            else:
                program = self.__unpack_prog_data(data)
                self.__programs[program.get_id()] = program
            programs.append(program)

        return programs

    def get_functions(self, prog_id = None):
        c = self.__conn.cursor()

        if (prog_id):
            c.execute('''SELECT
                id,
                program_id,
                name,
                ret_type,
                numbers_of_local_vars,
                numbers_of_arguments,
                sequence_of_controls,
                numbers_of_controls FROM function WHERE program_id = ?''', (prog_id,)
            )
        else:
            c.execute('''SELECT
                id,
                program_id,
                name,
                ret_type,
                numbers_of_local_vars,
                numbers_of_arguments,
                sequence_of_controls,
                numbers_of_controls FROM function'''
            )

        functions = []
        for data in c.fetchall():
            if self.__functions.has_key(data[0]):
                function = self.__functions[data[0]]
            else:
                function = FunctionProxy(_id = data[0])
                #function.set_program(self.get_program(data[1]))
                function.set_name(data[2])
                function.set_return_type(cPickle.loads(str(data[3])))
                function.set_numbers_of_local_vars(cPickle.loads(str(data[4])))
                function.set_numbers_of_arguments(cPickle.loads(str(data[5])))
                function.set_sequence_of_controls(cPickle.loads(str(data[6])))
                function.set_numbers_of_controls(cPickle.loads(str(data[7])))
                self.__functions[function.get_id()] = function

            functions.append(function)
        return functions