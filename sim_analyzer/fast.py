from analyzer_base import Analyzer
from config_container import Config

class FastAnalyzer(Analyzer):

    def sim_programs(self, prog1, prog2):
        headers_sim = self._simimilarity_dicts(
            prog1.num_of_headers(),
            prog2.num_of_headers()
        )

        # control types
        ctrl_type_sim = self._simimilarity_dicts(
            prog1.num_of_control_types(),
            prog2.num_of_control_types()
        )

        # local variables
        loc_vars_sim = self._simimilarity_dicts(
            prog1.num_of_local_variables(),
            prog2.num_of_local_variables()
        )

        # global variable
        glob_vars_sim = self._simimilarity_dicts(
            prog1.num_of_global_variables(),
            prog2.num_of_global_variables()
        )

        sim = Config.get('fast.ctrl_type_power') * ctrl_type_sim
        sim += Config.get('fast.headers_power') * headers_sim
        sim += Config.get('fast.loc_vars_power') * loc_vars_sim
        sim += Config.get('fast.glob_vars_power') * glob_vars_sim

        self._logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        self._logger.info("headers_sim = %f" % (headers_sim))
        self._logger.info("loc_vars_sim = %f" % (loc_vars_sim))
        self._logger.info("glob_vars_sim = %f" % (glob_vars_sim))
        self._logger.info("fast.sim_programs(%s, %s) = %f" % (prog1.name, prog2.name, sim))

        return sim

    def sim_functions(self, func1, func2):

        # control types
        ctrl_type_sim = self._simimilarity_dicts(
            func1.num_of_control_types(),
            func2.num_of_control_types()
        )

        # local variables
        loc_vars_sim = self._simimilarity_dicts(
            func1.num_of_local_variables(),
            func2.num_of_local_variables()
        )

        # return type
        ret_type_sim = 1 if func1.ret_type.code() == func2.ret_type.code() else 0



        sim = Config.get('fast.func_ctrl_type_power') * ctrl_type_sim
        sim += Config.get('fast.func_loc_vars_power') * loc_vars_sim

        self._logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        self._logger.info("loc_vars_sim = %f" % (loc_vars_sim))
        self._logger.info("fast.sim_functions(%s, %s) = %f" % (func1.name, func2.name, sim))

        return sim