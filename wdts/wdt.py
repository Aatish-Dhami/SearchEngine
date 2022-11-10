from abc import ABC, abstractmethod


class Wdt(ABC):
    """Represents the interface for different types of wdt calculations"""

    @abstractmethod
    def calculate_wdt(self, tftd, docLengthD=0, docLengthA=0, avgTftd=1):
        """Calculates and returns wdt for the particular variant"""
        pass
