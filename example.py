from llama_cleanup.main import AddressLookup

address_lookup = AddressLookup(
    canadian_postal_codes_path="/path/to/CanadianPostalCodes202403.csv",
    us_zip_codes_path="/path/to/USZIPCodes202409.csv",
    llama_model="llama3.1"
)

# Test the lookup method
result = address_lookup.lookup("789 Maple Dr., 2nd floor, Toronto, ON, M5V3L5")
print(result)

"""
Example Output:
{'city': 'Toronto', 'state_full': 'Ontario', 'latitude': np.float64(43.688438), 'longitude': np.float64(-79.307762), 'country': 'Canada'}
"""

"""
# For a remote model:

address_lookup = AddressLookup(
    canadian_postal_codes_path="/path/to/CanadianPostalCodes202403.csv",
    us_zip_codes_path="/path/to/USZIPCodes202409.csv",
    llama_model="gemma:2b",  # The model on the remote server
    remote=True,  # Enable remote
    remote_api_base="",  # Remote API base URL
    remote_api_key="your_api_key_here"  # Optional API key for authentication
)

result = address_lookup.lookup("456 Pine St New York, NY, USA")
print(result)

"""
