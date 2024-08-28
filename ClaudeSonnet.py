import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import requests
import json
from datetime import datetime, timedelta
import csv
import statistics
from decimal import Decimal, getcontext

getcontext().prec = 28

class UnitConverter:
    def __init__(self, master):
        self.master = master
        self.master.title("Advanced Unit Converter")
        self.master.geometry("500x550")
        self.api_key = "fca_live_HctLDMbdSYtG4Knt5KyIU5bcKBlNXs4MW3u4AiMp"  # Replace with your actual API key
        self.base_url = "https://api.exchangerate-api.com/v4/latest"
        self.create_widgets()
        self.base_currency = "USD"
        self.currency_rates = {}
        self.last_update = None
        self.update_currency_rates()

    def create_widgets(self):
        # Category selection
        self.category_label = ttk.Label(self.master, text="Select category:")
        self.category_label.grid(row=0, column=0, padx=10, pady=10)
        self.categories = ["Length", "Weight", "Volume", "Currency", "Fuel Efficiency"]
        self.category_var = tk.StringVar()
        self.category_combobox = ttk.Combobox(self.master, textvariable=self.category_var, values=self.categories, state="readonly")
        self.category_combobox.grid(row=0, column=1, padx=10, pady=10)
        self.category_combobox.bind("<<ComboboxSelected>>", self.update_units)

        # Input
        self.input_label = ttk.Label(self.master, text="Input:")
        self.input_label.grid(row=1, column=0, padx=10, pady=10)
        self.input_var = tk.StringVar()
        self.input_var.trace("w", self.validate_input)
        self.input_entry = ttk.Entry(self.master, textvariable=self.input_var)
        self.input_entry.grid(row=1, column=1, padx=10, pady=10)

        # From unit
        self.from_label = ttk.Label(self.master, text="From:")
        self.from_label.grid(row=2, column=0, padx=10, pady=10)
        self.from_var = tk.StringVar()
        self.from_combobox = ttk.Combobox(self.master, textvariable=self.from_var, state="readonly")
        self.from_combobox.grid(row=2, column=1, padx=10, pady=10)

        # To unit
        self.to_label = ttk.Label(self.master, text="To:")
        self.to_label.grid(row=3, column=0, padx=10, pady=10)
        self.to_var = tk.StringVar()
        self.to_combobox = ttk.Combobox(self.master, textvariable=self.to_var, state="readonly")
        self.to_combobox.grid(row=3, column=1, padx=10, pady=10)

        # Result
        self.result_label = ttk.Label(self.master, text="Result:")
        self.result_label.grid(row=4, column=0, padx=10, pady=10)
        self.result_var = tk.StringVar()
        self.result_entry = ttk.Entry(self.master, textvariable=self.result_var, state="readonly")
        self.result_entry.grid(row=4, column=1, padx=10, pady=10)

        # Convert button
        self.convert_button = ttk.Button(self.master, text="Convert", command=self.convert)
        self.convert_button.grid(row=5, column=0, columnspan=2, padx=10, pady=10)

        # Status label
        self.status_var = tk.StringVar()
        self.status_label = ttk.Label(self.master, textvariable=self.status_var)
        self.status_label.grid(row=6, column=0, columnspan=2, padx=10, pady=10)

        # Batch Convert button
        self.batch_button = ttk.Button(self.master, text="Batch Convert", command=self.batch_convert)
        self.batch_button.grid(row=7, column=0, columnspan=2, padx=10, pady=10)

        # Statistics display
        self.stats_text = tk.Text(self.master, height=5, width=50, state='disabled')
        self.stats_text.grid(row=8, column=0, columnspan=2, padx=10, pady=10)

    def update_units(self, event):
        category = self.category_var.get()
        if category == "Length":
            units = ["Meters", "Kilometers", "Centimeters", "Millimeters", "Miles", "Yards", "Feet", "Inches"]
        elif category == "Weight":
            units = ["Kilograms", "Grams", "Milligrams", "Pounds", "Ounces"]
        elif category == "Volume":
            units = ["Liters", "Milliliters", "Cubic Meters", "Cubic Centimeters", "Gallons (US)", "Fluid Ounces (US)"]
        elif category == "Currency":
            units = list(self.currency_rates.keys())
        elif category == "Fuel Efficiency":
            units = ["MPG (US)", "MPG (UK)", "L/100km", "km/L"]
        else:
            units = []
        
        self.from_combobox['values'] = units
        self.to_combobox['values'] = units
        
        if units:
            self.from_var.set(units[0])
            self.to_var.set(units[1] if len(units) > 1 else units[0])
        else:
            self.from_var.set('')
            self.to_var.set('')
        
        self.convert()  # Automatically convert when changing categories

    def validate_input(self, *args):
        value = self.input_var.get()
        if value:
            try:
                Decimal(value)
                self.convert()  # Automatically convert on valid input
            except:
                self.input_var.set(value[:-1])

    def convert(self):
        try:
            value = self.safe_float(self.input_var.get())
            from_unit = self.from_var.get()
            to_unit = self.to_var.get()
            category = self.category_var.get()

            if category == "Currency":
                self.update_currency_rates()
                result = self.convert_currency(value, from_unit, to_unit)
            elif category == "Fuel Efficiency":
                result = self.convert_fuel_efficiency(value, from_unit, to_unit)
            else:
                base_value = self.to_base_unit(value, from_unit, category)
                result = self.from_base_unit(base_value, to_unit, category)

            self.result_var.set(f"{self.format_result(result)}")
            self.status_var.set("Conversion successful")
        except ValueError as e:
            self.result_var.set("Invalid input")
            self.status_var.set(f"Error: {str(e)}")
        except Exception as e:
            self.status_var.set(f"Error: {str(e)}")

    def safe_float(self, value):
        try:
            return Decimal(value)
        except:
            raise ValueError("Invalid numeric input")

    def format_result(self, value):
        return f"{value:.10f}".rstrip('0').rstrip('.')

    def to_base_unit(self, value, unit, category):
        conversion_factors = {
            "Length": {
                "Meters": Decimal('1'),
                "Kilometers": Decimal('1000'),
                "Centimeters": Decimal('0.01'),
                "Millimeters": Decimal('0.001'),
                "Miles": Decimal('1609.344'),
                "Yards": Decimal('0.9144'),
                "Feet": Decimal('0.3048'),
                "Inches": Decimal('0.0254')
            },
            "Weight": {
                "Kilograms": Decimal('1'),
                "Grams": Decimal('0.001'),
                "Milligrams": Decimal('0.000001'),
                "Pounds": Decimal('0.45359237'),
                "Ounces": Decimal('0.028349523125')
            },
            "Volume": {
                "Liters": Decimal('1'),
                "Milliliters": Decimal('0.001'),
                "Cubic Meters": Decimal('1000'),
                "Cubic Centimeters": Decimal('0.001'),
                "Gallons (US)": Decimal('3.78541'),
                "Fluid Ounces (US)": Decimal('0.0295735295625')
            }
        }
        return value * conversion_factors[category][unit]

    def from_base_unit(self, value, unit, category):
        conversion_factors = {
            "Length": {
                "Meters": Decimal('1'),
                "Kilometers": Decimal('1000'),
                "Centimeters": Decimal('0.01'),
                "Millimeters": Decimal('0.001'),
                "Miles": Decimal('1609.344'),
                "Yards": Decimal('0.9144'),
                "Feet": Decimal('0.3048'),
                "Inches": Decimal('0.0254')
            },
            "Weight": {
                "Kilograms": Decimal('1'),
                "Grams": Decimal('0.001'),
                "Milligrams": Decimal('0.000001'),
                "Pounds": Decimal('0.45359237'),
                "Ounces": Decimal('0.028349523125')
            },
            "Volume": {
                "Liters": Decimal('1'),
                "Milliliters": Decimal('0.001'),
                "Cubic Meters": Decimal('1000'),
                "Cubic Centimeters": Decimal('0.001'),
                "Gallons (US)": Decimal('3.78541'),
                "Fluid Ounces (US)": Decimal('0.0295735295625')
            }
        }
        return value / conversion_factors[category][unit]

    def convert_currency(self, amount, from_currency, to_currency):
        if from_currency == to_currency:
            return amount
        if not self.currency_rates:
            raise Exception("Currency rates are not available")
        base_rate = self.currency_rates[from_currency]
        target_rate = self.currency_rates[to_currency]
        return amount * (target_rate / base_rate)

    def convert_fuel_efficiency(self, value, from_unit, to_unit):
        conversion_factors = {
            "MPG (US)": Decimal('1'),
            "MPG (UK)": Decimal('1.20095'),
            "L/100km": Decimal('235.215'),
            "km/L": Decimal('0.425144')
        }
        if from_unit == to_unit:
            return value
        to_mpg = value * conversion_factors[from_unit]
        return to_mpg / conversion_factors[to_unit]

    def update_currency_rates(self):
        if not self.last_update or datetime.now() - self.last_update > timedelta(hours=1):
            try:
                response = requests.get(f"{self.base_url}/{self.base_currency}")
                data = response.json()
                if 'rates' not in data:
                    raise Exception("Invalid response from currency API")
                self.currency_rates = {k: Decimal(v) for k, v in data['rates'].items()}
                self.last_update = datetime.now()
                self.status_var.set("Currency rates updated successfully")
            except Exception as e:
                self.status_var.set(f"Error updating currency rates: {str(e)}")
        else:
            self.status_var.set("Currency rates are up-to-date")

    def batch_convert(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if not file_path:
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if not output_path:
            return

        try:
            with open(file_path, 'r') as input_file, open(output_path, 'w', newline='') as output_file:
                reader = csv.reader(input_file)
                writer = csv.writer(output_file)
                header = next(reader)
                writer.writerow(header + ['Converted Value'])

                values = []
                for row in reader:
                    input_value = row[0]
                    from_unit = row[1]
                    to_unit = row[2]
                    category = row[3]

                    self.input_var.set(input_value)
                    self.from_var.set(from_unit)
                    self.to_var.set(to_unit)
                    self.category_var.set(category)
                    self.convert()
                    converted_value = self.result_var.get()
                    writer.writerow(row + [converted_value])

                    try:
                        values.append(Decimal(converted_value))
                    except:
                        pass

                if values:
                    self.display_statistics(values)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to process file: {str(e)}")

    def display_statistics(self, values):
        mean_val = statistics.mean(values)
        median_val = statistics.median(values)
        self.stats_text.config(state='normal')
        self.stats_text.delete('1.0', tk.END)
        self.stats_text.insert(tk.END, f"Mean: {mean_val}\n")
        self.stats_text.insert(tk.END, f"Median: {median_val}\n")
        self.stats_text.config(state='disabled')


if __name__ == "__main__":
    root = tk.Tk()
    app = UnitConverter(root)
    root.mainloop()
