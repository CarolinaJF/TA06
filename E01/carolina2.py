import os

def is_bisextile(year):
    # Check if a year is a leap year.
    return (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0)

def validate_dat_files(directory):
    errors = 0
    error_types = {
        'missing_lines': 0,
        'missing_station_name': 0,
        'invalid_coordinates': 0,
        'missing_values': 0,
        'year_out_of_range': 0,
        'month_out_of_range': 0,
        'incorrect_days': 0,
        'invalid_data_value': 0
    }

    for filename in os.listdir(directory):
        if filename.endswith('.dat'):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as file:
                lines = file.readlines()
                
                # Validate headers
                if len(lines) < 3:
                    print(f"Error in {filename}: File does not have enough lines.")
                    errors += 1
                    error_types['missing_lines'] += 1
                    continue
                
                # Validate station name and data type
                station_name = lines[0].strip()
                if not station_name:
                    print(f"Error in {filename}: Station name is missing.")
                    errors += 1
                    error_types['missing_station_name'] += 1
                
                # Validate coordinates
                coordinates = lines[1].strip().split()
                if len(coordinates) != 2:
                    print(f"Error in {filename}: Invalid coordinates (expecting 2 values).")
                    errors += 1
                    error_types['invalid_coordinates'] += 1
                    continue
                
                try:
                    float(coordinates[0])
                    float(coordinates[1])
                except ValueError:
                    print(f"Error in {filename}: Invalid coordinate values.")
                    errors += 1
                    error_types['invalid_coordinates'] += 1
                
                # Validate data lines
                for line in lines[2:]:
                    parts = line.strip().split()
                    if len(parts) < 34:
                        print(f"Error in {filename}: Data line has missing values. First three values: {parts[:3]}")
                        errors += 1
                        error_types['missing_values'] += 1
                        continue
                    
                    parts[0]
                    try:
                        year = int(parts[1])
                        month = int(parts[2])
                    except ValueError:
                        print(f"Error in {filename}: Invalid year or month. First three values: {parts[:3]}")
                        errors += 1
                        error_types['invalid_data_value'] += 1
                        continue
                    
                    data = parts[3:]
                    
                    if year < 2006 or year > 2100:
                        print(f"Error in {filename}: Year {year} is out of range. First three values: {parts[:3]}")
                        errors += 1
                        error_types['year_out_of_range'] += 1
                    
                    if month < 1 or month > 12:
                        print(f"Error in {filename}: Month {month} is out of range. First three values: {parts[:3]}")
                        errors += 1
                        error_types['month_out_of_range'] += 1
                    
                    # Validate days in month
                    if month == 2:
                        days_in_month = 29 if is_bisextile(year) else 28
                    elif month in [4, 6, 9, 11]:
                        days_in_month = 30
                    else:
                        days_in_month = 31
                    
                    if len(data) != days_in_month:
                        print(f"Error in {filename}: Data for month {month} has incorrect number of days. Expected {days_in_month}, found {len(data)}. First three values: {parts[:3]}")
                        errors += 1
                        error_types['incorrect_days'] += 1
                    
                    # Validate data values (checking for integer values or '-999')
                    for value in data:
                        if value != '-999':
                            try:
                                int(value)  # Try converting to int
                            except ValueError:
                                print(f"Error in {filename}: Invalid data value {value}. First three values: {parts[:3]}")
                                errors += 1
                                error_types['invalid_data_value'] += 1

    print(f"Total errors found: {errors}")
    for error_type, count in error_types.items():
        print(f"{error_type}: {count}")

# Directory containing the .dat files
directory = '/workspaces/TA06/E01/workspacesTA06E01ayuda1'
validate_dat_files(directory)
