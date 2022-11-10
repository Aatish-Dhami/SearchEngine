from wdts.wdt import Wdt


class OkapiWdt(Wdt):
    """Represents the interface for different types of wdt calculations"""

    def calculate_wdt(self, tftd, docLengthD=0, docLengthA=0, avgTftd=1):
        """Calculates and returns wdt for the particular variant"""
        return (2.2 * tftd)/((1.2 * (0.25 + (0.75*(docLengthD/docLengthA)))) + tftd)
