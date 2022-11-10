from wdts.wdt import Wdt
import numpy


class TfidfWdt(Wdt):
    """Represents the interface for different types of wdt calculations"""

    def calculate_wdt(self, tftd, docLengthD=0, docLengthA=0, avgTftd=1):
        """Calculates and returns wdt for the particular variant"""
        return tftd
