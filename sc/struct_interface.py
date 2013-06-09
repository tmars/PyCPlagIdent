#coding=utf8

from abc import ABCMeta, abstractmethod, abstractproperty


class FunctionBase(object):
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """ Название функции """

    @abstractproperty
    def ret_type(self):
        """ Тип возврата """

    @abstractmethod
    def num_of_control_types(self):
        """ Количество блоков каждого типа управления """

    @abstractmethod
    def seq_of_control_types(self):
        """ Последовательность кодов типов управления как в программе """

    @abstractmethod
    def num_of_local_variables(self):
        """ Количество локальных переменных по типам """

    @abstractmethod
    def num_of_arguments_variables(self):
        """ Количество аргументов по типам """

class ProgramBase():
    __metaclass__ = ABCMeta

    @abstractproperty
    def name(self):
        """ Название программы """

    @abstractproperty
    def source_code(self):
        """ Исходный код программы """

    @abstractproperty
    def functions(self):
        """ Функции в программе """

    @abstractmethod
    def num_of_headers(self):
        """ Присутствие стандартных хедеровпо названию """

    @abstractmethod
    def num_of_global_variables(self):
        """ Количество глобальных переменных по типам """

    @abstractmethod
    def num_of_control_types(self):
        """ Количество блоков каждого типа управления """

    @abstractmethod
    def num_of_local_variables(self):
        """ Количество локальных переменных по типам """

    @abstractmethod
    def count_of_control_blocks(self):
        """ Количество всего контрольных блоков"""
