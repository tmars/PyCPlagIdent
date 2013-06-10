#coding=utf8
import sys, os, getopt
from sc.parser import SCParser
from sim_analyzer.detailed import DetailedAnalyzer
from sim_analyzer.fast import FastAnalyzer
from detector import PlagiarismDetector
from logger import Logger
from repository import Repository

#####################################

find_funcs = False
find_progs = False
save_program = False

output = False
out_dir = 'out'
in_dir_prefix = 'c_files/'

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
        in_dir  = in_dir_prefix + arg
        if os.path.exists(in_dir) == False:
            print u'Невозможно открыть папку [%s] с исходными кодами программ.' % in_dir
            sys.exit(0)

        else:
            print u'Поиск исходных текстов в папке [%s]...' % in_dir
            target_progs = SCParser.scan_for_programs(in_dir, in_dir_prefix)
            print u'Найдено %d программ.\r\n' % (len(target_progs))

    elif opt == '--db-clear':
        db_clear = True

    elif opt == '--db-info':
        db_info = True

    elif opt in ('-h', '--help'):
        usage()
        sys.exit(0)

#####################################

logger = Logger('data/log.log')

fast_analizer = FastAnalyzer()
fast_analizer.set_logger(logger)

detailed_analizer = DetailedAnalyzer()
detailed_analizer.set_logger(logger)

repo = Repository('data/db.db')
detector = PlagiarismDetector(fast_analizer, detailed_analizer, repo)
detector.set_logger(logger)
detector.set_minimal_sim_values(0.5, 0.8)

#####################################
sim_progs = []
if find_progs and target_progs:
    print u'Поиск схожих программ:'

    for target in target_progs:
        print u'Поиск для программы [%s]...' % target.get_name()
        data = detector.find_sim_programs(target)

        if data:
            print u'Схожие программы:'
            for prog,fast,detail in data:
                print u'Программа [%s], схожесть = %.2f.' % (prog.get_name(), detail)
                sim_progs.append({
                    'p1': target.get_name(),
                    'p2': prog.get_name(),
                    'sim': detail,
                })

            if output:
                print detector.extract_programs(target, data, out_dir)
        else:
            print u'Не найдено.'
        print ''
    print u'Завершено.\r\n'

sim_funcs = []
if find_funcs and target_progs:
    print u'Поиск схожих функций:'

    for target_prog in target_progs:
        for target in target_prog.get_functions():

            print u'Поиск для функции [%s][%s]...' % (target_prog.get_name(), target.get_name())
            data = detector.find_sim_functions(target)
            if data:

                print u'Схожие функции:'
                for func,fast,detail in data:
                    print u'Функция [%s][%s], схожесть = %.2f.' % (func.get_program().get_name(), func.get_name(), detail)
                sim_funcs.append({
                    'p1': target.get_program().get_name(),
                    'f1': target.get_name(),
                    'p2': func.get_program().get_name(),
                    'f2': func.get_name(),
                    'sim': detail,
                })

                if output:
                    print detector.extract_functions(target, data, out_dir)
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

if find_progs or find_funcs:
    print u'Вывод:'
    if sim_progs or sim_funcs:
        if sim_progs:
            print u'Схожие программы:'
            for d in sim_progs:
                print u'[%s] и [%s] на %.2f%%' % (d['p1'], d['p2'], d['sim'] * 100)
        print u''

        if sim_funcs:
            print u'Схожие функции:'
            for d in sim_funcs:
                print u'[%s][%s] и [%s][%s] на %.2f%%' % (d['p1'], d['f1'], d['p2'], d['f2'], d['sim'] * 100)
        print u''

    else:
        print u'Сходств не обнаружено'
    print u'Завершено.\r\n'
