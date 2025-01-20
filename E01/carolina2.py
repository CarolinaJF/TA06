import os
import pandas as pd

def validate_dat_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith(".dat"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
                # Check if file has at least 2 lines
                if len(lines) < 2:
                    print(f"Error: {filename} does not have enough lines.")
                    continue
                
                # Validate header
                header = lines[0].strip()
                if not header.startswith("precip") or "MIRO C5" not in header or "RCP60" not in header or "Regresión" not in header:
                    print(f"Error: {filename} has an incorrect header.")
                    continue
                
                # Validate data
                data_line = lines[1].strip().split()
                if len(data_line) < 35:
                    print(f"Error: {filename} does not have enough columns.")
                    continue
                
                station_name = data_line[0]
                try:
                    year = int(data_line[1])
                    if year < 2006 or year > 2100:
                        print(f"Error: {filename} has an incorrect year: {year}.")
                        continue
                except ValueError:
                    print(f"Error: {filename} has a non-integer year.")
                    continue
                
                try:
                    month = int(data_line[2])
                    if month < 1 or month > 12:
                        print(f"Error: {filename} has an incorrect month: {month}.")
                        continue
                except ValueError:
                    print(f"Error: {filename} has a non-integer month.")
                    continue
                
                # Validate precipitation data
                precipitation_data = data_line[3:]
                if len(precipitation_data) != 31:
                    print(f"Error: {filename} does not have 31 days of data.")
                    continue
                
                valid_data_count = sum(1 for x in precipitation_data if x != '-999')
                if valid_data_count < 28:
                    print(f"Error: {filename} has less than 28 valid days of data.")
                    continue
                
                # Check for numeric values in precipitation data
                try:
                    precipitation_data = [float(x) for x in precipitation_data if x != '-999']
                except ValueError:
                    print(f"Error: {filename} has non-numeric precipitation data.")
                    continue
                
                print(f"{filename} is valid.")

if __name__ == "__main__":
    validate_dat_files("/workspaces/TA06/E01/ayuda1")