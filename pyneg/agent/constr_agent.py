from pyneg.comms import AtomicConstraint
from .agent import Agent


class ConstrainedAgent(Agent):
    def __init__(self):
        raise NotImplementedError()

    def add_constraint(self, constraint: AtomicConstraint) -> None:
        raise NotImplementedError()
#         super().__init__(name, neg_space, utilities, reservation_value, issue_weights,
#                          verbose=Verbosity.none, max_rounds=max_rounds)
#         self.auto_constraints = auto_constraints
#         if own_constraints:
#             self.own_constraints: Set[AtomicConstraint] = own_constraints
#         else:
#             self.own_constraints = set()

#         if opponent_constraints:
#             self.opponent_constraints: Set[AtomicConstraint] = opponent_constraints
#         else:
#             self.opponent_constraints = set()

#         self.constraints_satisfiable: bool = True

#     def negotiate(self, opponent: AbstractAgent) -> bool:
#         if self.constraints_satisfiable:
#             return super().negotiate(opponent)
#         else:
#             return False

#     def add_utilities(self, new_utils: Dict[str, float]):
#         super().add_utilities(new_utils)

#         # All utilities need to be added before we can determine
#         # whether there should be any constraints
#         if self.auto_constraints:
#             new_constraints = self.generate_new_constraints()
#             for new_constr in new_constraints:
#                 self.add_constraint(new_constr, True)

#     def generate_new_constraints(self):
#         if self.verbose >= Verbosity.debug:
#             print("{} is checking for new constraints".format(self.agent_name))

#         new_constraints = set()
#         for issue in self.neg_space.keys():
#             best_case = sum(
#                 [bc for i, bc in self.max_utility_by_issue.items() if i != issue])

#             for value in self.neg_space[issue]:
#                 atom = Offer.atom_from_issue_value(issue, value)
#                 if atom in self.utilities.keys():
#                     value_util = self.utilities[atom]
#                 else:
#                     value_util = 0

#                 if best_case+value_util < self.absolute_reservation_value:
#                     if self.verbose >= Verbosity.reasoning:
#                         print("{} is adding new constraint {} because best_case util of {} is too low".format(
#                             self.agent_name,
#                             AtomicConstraint(issue, value),
#                             best_case+value_util))
#                     new_constraints.add(AtomicConstraint(issue, value))

#         return new_constraints

#     def get_unconstrained_values_by_issue(self, issue):
#         issue_constrained_values = [
#             constr.value for constr in self.get_all_constraints() if constr.issue == issue]
#         issue_un_constrained_values = set(
#             self.neg_space[issue]) - set(issue_constrained_values)
#         return issue_un_constrained_values

#     def add_constraint(self, constraint: AtomicConstraint, own_constraint: bool) -> None:
#         if own_constraint:
#             self.own_constraints.add(constraint)
#             if self.verbose >= Verbosity.reasoning:
#                 print("{} is adding own constraint: {}".format(
#                     self.agent_name, constraint))
#         else:
#             self.opponent_constraints.add(constraint)
#             if self.verbose >= Verbosity.reasoning:
#                 print("{} is adding opponent constraint: {}".format(
#                     self.agent_name, constraint))

#         if not self.constraints_satisfiable:
#             return

#         if not Offer.atom_from_issue_value(constraint.issue, constraint.value) in self.utilities.keys():
#             self.add_utilities({Offer.atom_from_issue_value(
#                 constraint.issue, constraint.value): self.non_agreement_cost})
#         else:
#             self.utilities[Offer.atom_from_issue_value(
#                 constraint.issue, constraint.value)] = self.non_agreement_cost

#     # def make_strat_constraint_compliant(self) -> None:
#     #     for constr in self.get_all_strat_constraints():
#     #         for issue in self.neg_space.keys():
#     #             issue_unconstrained_values = self.get_unconstrained_values_by_issue(
#     #                 issue)
#     #             if len(issue_unconstrained_values) == 0:
#     #                 if self.verbose >= Verbosity.reasoning:
#     #                     print("Found incompatible constraint: {}".format(constraint))

#     #                 self.constraints_satisfiable = False
#     #                 # Unsatisfiable constraint so we're terminating on the next message so we won't need to update the strat
#     #                 return

#     #             for value in self.neg_space[issue].keys():
#     #                 if not constraint.is_satisfied_by_assignment(issue, value):
#     #                     self.strategy.set_prob(issue, value, 0)

#     #             # it's possible we just made the last value in the strategy 0 so
#     #             # we have to figure out which value is still unconstrained
#     #             # and set that one to 1
#     #             if sum(self.strat_dict[issue].values()) == 0:
#     #                 self.strat_dict[issue][next(
#     #                     iter(issue_unconstrained_values))] = 1
#     #             else:
#     #                 strat_sum = sum(self.strat_dict[issue].values())
#     #                 self.strat_dict[issue] = {
#     #                     key: prob / strat_sum for key, prob in self.strat_dict[issue].items()}

#     def satisfies_all_constraints(self, offer: Offer) -> bool:
#         all_constraints = self.get_all_constraints()
#         for constr in all_constraints:
#             if not constr.is_satisfied_by_strat(offer):
#                 return False
#         return True

#     def generate_next_message_from_transcript(self) -> Optional[Message]:
#         try:
#             last_message = self.transcript[-1]
#         except IndexError:
#             # if our transcript is empty, we should make the initial offer
#             return self.generate_offer_message()

#         if last_message.constraint:
#             if self.verbose >= Verbosity.reasoning:
#                 print("{} is adding opponent constraint {}".format(
#                     self.agent_name, last_message.constraint))
#             self.add_constraint(last_message.constraint, False)

#         if self.verbose >= Verbosity.reasoning:
#             print("{} is using {} to generate next offer.".format(
#                 self.agent_name, last_message))

#         if last_message.is_acceptance():
#             self.negotiation_active = False
#             self.successful = True
#             return None

#         if last_message.is_termination():
#             self.negotiation_active = False
#             self.successful = False
#             return None

#         if self.should_terminate():
#             self.negotiation_active = False
#             self.successful = False
#             return Message(self.agent_name,
#                            self.opponent_name,
#                            MessageType.terminate,
#                            None)

#         if self.accepts(last_message.offer):
#             self.negotiation_active = False
#             self.successful = True
#             return Message(self.agent_name,
#                            self.opponent_name,
#                            MessageType.accept,
#                            last_message.offer)

#         return self.generate_offer_message()

#     def generate_offer_message(self) -> Message:
#         try:
#             offer = self.generate_offer()
#         except RuntimeError:
#             if self.verbose >= Verbosity.reasoning:
#                 print("{} is terminating because they were unable to generate an offer".format(
#                     self.agent_name))
#             offer = None

#         if not offer:
#             # We werent able to generate an offer so terminate the negotiation
#             self.negotiation_active = False
#             self.successful = False
#             termination_message = Message(
#                 self.agent_name, self.opponent_name, MessageType.terminate, None)
#             self.record_message(termination_message)
#             return termination_message

#         if not self.satisfies_all_constraints(offer):
#             raise RuntimeError(
#                 "should not be able to generate constraint violating offer: " +
#                 "{}\n constraints: {}".format(offer, self.get_all_constraints()))

#         # possible we don't have any previous messages
#         try:
#             constraint = self.find_violated_constraint(
#                 self.transcript[-1].offer)
#         except IndexError:
#             constraint = None

#         return Message(self.agent_name, self.opponent_name, MessageType.offer, offer=offer, constraint=constraint)

#     def generate_offer(self) -> Optional[Offer]:
#         if self.constraints_satisfiable:
#             return super().generate_offer()
#         else:
#             raise RuntimeError(
#                 "Cannot generate offer with incompatable constraints: {}".format(self.get_all_constraints()))

#     def find_violated_constraint(self, offer: Optional[Offer]) -> Optional[AtomicConstraint]:
#         if not offer:
#             return None

#         for constr in self.own_constraints:
#             for issue in self.neg_space.keys():
#                 for value in self.neg_space[issue]:
#                     if not constr.is_satisfied_by_assignment(issue, value) and not isclose(offer[issue][value], 0):
#                         return AtomicConstraint(issue, value)

#         return None

#     def calc_offer_utility(self, offer: Offer) -> float:
#         if not self.satisfies_all_constraints(offer):
#             return self.non_agreement_cost

#         return super().calc_offer_utility(offer)

#     def receive_message(self, msg: Message) -> None:
#         if self.verbose >= Verbosity.messages:
#             print("{}: received message: {}".format(self.agent_name, msg))
#         self.record_message(msg)
#         if msg.constraint:
#             self.add_constraint(msg.constraint, False)
#             if self.verbose >= Verbosity.debug:
#                 print("constraints still consistant: {}".format(
#                     self.constraints_satisfiable))

#     def get_all_constraints(self) -> Set[AtomicConstraint]:
#         return self.own_constraints.copy().union(self.opponent_constraints)

#     def should_terminate(self) -> bool:
#         return len(self.transcript) >= self.max_rounds or not self.constraints_satisfiable
