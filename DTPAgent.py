import re
import subprocess as sp
from os import remove, getpid
from os.path import join, abspath, dirname
from problog.tasks.dtproblog import dtproblog
from problog.program import PrologString
from numpy import isclose
from numpy.random import choice
import gc
from constraintNegotiationAgent import ConstraintNegotiationAgent
from randomNegotiationAgent import Verbosity


class DTPNegotiationAgent(ConstraintNegotiationAgent):
    def __init__(self, uuid, utilities, kb, reservation_value, non_agreement_cost, issues=None, max_rounds=10000,
                 verbose=0, name="", reporting=True, mean_utility=0, std_utility=0, constraint_threshold=-20):
        super().__init__(uuid, utilities, kb, reservation_value, non_agreement_cost, issues=issues,
                         max_rounds=max_rounds, verbose=verbose, name=name, reporting=reporting,
                         mean_utility=mean_utility, std_utility=std_utility, constraint_threshold=constraint_threshold)
        self.strat_name = "DTP"
        self.generated_offers = []

    def file_based_dtproblog(self, model):
        # using the python implementation of problog causes memory leaks
        # so we use the commandline interface separately to avoid this as a temp fix
        self.total_offers_generated += 1
        model_path = abspath(join(dirname(__file__), 'models/temp_model_{}.pl'.format(getpid())))
        if self.verbose >= Verbosity.debug:
            print("{} is calculating dtp model: {}".format(self.agent_name, model))

        with open(model_path, "w") as temp_file:
            temp_file.write(model)

        process = sp.Popen(["problog", "dt", model_path, "--verbose"], stdout=sp.PIPE)
        output, error = process.communicate()
        decoded_output = output.decode("ascii")
        score = float(re.search(r"SCORE: (-?\d+\.\d+)", decoded_output).group(1))

        ans = {}
        for string in decoded_output.split("\n"):
            if string and not re.search("[INFO]", string):
                key, prob = string.strip().split(":\t")
                ans[key] = float(prob)

        # for issue in self.issues.keys:
        #     if not issue in ans

        remove(model_path)
        return ans, score

    def compile_dtproblog_model(self):
        decision_facts_string = self.format_dtproblog_strat()
        utility_string = self.format_utility_string()
        kb_string = "\n".join(self.KB) + "\n"
        return decision_facts_string + kb_string + utility_string

    def format_dtproblog_strat(self):
        return_string = ""
        for issue in self.strat_dict.keys():
            atom_list = []
            for value in self.strat_dict[issue].keys():
                if "." in str(value):
                    atom_list.append("?::'{issue}_{val}'".format(
                        issue=issue, val=value))
                else:
                    atom_list.append("?::{issue}_{val}".format(
                        issue=issue, val=value))

            return_string += ";".join(atom_list) + ".\n"
        return return_string

    def format_utility_string(self):
        return_string = ""
        for u, r in self.utilities.items():
            return_string += "utility({},{}).\n".format(u, r)

        offer_counter = 0
        for offer, score in self.generated_offers:
            atom_list = []
            for atom, val in offer.items():
                if isclose(val, 1):
                    atom_list.append(atom)
            return_string += "offer{} :- {}.\n".format(offer_counter, ",".join(atom_list))
            return_string += "utility(offer{},{}).\n".format(offer_counter, -score + self.non_agreement_cost)
            offer_counter += 1

        for constr in self.get_all_constraints():
            return_string += "utility({}_{},{}).\n".format(constr.issue, constr.value, -(2 ** 31))

        return return_string

    def generate_offer(self):
        # query_output, score = self.file_based_dtproblog(self.compile_dtproblog_model())

        program = PrologString(self.compile_dtproblog_model())
        query_output, score, _ = dtproblog(program)
        query_output = {str(atom): float(prob) for atom, prob in query_output.items()}
        gc.collect()
        if self.verbose >= Verbosity.debug:
            print("{} generated offer: {}".format(self.agent_name, self.nested_dict_from_atom_dict(query_output)))

        # if there are no acceptable offers left we should terminate
        if score < self.reservation_value:
            return None

        self.generated_offers.append((query_output, score))
        generated_offer = self.nested_dict_from_atom_dict(query_output)

        # if dtproblog didn't choose a value we'll just randomly choose one since it makes no difference
        # but we need to choose according to the strat dict so we don't choose a constrained value
        listed_strat = {}
        for issue in self.strat_dict.keys():
            listed_strat[issue] = list(map(list, zip(*self.strat_dict[issue].items())))

        for issue in generated_offer.keys():
            if isclose(sum(generated_offer[issue].values()), 0):
                chosen_value = str(choice(listed_strat[issue][0], 1, p=listed_strat[issue][1])[0])
                generated_offer[issue] = {key: 0 for key in self.strat_dict[issue].keys()}
                generated_offer[issue][chosen_value] = 1

        return generated_offer
