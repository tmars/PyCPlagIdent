from analyzer_base import Analyzer
from config_container import Config

class FastAnalyzer(Analyzer):

    def sim_programs(self, prog1, prog2):
        headers_sim = self._simimilarity_dicts(
            prog1.get_numbers_of_headers(),
            prog2.get_numbers_of_headers()
        )

        # control types
        ctrl_type_sim = self._simimilarity_dicts(
            prog1.get_numbers_of_controls(),
            prog2.get_numbers_of_controls()
        )

        # local variables
        loc_vars_sim = self._simimilarity_dicts(
            prog1.get_numbers_of_local_vars(),
            prog2.get_numbers_of_local_vars()
        )

        # global variable
        glob_vars_sim = self._simimilarity_dicts(
            prog1.get_numbers_of_global_vars(),
            prog2.get_numbers_of_global_vars()
        )

        sim = Config.get('fast.ctrl_type_power') * ctrl_type_sim
        sim += Config.get('fast.headers_power') * headers_sim
        sim += Config.get('fast.loc_vars_power') * loc_vars_sim
        sim += Config.get('fast.glob_vars_power') * glob_vars_sim

        self._logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        self._logger.info("headers_sim = %f" % (headers_sim))
        self._logger.info("loc_vars_sim = %f" % (loc_vars_sim))
        self._logger.info("glob_vars_sim = %f" % (glob_vars_sim))
        self._logger.info("fast.sim_programs(%s, %s) = %f" % (prog1.get_name(), prog2.get_name(), sim))

        return sim

    def sim_functions(self, func1, func2):

        # control types
        ctrl_type_sim = self._simimilarity_dicts(
            func1.get_numbers_of_controls(),
            func2.get_numbers_of_controls()
        )

        # local variables
        loc_vars_sim = self._simimilarity_dicts(
            func1.get_numbers_of_local_vars(),
            func2.get_numbers_of_local_vars()
        )
        
        sim = Config.get('fast.func_ctrl_type_power') * ctrl_type_sim
        sim += Config.get('fast.func_loc_vars_power') * loc_vars_sim

        self._logger.info("ctrl_type_sim = %f" % (ctrl_type_sim))
        self._logger.info("loc_vars_sim = %f" % (loc_vars_sim))
        self._logger.info("fast.sim_functions(%s, %s) = %f" % (func1.get_name(), func2.get_name(), sim))

        return sim