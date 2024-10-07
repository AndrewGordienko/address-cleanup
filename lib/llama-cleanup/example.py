from llama_cleanup.main import AddressLookup

address_lookup = AddressLookup(
    canadian_postal_codes_path="CanadianPostalCodes202403.csv",
    us_zip_codes_path="USZIPCodes202409.csv",
    llama_model="llama3.2:1b"
)

# Test the lookup method
result = address_lookup.lookup("789 Maple Dr., 2nd floor, SAINT-JÉRÔME, Quebec, M5V3L5")
print(result)
