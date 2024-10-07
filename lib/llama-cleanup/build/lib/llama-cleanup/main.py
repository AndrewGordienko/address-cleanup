import re
import json
import pandas as pd
from langchain_ollama import OllamaLLM

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

# Function to process addresses and get city, province/state, and country in JSON format
def process_addresses(canadian_postal_codes_path, us_zip_codes_path, llama_model, input_file, output_file):
    failed_lookups = []  # To track failed lookups

    # Load the Canadian and US postal codes data
    canadian_postal_codes = pd.read_csv(canadian_postal_codes_path)
    us_zip_codes = pd.read_csv(us_zip_codes_path)
    
    # Initialize the Llama model
    llm = OllamaLLM(model=llama_model)

    with open(input_file, 'r') as file, open(output_file, 'w') as outfile:
        addresses = file.readlines()

        # Process each address
        for address in addresses:
            address = address.strip()
            print(f"Processing address: {address}")

            # Modified prompt to get city, state, and country in JSON format
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
                        outfile.write(output_line + "\n")  # Save the output to the file
                    else:
                        failed_lookups.append(f"{city} / {state_full}")

                except json.JSONDecodeError as e:
                    print(f"Failed to parse JSON object: {e}")
                    failed_lookups.append(address)  # Add to failed lookups list
                    continue  # Skip to next address
            else:
                print(f"No JSON object found in Llama response: {response}")
                failed_lookups.append(address)  # Add to failed lookups list
                continue  # Skip to next address

    # Print the failed lookups at the end
    if failed_lookups:
        print("\nFailed Lookups:")
        for failed in failed_lookups:
            print(failed)

if __name__ == "__main__":
    import argparse
    
    # Command-line arguments parser
    parser = argparse.ArgumentParser(description="Process addresses and lookup latitude/longitude.")
    
    # Add the necessary arguments
    parser.add_argument('--canadian_postal_codes_path', required=True, help="Path to the Canadian postal codes CSV file.")
    parser.add_argument('--us_zip_codes_path', required=True, help="Path to the US zip codes CSV file.")
    parser.add_argument('--llama_model', required=True, help="Llama model version to use.")
    parser.add_argument('--input_file', required=True, help="Input file with addresses.")
    parser.add_argument('--output_file', required=True, help="Output file to save the results.")

    # Parse the arguments
    args = parser.parse_args()

    # Call the function with the passed arguments
    process_addresses(
        args.canadian_postal_codes_path,
        args.us_zip_codes_path,
        args.llama_model,
        args.input_file,
        args.output_file
    )

