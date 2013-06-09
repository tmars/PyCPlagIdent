#coding=utf8

class SCFileDecorator(object):

    def __init__(self, filename, width = 60):
        self.__w = width
        self.__file = open(filename, 'w')

    def __del__(self):
        self.__file.close()
    def write_comment(self, strings):
        self.__file.write("/*" + ("*" * self.__w) + "*/\n")

        for string in strings:
            self.__file.write("/*" + string.center(self.__w, ' ') + "*/\n")

        self.__file.write("/*" + ("*" * self.__w) + "*/\n")
        self.__file.write("\n")

    def write(self, string):
        self.__file.write(string)
