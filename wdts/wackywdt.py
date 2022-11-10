from wdts.wdt import Wdt
import numpy


class WackyWdt(Wdt):
    """Represents the interface for different types of wdt calculations"""

    def calculate_wdt(self, tftd, docLengthD=0, docLengthA=0, avgTftd=1):
        """Calculates and returns wdt for the particular variant"""
        if avgTftd <= 0:
            avgTftd = 1
        return (1 + numpy.log(tftd))/(1 + numpy.log(avgTftd))
