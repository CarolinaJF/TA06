import os
import pandas as pd

def validate_dat_files(directory):
    for filename in os.listdir(directory):
        if filename.endswith('.dat'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
                # Check headers
                if len(lines) < 3:
                    print(f"Error in {filename}: Not enough lines for headers and data.")
                    continue
                
                # Validate first line (data origin and type)
                header1 = lines[0].strip()
                if not header1.startswith("precip") or "MIRO C5" not in header1 or "RCP60" not in header1:
                    print(f"Error in {filename}: Invalid first header line.")
                    continue
                
                # Validate second line (station name and coordinates)
                header2 = lines[1].strip().split()
                if len(header2) < 2:
                    print(f"Error in {filename}: Invalid second header line.")
                    continue
                
                # Validate data lines
                for line in lines[2:]:
                    data = line.strip().split()
                    if len(data) < 34:
                        print(f"Error in {filename}: Data line has insufficient columns.")
                        continue
                    
                    station_name = data[0]
                    year = int(data[1])
                    month = int(data[2])
                    daily_precipitations = data[3:]
                    
                    if year < 2006 or year > 2100:
                        print(f"Error in {filename}: Year out of range in line: {line.strip()}")
                        continue
                    
                    if month < 1 or month > 12:
                        print(f"Error in {filename}: Invalid month in line: {line.strip()}")
                        continue
                    
                    days_in_month = 31 if month in [1, 3, 5, 7, 8, 10, 12] else 30 if month in [4, 6, 9, 11] else 28
                    if len(daily_precipitations) != days_in_month:
                        print(f"Error in {filename}: Incorrect number of days in month {month} in line: {line.strip()}")
                        continue
                    
                    for value in daily_precipitations:
                        if value != '-999':
                            try:
                                float(value)
                            except ValueError:
                                print(f"Error in {filename}: Invalid precipitation value in line: {line.strip()}")
                                break

if __name__ == "__main__":
    validate_dat_files('/workspaces/TA06/E01/ayuda1')