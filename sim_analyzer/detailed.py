import sys
from analyzer_base import Analyzer
from config_container import Config
from libs.munkres import Munkres, print_matrix, make_cost_matrix
from logger import Logger

class DetailedAnalyzer(Analyzer):

    def sim_functions(self, func1, func2):

        # control types
        ctrl_type_sim = self._simimilarity_dicts(
            func1.num_of_control_types(),
            func2.num_of_control_types()
        )

        # argument types
        args_vars_sim = self._simimilarity_dicts(
            func1.num_of_arguments_variables(),
            func2.num_of_arguments_variables()
        )

        # local variables
        loc_vars_sim = self._simimilarity_dicts(
            func1.num_of_local_variables(),
            func2.num_of_local_variables()
        )

        # control sequence
        ctrl_seq_sim = self._simimilarity_lists(
            func1.seq_of_control_types(),
            func2.seq_of_control_types()
        )

        # return type
        ret_type_sim = 1 if func1.ret_type.code() == func2.ret_type.code() else 0



        sim = Config.get('detailed.ctrl_type_power') * ctrl_type_sim
        sim += Config.get('detailed.ctrl_seq_power') * ctrl_seq_sim
        sim += Config.get('detailed.loc_vars_power') * loc_vars_sim
        sim += Config.get('detailed.ret_type_power') * ret_type_sim
        sim += Config.get('detailed.args_vars_power') * args_vars_sim

        Logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        Logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        Logger.info("ctrl_seq_sim = %f" % (ctrl_seq_sim))
        Logger.info("loc_vars_sim = %f" % (loc_vars_sim))
        Logger.info("ret_type_sim = %f" % (ret_type_sim))
        Logger.info("args_vars_sim = %f" % (args_vars_sim))
        Logger.info("detailed.sim_functions(%s, %s) = %f" % (func1.name, func2.name, sim))

        return sim

    def sim_programs(self, prog1, prog2):
        # headers
        headers_sim = self._simimilarity_dicts(
            prog1.num_of_headers(),
            prog2.num_of_headers()
        )

        # global variable
        glob_vars_sim = self._simimilarity_dicts(
            prog1.num_of_global_variables(),
            prog2.num_of_global_variables()
        )

        # function similiar
        precision = 10000
        matrix = []
        for i in range(0, len(prog1.functions)):
            matrix.append(range(len(prog2.functions)))
            for j in range(0, len(prog2.functions)):
                matrix[i][j] = self.sim_functions(prog1.functions[i], prog2.functions[j]) * precision

        cost_matrix = make_cost_matrix(matrix, lambda cost: sys.maxint - cost)
        m = Munkres()
        indexes = m.compute(cost_matrix)
        score = 1.0 / (prog1.count_of_control_blocks() + prog2.count_of_control_blocks())
        funcs_sim = 0
        for i,j in indexes:
            value = matrix[i][j]
            funcs_sim += (value / precision) * \
                ((len(prog1.functions[i].seq_of_control_types()) + len(prog2.functions[j].seq_of_control_types()))* score)
        #funcs_sim /= max(len(prog1.functions), len(prog2.functions))


        sim = Config.get('detailed.glob_vars_power') * glob_vars_sim
        sim += Config.get('detailed.headers_power') * headers_sim
        sim += Config.get('detailed.funcs_power') * funcs_sim

        Logger.info("headers_sim = %f" % headers_sim)
        Logger.info("glob_vars_sim = %f" % glob_vars_sim)
        Logger.info("funcs_sim = %f" % funcs_sim)
        Logger.info("detailed.sim_programs(%s, %s) = %f" % (prog1.name, prog1.name, sim))

        return sim