import re
import json
import pandas as pd
from langchain_ollama import OllamaLLM  # Ensure this is correctly imported

# Function to lookup latitude and longitude based on city and province/state for Canadian addresses
def lookup_lat_long_canada(city, province_abbr, canadian_postal_codes):
    city = city.upper()

    # Search in the Canadian postal codes data
    result = canadian_postal_codes[
        (canadian_postal_codes['PROVINCE_ABBR'] == province_abbr) &
        (canadian_postal_codes['CITY'] == city)
    ]
    if not result.empty:
        latitude = result.iloc[0]['LATITUDE']
        longitude = result.iloc[0]['LONGITUDE']
        return latitude, longitude
    else:
        print(f"No match found for City: {city}, Province: {province_abbr} in Canadian CSV.")
        return None, None

# Function to lookup latitude and longitude based on city and state for U.S. addresses
def lookup_lat_long_us(city, state_abbr, us_zip_codes):
    city = city.upper()

    # Search in the U.S. zip codes data
    result = us_zip_codes[
        (us_zip_codes['State'] == state_abbr) &
        (us_zip_codes['City'] == city)
    ]
    if not result.empty:
        latitude = result.iloc[0]['ZipLatitude']
        longitude = result.iloc[0]['ZipLongitude']
        return latitude, longitude
    else:
        print(f"No match found for City: {city}, State: {state_abbr} in U.S. CSV.")
        return None, None

# Function to process a single address
def process_single_address(address, llama_model, canadian_postal_codes_path, us_zip_codes_path):
    canadian_postal_codes = pd.read_csv(canadian_postal_codes_path)
    us_zip_codes = pd.read_csv(us_zip_codes_path)
    llm = OllamaLLM(model=llama_model)

    # Prompt to get city, state, and country in JSON format
    prompt = (
        f"Extract the City, State or Province, from the following address: '{address}'. Based on the City and State or Province determine the country. If the country is Canada write Canada, if the country is America write America. Write the State in full form, no abbreviations. Also determine the abbreviation of the state or province."
        "Return the result in JSON format with keys 'city', 'state_or_province', 'state_or_province_abbreviation' and 'country'. "
        "Only output the JSON object. Do not include any explanatory text."
    )
    response = llm.invoke(prompt)

    # Extract JSON object from the response
    json_match = re.search(r'\{.*?\}', response, re.DOTALL)
    if json_match:
        json_text = json_match.group(0)
        try:
            data = json.loads(json_text)
            
            # Get the details
            city = data['city']
            state_full = data['state_or_province']  # Use the full name of the state/province
            state_abbr = data['state_or_province_abbreviation']
            country = data['country']

            # Perform the lookup based on the country
            if country == 'Canada':
                latitude, longitude = lookup_lat_long_canada(city, state_abbr, canadian_postal_codes)
            elif country == 'America':
                latitude, longitude = lookup_lat_long_us(city, state_abbr, us_zip_codes)
            else:
                latitude, longitude = None, None

            # Check for failed lookups
            if latitude is not None and longitude is not None:
                output_line = f"{city} / {state_full} / {latitude} / {longitude}"
                print(output_line)
                return {
                    'city': city,
                    'state_full': state_full,
                    'latitude': latitude,
                    'longitude': longitude,
                    'country': country
                }
            else:
                print(f"Failed to find coordinates for: {city} / {state_full}")
                return None

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON object: {e}")
            return None
    else:
        print(f"No JSON object found in Llama response: {response}")
        return None

# Example usage of the function
if __name__ == "__main__":
    # Define the Llama model and CSV paths
    llama_model = "llama3.1"
    canadian_postal_codes_path = "CanadianPostalCodes202403.csv"
    us_zip_codes_path = "USZIPCodes202409.csv"
    
    # Example address
    address = "789 Maple Dr., 2nd floor, Toronto, ON, M5V3L5"
    
    # Process the address
    result = process_single_address(address, llama_model, canadian_postal_codes_path, us_zip_codes_path)
    
    if result:
        print(f"Processed result: {result}")
