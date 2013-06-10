import sys
from analyzer_base import Analyzer
from config_container import Config
from libs.munkres import Munkres, make_cost_matrix

class DetailedAnalyzer(Analyzer):

    def sim_functions(self, func1, func2):

        # control types
        ctrl_type_sim = self._simimilarity_dicts(
            func1.get_numbers_of_controls(),
            func2.get_numbers_of_controls()
        )

        # argument types
        args_vars_sim = self._simimilarity_dicts(
            func1.get_numbers_of_arguments(),
            func2.get_numbers_of_arguments()
        )

        # local variables
        loc_vars_sim = self._simimilarity_dicts(
            func1.get_numbers_of_local_vars(),
            func2.get_numbers_of_local_vars()
        )

        # control sequence
        ctrl_seq_sim = self._simimilarity_lists(
            func1.get_sequence_of_controls(),
            func2.get_sequence_of_controls()
        )

        # return type
        ret_type_sim = 1 if func1.get_return_type().code() == func2.get_return_type().code() else 0

        sim = Config.get('detailed.ctrl_type_power') * ctrl_type_sim
        sim += Config.get('detailed.ctrl_seq_power') * ctrl_seq_sim
        sim += Config.get('detailed.loc_vars_power') * loc_vars_sim
        sim += Config.get('detailed.ret_type_power') * ret_type_sim
        sim += Config.get('detailed.args_vars_power') * args_vars_sim

        self._logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        self._logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        self._logger.info("ctrl_seq_sim = %f" % (ctrl_seq_sim))
        self._logger.info("loc_vars_sim = %f" % (loc_vars_sim))
        self._logger.info("ret_type_sim = %f" % (ret_type_sim))
        self._logger.info("args_vars_sim = %f" % (args_vars_sim))
        self._logger.info("detailed.sim_functions(%s, %s) = %f" % (func1.get_name(), func2.get_name(), sim))

        return sim

    def sim_programs(self, prog1, prog2):
        # headers
        headers_sim = self._simimilarity_dicts(
            prog1.get_numbers_of_headers(),
            prog2.get_numbers_of_headers()
        )

        # global variable
        glob_vars_sim = self._simimilarity_dicts(
            prog1.get_numbers_of_global_vars(),
            prog2.get_numbers_of_global_vars()
        )

        # function similiar
        precision = 10000
        matrix = []
        functions1 = prog1.get_functions()
        functions2 = prog2.get_functions()
        for i in range(0, len(functions1)):
            matrix.append(range(len(functions2)))
            for j in range(0, len(functions2)):
                matrix[i][j] = self.sim_functions(functions1[i], functions2[j]) * precision

        cost_matrix = make_cost_matrix(matrix, lambda cost: sys.maxint - cost)
        m = Munkres()
        indexes = m.compute(cost_matrix)
        score = 1.0 / (prog1.get_count_of_controls() + prog2.get_count_of_controls())
        funcs_sim = 0
        for i,j in indexes:
            value = matrix[i][j]
            funcs_sim += (value / precision) * \
                ((len(functions1[i].get_sequence_of_controls()) + len(functions2[j].get_sequence_of_controls()))* score)

        sim = Config.get('detailed.glob_vars_power') * glob_vars_sim
        sim += Config.get('detailed.headers_power') * headers_sim
        sim += Config.get('detailed.funcs_power') * funcs_sim

        self._logger.info("headers_sim = %f" % headers_sim)
        self._logger.info("glob_vars_sim = %f" % glob_vars_sim)
        self._logger.info("funcs_sim = %f" % funcs_sim)
        self._logger.info("detailed.sim_programs(%s, %s) = %f" % (prog1.get_name(), prog1.get_name(), sim))

        return sim