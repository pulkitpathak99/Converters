import unittest
from decimal import Decimal
from ClaudeSonnet import UnitConverter  # Assuming your converter file is named 'unit_converter.py'

class TestUnitConverter(unittest.TestCase):
    def setUp(self):
        self.converter = UnitConverter(None)  # Initialize the converter without the GUI
        
    def test_length_conversion(self):
        # Test Meters to Kilometers
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1000'), 'Meters', 'Length'), 'Kilometers', 'Length')
        self.assertEqual(result, Decimal('1'))

        # Test Miles to Meters
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1'), 'Miles', 'Length'), 'Meters', 'Length')
        self.assertEqual(result, Decimal('1609.344'))

        # Test Feet to Inches
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1'), 'Feet', 'Length'), 'Inches', 'Length')
        self.assertEqual(result, Decimal('12'))

    def test_weight_conversion(self):
        # Test Kilograms to Grams
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1'), 'Kilograms', 'Weight'), 'Grams', 'Weight')
        self.assertEqual(result, Decimal('1000'))

        # Test Pounds to Kilograms
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1'), 'Pounds', 'Weight'), 'Kilograms', 'Weight')
        self.assertEqual(result, Decimal('0.45359237'))

    def test_volume_conversion(self):
        # Test Liters to Milliliters
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1'), 'Liters', 'Volume'), 'Milliliters', 'Volume')
        self.assertEqual(result, Decimal('1000'))

        # Test Gallons (US) to Liters
        result = self.converter.from_base_unit(
            self.converter.to_base_unit(Decimal('1'), 'Gallons (US)', 'Volume'), 'Liters', 'Volume')
        self.assertEqual(result, Decimal('3.78541'))

    def test_fuel_efficiency_conversion(self):
        # Test MPG (US) to L/100km
        result = self.converter.convert_fuel_efficiency(Decimal('1'), 'MPG (US)', 'L/100km')
        self.assertEqual(round(result, 5), Decimal('235.21500'))

        # Test km/L to MPG (US)
        result = self.converter.convert_fuel_efficiency(Decimal('1'), 'km/L', 'MPG (US)')
        self.assertEqual(round(result, 6), Decimal('2.35215'))

    def test_currency_conversion(self):
        # Simulate currency rates
        self.converter.currency_rates = {'USD': Decimal('1'), 'EUR': Decimal('0.85')}
        
        # Test USD to EUR conversion
        result = self.converter.convert_currency(Decimal('100'), 'USD', 'EUR')
        self.assertEqual(result, Decimal('85'))

        # Test EUR to USD conversion
        result = self.converter.convert_currency(Decimal('85'), 'EUR', 'USD')
        self.assertEqual(result, Decimal('100'))

    def test_invalid_input(self):
        # Test invalid input for conversions
        with self.assertRaises(ValueError):
            self.converter.safe_float('abc')

if __name__ == "__main__":
    unittest.main()
