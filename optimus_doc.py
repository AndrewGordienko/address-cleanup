from optimus_lookup import AddressLookup

# Paths to the Canadian and US postal code CSV files
canadian_csv_path = 'data/CanadianPostalCodes202403.csv'
us_csv_path = 'data/USZIPCodes202409.csv'

# Initialize the AddressLookup class with the paths to the CSV files
address_lookup = AddressLookup(canadian_csv=canadian_csv_path, us_csv=us_csv_path)

# Test with a single address
address = "789 Maple Dr., 2nd floor, Toronto, ON, M5V 3L5"
address = "456 Pine St New York, NY, USA"
predicted_city, predicted_province, latitude, longitude = address_lookup.lookup(address)

print(f"Input Address: {address}")
print(f"Predicted City: {predicted_city}")
print(f"Predicted Province/State: {predicted_province}")
print(f"Latitude: {latitude}")
print(f"Longitude: {longitude}")
print("-" * 50)

"""
Change to the directory where the distribution files are extracted.

cd optimus_lookup_dist
ls
You should see something like:
optimus_lookup-1.0.0-py3-none-any.whl
optimus-lookup-1.0.0.tar.gz

Install the Package Using pip
You can install the package using either the .whl (wheel) file or the .tar.gz (source distribution) file. Using the wheel file is generally faster and simpler.

Option A: Install Using the .whl File
pip install optimus_lookup-1.0.0-py3-none-any.whl

Option B: Install Using the .tar.gz File
pip install optimus-lookup-1.0.0.tar.gz
"""
