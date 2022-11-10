from abc import ABC, abstractmethod


class Variants(ABC):
    """Represents the interface for different types of variants calculations"""

    @abstractmethod
    def get_accumulator_dict(self, query, path, dp_index, token_processor):
        """Calculates and returns wdt for the particular variant"""
        pass

    @abstractmethod
    def _get_wdt(self, tftd):
        """Calculates wdt for the specific term-document"""
        pass

    @abstractmethod
    def _get_wqt(self, n, dft):
        """Calculates wqt for the specific term"""
        pass

    def _get_ld(self, factor=1):
        pass
