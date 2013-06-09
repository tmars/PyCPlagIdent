#coding=utf8
import sys, os, getopt
import sc.parser as sc_parser
from sim_analyzer.detailed import DetailedAnalyzer
from sim_analyzer.fast import FastAnalyzer
from detector import PlagiarismDetector

#####################################

find_funcs = False
find_progs = False
save_program = False

output = False
out_dir = 'out'

in_dir = None
target_progs = None

db_clear= False
db_info = False

#####################################

def usage():
    print u"""
Возможные параметры:
[-h|--help] - вызов справки
[-m] - режим поиска плагиата [f|p|a]:
    f - поиск схожих функций
    p - поиск схожих программ
    b - поиск сходих функций и программ
[-s] - флаг для сохранения найденных программ в базе данных
[-o] - флаг для выгрузки найденных схожих исходных кодов в папку %s'
[-i [dir]] - установка папки, для поиска исходных кодов (поиск в папке с_files/[dir])
[--db-info] - информация о базе данных
[--db-clear] - удаление всех имеющихся в базе данных программ
""" % out_dir

#####################################

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:om:sh', ['db-clear', 'db-info', 'help'])
except:
    print u'Неверные параметры'
    usage()
    sys.exit(0)

for opt,arg in opts:
    if opt == '-m':
        if arg == 'f':
            find_funcs = True
        elif arg == 'p':
            find_progs = True
        elif arg == 'b':
            find_funcs = True
            find_progs = True
        else:
            print u'Неправильный режим -m=[f|p|a]'

    elif opt == '-s':
        save_program = True

    elif opt == '-o':
        output = True

    elif opt == '-i':
        in_dir  = 'c_files/' + arg
        if os.path.exists(in_dir) == False:
            print u'Невозможно открыть папку [%s] с исходными кодами программ.' % in_dir
            sys.exit(0)

        else:
            print u'Поиск исходных текстов в папке [%s]...' % in_dir
            target_progs = sc_parser.scan_for_programs(in_dir)
            print u'Найдено %d программ.\r\n' % (len(target_progs))

    elif opt == '--db-clear':
        db_clear = True

    elif opt == '--db-info':
        db_info = True

    elif opt in ('-h', '--help'):
        usage()
        sys.exit(0)

#####################################

fast_analizer = FastAnalyzer()
detailed_analizer = DetailedAnalyzer()
detector = PlagiarismDetector(0.5, 0.8, fast_analizer, detailed_analizer)

#####################################

if find_progs and target_progs:
    print u'Поиск схожих программ:'

    for target in target_progs:
        print u'Поиск для программы [%s]...' % target.name
        data = detector.find_sim_progs(target)

        if data:
            print u'Схожые программы:'
            for prog,fast,detail in data:
                print u'Программа [%s], схожесть = %.2f.' % (prog.name, detail)

            if output:
                print detector.extract_programs(target, data, out_dir)
        else:
            print u'Не найдено.'
        print ''
    print u'Завершено.\r\n'

if find_funcs and target_progs:
    print u'Поиск схожих функций:'


    for target_prog in target_progs:
        for target in target_prog.functions:

            print u'Поиск для функции [%s][%s]...' % (target_prog.name, target.name)
            data = detector.find_sim_funcs(target)
            if data:

                print u'Схожие функции:'
                for prog,func,fast,detail in data:
                    print u'Функция [%s][%s], схожесть = %.2f.' % (prog.name, func.name, detail)

                if output:
                    print detector.extract_functions(target_prog, target, data, out_dir)
            else:
                print u'Не найдено.'
            print ''
    print u'Завершено.\r\n'

if save_program and target_progs:
    print u'Сохранение программ в базе данных...'
    detector.save_progs(target_progs)
    print u'Завершено.\r\n'

if db_clear:
    print u'Опустошение базы данных...'
    detector.clear()
    print u'Завершено.\r\n'

if db_info:
    print u'Информация о базе данных:'
    print detector.info()
    print u'Завершено.\r\n'
