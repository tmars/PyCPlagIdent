import time, os
from config_container import Config
from sc.extractor import SCExtractor
from sc.decorator import SCFileDecorator

class PlagiarismDetector(object):
    def __init__(self, fast_analyzer, detailed_analyzer, repo):
        self.__fast_analyzer = fast_analyzer
        self.__fast_min_sim = 0.5

        self.__detailed_analyzer = detailed_analyzer
        self.__detailed_min_sim = 0.8

        self.__logger = None

        self.__repo = repo
        self.__prog_canditates = self.__repo.get_programs()
        self.__func_canditates = self.__repo.get_functions()

    def __extracted_program(self, prog):
        text = SCExtractor.extract_program(prog.source_code)
        return text

    def __extracted_function(self, prog, func):
        text = SCExtractor.extract_function(prog.source_code, func.name)
        return text

    def set_logger(self, logger):
        self.__logger = logger

    def set_minimal_sim_values(self, fast_min_sim, detailed_min_sim):
        self.__fast_min_sim = fast_min_sim
        self.__detailed_min_sim = detailed_min_sim

    def __select_result(self, canditates, target, sim_func, min_sim_value = 0.8):
        result = []

        for obj in canditates:
            sim = sim_func(obj, target)

            self.__logger.info("sim %s([%s], [%s]) = %f" % (type(obj), obj.name, target.name, sim))

            if sim > min_sim_value:
                result.append(obj)

        return result

    #return [(prog, func, fast_similiraty, detailed_similiraty)]
    def find_sim_funcs(self, target):
        canditates = self.__func_canditates

        start = time.time()
        primary = self.__select_result(canditates, target, self.__fast_analyzer.sim_functions, self.__fast_min_sim)
        self.__logger.info("fast analyze from %d functions for %f detaileds" % (len(canditates), time.time() - start))

        start = time.time()
        result = self.__select_result(primary, target, self.__detailed_analyzer.sim_functions, self.__detailed_min_sim)
        self.__logger.info("detailed analyze from %d functions for %f detaileds" % (len(primary), time.time() - start))

        ret = []
        for func in result:
            prog = self.__repo.get_program(func.prog_id)
            fast = self.__fast_analyzer.sim_functions(func, target)
            detailed = self.__detailed_analyzer.sim_functions(func, target)
            ret.append((prog, func, fast, detailed))

        return ret

    #return [(prog, fast_similiraty, detailed_similiraty)]
    def find_sim_progs(self, target):
        canditates = self.__prog_canditates

        start = time.time()
        primary = self.__select_result(canditates, target, self.__fast_analyzer.sim_programs, self.__fast_min_sim)
        self.__logger.info("fast analyze from %d programs for %f detaileds" % (len(canditates), time.time() - start))

        for prog in primary:
            prog.functions = self.__repo.get_functions(prog.id)

        start = time.time()
        result = self.__select_result(primary, target, self.__detailed_analyzer.sim_programs, self.__detailed_min_sim)
        self.__logger.info("detailed analyze from %d programs for %f detaileds" % (len(primary), time.time() - start))

        ret = []
        for prog in result:
            fast = self.__fast_analyzer.sim_programs(prog, target)
            detailed = self.__detailed_analyzer.sim_programs(prog, target)
            ret.append((prog, fast, detailed))

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

        src = SCFileDecorator(filename_src)
        src.write_comment(["generated with %s %s" % (Config.get('package'), Config.get('version'))])
        src.write_comment(["source code of", "target program=%s" % (target.name)])
        src.write(self.__extracted_program(target))
        src.write_comment(["end of source code"])
        del src

        src = SCFileDecorator(filename_sim)
        src.write_comment(["generated with %s %s" % (Config.get('package'), Config.get('version'))])
        src.write_comment(["source code of", "similar programs"])

        for prog,f,s in data:
            src.write_comment([
                "program=%s" % (target.name),
                "f.sim=%f" % (f),
                "s.sim=%f" % (s),
            ])
            src.write(self.__extracted_program(prog))
            src.write_comment(["end of program=%s" % (prog.name)])

        del src

    def extract_functions(self, target_prog, target, data, out_dir):
        out_dir += "/%s/funcs/%s" % (target_prog.name, target.name)
        if not os.path.exists(out_dir):
            os.makedirs(out_dir)

        filename_src = "%s/src.c" % (out_dir)
        filename_sim = "%s/sim.c" % (out_dir)

        src = SCFileDecorator(filename_src)
        src.write_comment(["generated with %s %s" % (Config.get('package'), Config.get('version'))])
        src.write_comment(["source code of", "target function=%s" % (target.name)])
        src.write(self.__extracted_function(target_prog, target))
        src.write_comment(["end of source code"])
        del src

        src = SCFileDecorator(filename_sim)
        src.write_comment(["generated with %s %s" % (Config.get('package'), Config.get('version'))])
        src.write_comment(["source code of", "similar functions"])

        for prog,func,f,s in data:
            src.write_comment([
                "program=%s" % (prog.name),
                "function=%s" % (func.name),
                "f.sim=%f" % (f),
                "s.sim=%f" % (s)
            ])
            src.write(self.__extracted_function(prog, func))
            src.write_comment(["end of function=%s" % (func.name)])

        del src