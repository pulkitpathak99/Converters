import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import csv
import statistics
import threading
import time

class UnitConverter:
    def __init__(self):
        self.categories = {
            'Length': ['Meters', 'Feet', 'Miles', 'Kilometers'],
            'Weight': ['Kilograms', 'Pounds', 'Grams'],
            'Volume': ['Liters', 'Gallons', 'Milliliters'],
            'Fuel Efficiency': ['Miles per Gallon', 'Liters per 100 km']
        }

        self.conversion_factors = {
            'Length': {
                'Meters': 1,
                'Feet': 0.3048,
                'Miles': 1609.34,
                'Kilometers': 1000
            },
            'Weight': {
                'Kilograms': 1,
                'Pounds': 0.453592,
                'Grams': 0.001
            },
            'Volume': {
                'Liters': 1,
                'Gallons': 3.78541,
                'Milliliters': 0.001
            }
            # Fuel Efficiency handled separately
        }

    def convert_fuel_efficiency(self, value, from_unit, to_unit):
        if from_unit == to_unit:
            return value
        elif from_unit == 'Miles per Gallon' and to_unit == 'Liters per 100 km':
            try:
                return 235.214583 / value
            except ZeroDivisionError:
                return "Division by zero"
        elif from_unit == 'Liters per 100 km' and to_unit == 'Miles per Gallon':
            try:
                return 235.214583 / value
            except ZeroDivisionError:
                return "Division by zero"
        else:
            return "Unsupported fuel efficiency conversion"

    def convert(self, value, from_unit, to_unit):
        # Identify category
        for category, units in self.categories.items():
            if from_unit in units and to_unit in units:
                if category == 'Fuel Efficiency':
                    return self.convert_fuel_efficiency(value, from_unit, to_unit)
                else:
                    # Convert from 'from_unit' to base unit
                    try:
                        base_value = value * self.conversion_factors[category][from_unit]
                        # Convert from base unit to 'to_unit'
                        result = base_value / self.conversion_factors[category][to_unit]
                        return result
                    except KeyError:
                        return "Unsupported unit conversion"
        return "Unsupported conversion"

class CurrencyConverter:
    def __init__(self):
        self.base = 'USD'
        self.rates = {}
        self.last_fetched = 0
        self.update_interval = 3600  # 1 hour

    def fetch_rates(self):
        url = f"https://api.exchangerate.host/latest?base={self.base}"
        try:
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                self.rates = data['rates']
                self.last_fetched = time.time()
            else:
                print("Failed to fetch currency data.")
        except Exception as e:
            print(f"Error fetching currency rates: {e}")

    def get_rates(self):
        if not self.rates or (time.time() - self.last_fetched > self.update_interval):
            self.fetch_rates()
        return self.rates

    def convert(self, value, from_currency, to_currency):
        rates = self.get_rates()
        if from_currency == to_currency:
            return value
        if from_currency != self.base:
            from_rate = rates.get(from_currency)
            if from_rate is None:
                return "Unsupported currency"
        else:
            from_rate = 1.0
        if to_currency != self.base:
            to_rate = rates.get(to_currency)
            if to_rate is None:
                return "Unsupported currency"
        else:
            to_rate = 1.0
        if from_rate is None or to_rate is None:
            return "Unsupported currency"
        # Convert to base, then to target
        try:
            base_value = value / from_rate
            result = base_value * to_rate
            return result
        except ZeroDivisionError:
            return "Division by zero"

class UnitConverterApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Unit Converter")
        self.master.geometry("600x600")
        self.master.resizable(False, False)

        # Initialize converters
        self.unit_converter = UnitConverter()
        self.currency_converter = CurrencyConverter()

        # Initialize the notebook
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both')

        # Single Conversion Tab
        self.single_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.single_tab, text='Single Conversion')

        # Batch Conversion Tab
        self.batch_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.batch_tab, text='Batch Conversion')

        # Setup Single Conversion Tab
        self.setup_single_tab()

        # Setup Batch Conversion Tab
        self.setup_batch_tab()

    def setup_single_tab(self):
        # Create a frame for single conversion
        frame = self.single_tab
        padding = {'padx': 10, 'pady': 10}

        # Value label and entry with validation
        label_value = ttk.Label(frame, text="Value:")
        label_value.grid(column=0, row=0, sticky='W', **padding)

        # Register validation command
        vcmd = (self.master.register(self.validate_input), '%P')

        self.entry_value = ttk.Entry(frame, validate='key', validatecommand=vcmd)
        self.entry_value.grid(column=1, row=0, **padding)

        # From unit
        label_from = ttk.Label(frame, text="From:")
        label_from.grid(column=0, row=1, sticky='W', **padding)

        self.combo_from = ttk.Combobox(frame, values=self.get_all_units(), state='readonly')
        self.combo_from.set("Meters")
        self.combo_from.grid(column=1, row=1, **padding)

        # To unit
        label_to = ttk.Label(frame, text="To:")
        label_to.grid(column=0, row=2, sticky='W', **padding)

        self.combo_to = ttk.Combobox(frame, values=self.get_all_units(), state='readonly')
        self.combo_to.set("Feet")
        self.combo_to.grid(column=1, row=2, **padding)

        # Convert button
        self.button_convert = ttk.Button(frame, text="Convert", command=self.convert_single)
        self.button_convert.grid(column=0, row=3, columnspan=2, **padding)

        # Result label
        self.label_result = ttk.Label(frame, text="", foreground="blue", font=('Arial', 12, 'bold'))
        self.label_result.grid(column=0, row=4, columnspan=2, **padding)

    def setup_batch_tab(self):
        # Create a frame for batch conversion
        frame = self.batch_tab
        padding = {'padx': 10, 'pady': 10}

        # Button to load file
        self.button_load = ttk.Button(frame, text="Load Conversion File", command=self.load_file)
        self.button_load.grid(column=0, row=0, sticky='W', **padding)

        # Text widget to display results
        self.text_results = tk.Text(frame, height=20, width=70, state='disabled', wrap='word')
        self.text_results.grid(column=0, row=1, columnspan=2, **padding)

        # Summary statistics
        self.label_summary = ttk.Label(frame, text="", foreground="green", font=('Arial', 10, 'bold'))
        self.label_summary.grid(column=0, row=2, columnspan=2, **padding)

    def get_all_units(self):
        # Get all units from all categories
        units = []
        for category_units in self.unit_converter.categories.values():
            units.extend(category_units)
        # Include currencies
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'AUD', 'CAD', 'CHF', 'NZD', 'SEK', 'NOK', 'MXN']
        units.extend(currencies)
        return sorted(set(units))

    def validate_input(self, P):
        # Allow empty string or valid float number
        if P == "":
            return True
        try:
            float(P)
            return True
        except ValueError:
            return False

    def determine_category(self, from_unit, to_unit):
        for category, units in self.unit_converter.categories.items():
            if from_unit in units and to_unit in units:
                return category
        # Check if both are currencies
        currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'AUD', 'CAD', 'CHF', 'NZD', 'SEK', 'NOK', 'MXN']
        if from_unit in currencies and to_unit in currencies:
            return 'Currency'
        return None

    def convert_single(self):
        value_str = self.entry_value.get()
        from_unit = self.combo_from.get()
        to_unit = self.combo_to.get()

        if not value_str:
            self.label_result.config(text="Please enter a value.", foreground="red")
            return
        try:
            value = float(value_str)
        except ValueError:
            self.label_result.config(text="Invalid input. Please enter a valid number.", foreground="red")
            return

        category = self.determine_category(from_unit, to_unit)
        if category is None:
            self.label_result.config(text="Unsupported conversion.", foreground="red")
            return

        if category == 'Currency':
            # Perform currency conversion in a separate thread
            self.convert_currency(value, from_unit, to_unit)
        else:
            # Perform unit conversion
            result = self.unit_converter.convert(value, from_unit, to_unit)
            if isinstance(result, float):
                self.label_result.config(text=f"Result: {result:.4f} {to_unit}", foreground="blue")
            else:
                self.label_result.config(text=f"Error: {result}", foreground="red")

    def convert_currency(self, value, from_currency, to_currency):
        def task():
            result = self.currency_converter.convert(value, from_currency, to_currency)
            if isinstance(result, float):
                display_result = f"Result: {result:.4f} {to_currency}"
                color = "blue"
            else:
                display_result = f"Error: {result}"
                color = "red"
            self.master.after(0, lambda: self.label_result.config(text=display_result, foreground=color))
        threading.Thread(target=task).start()

    def load_file(self):
        file_path = filedialog.askopenfilename(
            title="Select Conversion CSV File",
            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
        )
        if not file_path:
            return
        threading.Thread(target=self.process_file, args=(file_path,)).start()

    def process_file(self, file_path):
        try:
            with open(file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                # Expect columns: value, from_unit, to_unit
                rows = list(reader)
                if not rows:
                    self.master.after(0, lambda: messagebox.showwarning("No Data", "The CSV file is empty."))
                    return
                # Check if any currency conversions are needed
                needs_currency = False
                currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CNY', 'AUD', 'CAD', 'CHF', 'NZD', 'SEK', 'NOK', 'MXN']
                for row in rows:
                    from_unit = row.get('from_unit') or row.get('From') or row.get('FROM')
                    to_unit = row.get('to_unit') or row.get('To') or row.get('TO')
                    if from_unit in currencies and to_unit in currencies:
                        needs_currency = True
                        break
                if needs_currency:
                    self.currency_converter.fetch_rates()
                results = []
                values_for_stats = []
                for idx, row in enumerate(rows, start=1):
                    value_str = row.get('value') or row.get('Value') or row.get('VALUE')
                    from_unit = row.get('from_unit') or row.get('From') or row.get('FROM')
                    to_unit = row.get('to_unit') or row.get('To') or row.get('TO')
                    if value_str is None or from_unit is None or to_unit is None:
                        results.append(f"{idx}. Invalid row: missing fields.")
                        continue
                    try:
                        value = float(value_str)
                    except ValueError:
                        results.append(f"{idx}. Invalid value: {value_str}")
                        continue
                    category = self.determine_category(from_unit, to_unit)
                    if category is None:
                        results.append(f"{idx}. Unsupported conversion: {from_unit} to {to_unit}")
                        continue
                    if category == 'Currency':
                        converted = self.currency_converter.convert(value, from_unit, to_unit)
                    else:
                        converted = self.unit_converter.convert(value, from_unit, to_unit)
                    if isinstance(converted, float):
                        results.append(f"{idx}. {value} {from_unit} = {converted:.4f} {to_unit}")
                        values_for_stats.append(converted)
                    else:
                        results.append(f"{idx}. Error: {converted}")
            # After processing, calculate statistics
            if values_for_stats:
                total = sum(values_for_stats)
                average = statistics.mean(values_for_stats)
                minimum = min(values_for_stats)
                maximum = max(values_for_stats)
                summary = f"Total: {total:.4f}, Average: {average:.4f}, Min: {minimum:.4f}, Max: {maximum:.4f}"
            else:
                summary = "No valid numeric conversions."
            # Display results and summary in the main thread
            self.master.after(0, lambda: self.display_batch_results(results, summary))
        except FileNotFoundError:
            self.master.after(0, lambda: messagebox.showerror("File Not Found", "The selected file does not exist."))
        except Exception as e:
            self.master.after(0, lambda: messagebox.showerror("Error", f"Failed to process file: {e}"))

    def display_batch_results(self, results, summary):
        self.text_results.config(state='normal')
        self.text_results.delete(1.0, tk.END)
        for res in results:
            self.text_results.insert(tk.END, f"{res}\n")
        self.text_results.config(state='disabled')
        self.label_summary.config(text=summary)

def main():
    root = tk.Tk()
    app = UnitConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
