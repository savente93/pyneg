from pyneg.comms import Offer
from pyneg.types import AtomicDict


class Generator():
    '''
    Generator empty class that is used soley for type annotations

    :raises NotImplementedError
    :raises NotImplementedError
    '''

    def __init__(self):
        raise NotImplementedError()

    def generate_offer(self) -> Offer:
        raise NotImplementedError()

    def add_utilities(self, new_utils: AtomicDict) -> None:
        raise NotImplementedError()

    def set_utilities(self, new_utils: AtomicDict) -> None:
        raise NotImplementedError()
