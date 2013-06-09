#coding=utf8
import sys, os, getopt
import sc.parser as sc_parser
from sim_analyzer.detailed import DetailedAnalyzer
from sim_analyzer.fast import FastAnalyzer
from detector import PlagiarismDetector

find_funcs = False
find_progs = False
save_program = False
clear_database = False
output = False
out_dir = "out"
in_dir = 'c_files/col1'

opts, args = getopt.getopt(sys.argv[1:], 'i:om:s', ["clear-database"])

for opt,arg in opts:
    if opt == '-m':
        if arg == 'f':
            find_funcs = True
        elif arg == 'p':
            find_progs = True
        elif arg == 'a':
            find_funcs = True
            find_progs = True
        else:
            print "Error parameter -m=[f|p|a]"

    elif opt == '-s':
        save_program = True

    elif opt == '-o':
        output = True

    elif opt == '-i':
        in_dir  = 'c_files/' + arg

    elif opt == '--clear-database':
        clear_database = True

if os.path.exists(in_dir) == False:
    print "Errror get access to in_dir [%s]" % in_dir
    sys.exit(0)

print "Scaning in_dir[%s] for source code of program..." % in_dir

target_progs = sc_parser.scan_for_programs(in_dir)
print "Finded %d programs.\r\n" % (len(target_progs))

fast_analizer = FastAnalyzer()
detailed_analizer = DetailedAnalyzer()
detector = PlagiarismDetector(0.5, 0.8, fast_analizer, detailed_analizer)

if find_progs:
    print "Finding similar programs:"

    for target in target_progs:
        print "Analize program [%s]..." % target.name
        data = detector.find_sim_progs(target)

        if data:
            print "Similar programs:"

            for prog,fast,detail in data:
                print "program [%s] fast = %.2f, detail = %.2f" % (prog.name, fast, detail)

            if output:
                print detector.extract_programs(target, data, out_dir)


        else:
            print "Not found."

        print ""
    print "Done.\r\n"

if find_funcs:
    print "Finding similar functions:"

    for target_prog in target_progs:
        for target in target_prog.functions:

            print "Analize function [%s][%s]..." % (target_prog.name, target.name)
            data = detector.find_sim_funcs(target)

            if data:

                print "Similar functions:"

                for prog,func,fast,detail in data:
                    print "function [%s][%s] fast = %.2f, detail = %.2f" % (prog.name, func.name, fast, detail)

                if output:
                    print detector.extract_functions(target_prog, target, data, out_dir)

            else:
                print "Not found."
            print ""
    print "Done.\r\n"

if save_program:
    print "Saving program to base..."
    detector.save_progs(target_progs)
    print "Done.\r\n"

if clear_database:
    print "Clearing database..."
    detector.clear()
    print "Done.\r\n"
