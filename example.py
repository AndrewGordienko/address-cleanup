from llama_cleanup.main import AddressLookup

# Initialize the class and use it
address_lookup = AddressLookup(
    canadian_postal_codes_path="CanadianPostalCodes202403.csv",
    us_zip_codes_path="USZIPCodes202409.csv",
    llama_model="llama3.1"
)

# Test the lookup method
result = address_lookup.lookup("789 Maple Dr., 2nd floor, Toronto, ON, M5V3L5")
print(result)

"""
Example Output:
{'city': 'Toronto', 'state_full': 'Ontario', 'latitude': np.float64(43.688438), 'longitude': np.float64(-79.307762), 'country': 'Canada'}
"""
