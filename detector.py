import time, os
from config_container import Config
from repository import Repository
from logger import Logger
from sc.extractor import SCExtractor

width = 60

class PlagiarismDetector(object):
    def __init__(self, fast_min_sim, detailed_min_sim, first_analyzer, second_analyzer):
        self.__fast_min_sim = fast_min_sim
        self.__first_analyzer = first_analyzer
        self.__second_analyzer = second_analyzer
        self.__detailed_min_sim = detailed_min_sim
        self.__repo = Repository()
        self.__prog_canditates = None
        self.__prog_canditates = self.__repo.get_programs()
        self.__func_canditates = self.__repo.get_functions()

    def __write_comment(self, fil, strings):
        fil.write("/*" + ("*" * width) + "*/\n")
        for string in strings:
            fil.write("/*" + string.center(width, ' ') + "*/\n")
        fil.write("/*" + ("*" * width) + "*/\n")
        fil.write("\n")

    def __open_file(self, filename):
        fil = open(filename, 'w')
        fil.write("/*" + ("*" * width) + "*/\n")
        fil.write("/*" + ("generated with plag_detector V" + Config.get("version")).center(width, ' ') + "*/\n")
        fil.write("/*" + ("*" * width) + "*/\n")
        fil.write("\n")

        return fil

    def __extracted_program(self, prog):
        text = SCExtractor.extract_program(prog.source_code)
        return text

    def __extracted_function(self, prog, func):
        text = SCExtractor.extract_function(prog.source_code, func.name)
        return text

    def select_result(self, canditates, target, sim_func, min_sim_value = 0.8):
        result = []

        for obj in canditates:
            sim = sim_func(obj, target)

            Logger.info("sim %s([%s], [%s]) = %f" % (type(obj), obj.name, target.name, sim))

            if sim > min_sim_value:
                result.append(obj)

        return result

    #return [(prog, func, first_similiraty, second_similiraty)]
    def find_sim_funcs(self, target):
        canditates = self.__func_canditates

        start = time.time()
        primary = self.select_result(canditates, target, self.__first_analyzer.sim_functions, self.__fast_min_sim)
        Logger.info("fast analyze from %d functions for %f seconds" % (len(canditates), time.time() - start))

        start = time.time()
        result = self.select_result(primary, target, self.__second_analyzer.sim_functions, self.__detailed_min_sim)
        Logger.info("detailed analyze from %d functions for %f seconds" % (len(primary), time.time() - start))

        ret = []
        for func in result:
            prog = self.__repo.get_program(func.prog_id)
            first = self.__first_analyzer.sim_functions(func, target)
            second = self.__second_analyzer.sim_functions(func, target)
            ret.append((prog, func, first, second))

        return ret

    #return [(prog, first_similiraty, second_similiraty)]
    def find_sim_progs(self, target):
        canditates = self.__prog_canditates

        start = time.time()
        primary = self.select_result(canditates, target, self.__first_analyzer.sim_programs, self.__fast_min_sim)
        Logger.info("fast analyze from %d programs for %f seconds" % (len(canditates), time.time() - start))

        for prog in primary:
            prog.functions = self.__repo.get_functions(prog.id)

        start = time.time()
        result = self.select_result(primary, target, self.__second_analyzer.sim_programs, self.__detailed_min_sim)
        Logger.info("detailed analyze from %d programs for %f seconds" % (len(primary), time.time() - start))

        ret = []
        for prog in result:
            first = self.__first_analyzer.sim_programs(prog, target)
            second = self.__second_analyzer.sim_programs(prog, target)
            ret.append((prog, first, second))

        return ret

    def save_progs(self, progs):
        for prog in progs:
            self.__repo.insert_program(prog)

    def clear(self):
        return self.__repo.clear()

    def info(self):
        return self.__repo.info()

    def extract_programs(self, target, data, out_dir):
        out_dir += "/" + target.name
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        filename_src = "%s/src.c" %(out_dir)
        filename_sim = "%s/sim.c" %(out_dir)

        fil = self.__open_file(filename_src)
        self.__write_comment(fil, ["source code of", "target program=%s" % (target.name)])
        fil.write(self.__extracted_program(target))
        self.__write_comment(fil, ["end of source code"])

        fil = self.__open_file(filename_sim)
        self.__write_comment(fil, ["source code of", "similar programs"])

        for prog,f,s in data:
            self.__write_comment(fil, [
                "program=%s" % (target.name),
                "f.sim=%f" % (f),
                "s.sim=%f" % (s),
            ])
            fil.write(self.__extracted_program(prog))
            self.__write_comment(fil, ["end of program=%s" % (prog.name)])

        fil.close()

    def extract_functions(self, target_prog, target, data, out_dir):
        out_dir += "/%s/funcs/%s" % (target_prog.name, target.name)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        filename_src = "%s/src.c" % (out_dir)
        filename_sim = "%s/sim.c" % (out_dir)

        fil = self.__open_file(filename_src)
        self.__write_comment(fil, ["source code of", "target function=%s" % (target.name)])
        fil.write(self.__extracted_function(target_prog, target))
        self.__write_comment(fil, ["end of source code"])

        fil = self.__open_file(filename_sim)
        self.__write_comment(fil, ["source code of", "similar functions"])

        for prog,func,f,s in data:
            self.__write_comment(fil, [
                "program=%s" % (prog.name),
                "function=%s" % (func.name),
                "f.sim=%f" % (f),
                "s.sim=%f" % (s)
            ])
            fil.write(self.__extracted_function(prog, func))
            self.__write_comment(fil, ["end of function=%s" % (func.name)])

        fil.close()