"""
This module defines the Message class, which is the main mode of communication between agents.
"""

from typing import Optional

from pyneg.types import MessageType
from .atomic_constraint import AtomicConstraint
from .offer import Offer


class Message():
    """
    This class is the main mode of communication between agents.
    It contains a sender and recipient name (mainly for logging purposes),
    a type (defined in :ref:`msg_type`), and optionally an offer and
    constraint. The message contain an offer if and only if it is either ACCEPT or OFFER.
    """
    def __init__(self, sender_name: str,
                 recipient_name: str,
                 type_: MessageType,
                 offer: Optional[Offer],
                 constraint: Optional[AtomicConstraint] = None):

        self.sender_name: str = sender_name
        self.recipient_name: str = recipient_name

        if not isinstance(type_, MessageType):
            raise ValueError("Invalid message type")

        if not isinstance(offer, Offer) and offer is not None:
            raise ValueError("Invalid offer")

        if type_ == MessageType.EMPTY:
            if offer:
                raise ValueError("empty message cannot have an offer")
            self.type_: MessageType = MessageType.EMPTY
            self.offer: Optional[Offer] = None
            self.constraint: Optional[AtomicConstraint] = None
            return

        if not offer and type_ != MessageType.EXIT:
            raise ValueError("Non empty message must have an offer")
        self.type_ = type_
        self.offer = offer
        self.constraint = constraint
        return

    def is_empty(self) -> bool:
        """
        Checks whether the message is empty

        :return: True iff the message is empty
        :rtype: bool
        """
        return self.type_ == MessageType.EMPTY

    def is_acceptance(self) -> bool:
        """
        Checks whether the message is one of acceptance

        :return: True iff sender accepts the offer in this message
        :rtype: bool
        """
        return self.type_ == MessageType.ACCEPT

    def is_termination(self) -> bool:
        """
        Checks whether the message signals one party is ending the negotiation early.

        :return: True iff sender is ending the negotiation early
        :rtype: bool
        """
        return self.type_ == MessageType.EXIT

    def has_constraint(self) -> bool:
        """
        Checks whether the message has a constraint

        :return: True iff the message has a constraint
        :rtype: bool
        """
        return self.constraint is not None

    def is_offer(self) -> bool:
        """
        Checks whether the message contains an offer

        :return: True iff the message contains an offer
        :rtype: bool
        """
        return self.type_ == MessageType.OFFER

    def get_constraint(self) -> AtomicConstraint:
        """
        Returns the constraint associated with this message

        :raises ValueError: Raised if the message does not contain a constraint
        :return: The constraint associated with this message
        :rtype: AtomicConstraint
        """
        if not self.constraint:
            raise ValueError("Message has no constraint")
        return self.constraint

    def __hash__(self):
        return hash([self.sender_name,
                     self.recipient_name,
                     self.type_,
                     self.offer,
                     self.constraint])

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Message):
            return False

        if other.type_ != self.type_:
            return False

        if other.offer != self.offer:
            return False

        if other.constraint != self.constraint:
            return False

        return True

    def __repr__(self) -> str:

        if not self.offer:
            return "({sender}=>{recip};{type_})".format(
                sender=self.sender_name,
                recip=self.recipient_name,
                type_=self.type_.name)

        if self.constraint:
            return "({sender}=>{recip};{type_};{offer};{constraint})".format(
                sender=self.sender_name,
                recip=self.recipient_name,
                type_=self.type_.name,
                offer=self.offer,
                constraint=self.constraint)

        return "({sender}=>{recip};{type_};{offer})".format(
            sender=self.sender_name,
            recip=self.recipient_name,
            type_=self.type_.name,
            offer=self.offer)
