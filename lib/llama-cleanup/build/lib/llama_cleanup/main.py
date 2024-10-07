import re
import json
import pandas as pd
import numpy as np
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI  # Import for remote model

class AddressLookup:
    def __init__(self, canadian_postal_codes_path, us_zip_codes_path, llama_model, remote=False, remote_api_base=None, remote_api_key=None):
        """
        Initializes the AddressLookup class with paths to CSV files and the model version.

        Args:
            canadian_postal_codes_path (str): Path to the Canadian postal codes CSV file.
            us_zip_codes_path (str): Path to the U.S. zip codes CSV file.
            llama_model (str): The version of the Llama model to use.
            remote (bool): Whether to use a remote Llama server. Defaults to False (local).
            remote_api_base (str): The base URL for the remote Llama API (if remote=True).
            remote_api_key (str): The API key for the remote Llama server (if required).
        """
        self.canadian_postal_codes = pd.read_csv(canadian_postal_codes_path)
        self.us_zip_codes = pd.read_csv(us_zip_codes_path)
        
        # Determine whether to use local or remote Llama model
        self.remote = remote
        if not remote:
            # Local Llama model
            self.llm = OllamaLLM(model=llama_model)
        else:
            # Remote Llama model (using OpenAI API-like interface)
            if not remote_api_base or not llama_model:
                raise ValueError("For remote model, 'remote_api_base' and 'llama_model' must be provided.")
            
            self.llm = ChatOpenAI(
                openai_api_base=remote_api_base,  # Server IP/URL
                openai_api_key=remote_api_key or 'NA',  # Provide API key or 'NA' if not needed
                model_name=llama_model  # Model name on the server
            )

    def lookup_lat_long_canada(self, city, province_abbr):
        """
        Lookup latitude and longitude for Canadian addresses.

        Args:
            city (str): The city name.
            province_abbr (str): The province abbreviation.

        Returns:
            tuple: (latitude, longitude) or (None, None) if not found.
        """
        city = city.upper()
        result = self.canadian_postal_codes[
            (self.canadian_postal_codes['PROVINCE_ABBR'] == province_abbr) &
            (self.canadian_postal_codes['CITY'] == city)
        ]
        if not result.empty:
            latitude = np.float64(result.iloc[0]['LATITUDE'])
            longitude = np.float64(result.iloc[0]['LONGITUDE'])
            return latitude, longitude
        else:
            print(f"No match found for City: {city}, Province: {province_abbr} in Canadian CSV.")
            return None, None

    def lookup_lat_long_us(self, city, state_abbr):
        """
        Lookup latitude and longitude for U.S. addresses.

        Args:
            city (str): The city name.
            state_abbr (str): The state abbreviation.

        Returns:
            tuple: (latitude, longitude) or (None, None) if not found.
        """
        city = city.upper()
        result = self.us_zip_codes[
            (self.us_zip_codes['State'] == state_abbr) &
            (self.us_zip_codes['City'] == city)
        ]
        if not result.empty:
            latitude = np.float64(result.iloc[0]['ZipLatitude'])
            longitude = np.float64(result.iloc[0]['ZipLongitude'])
            return latitude, longitude
        else:
            print(f"No match found for City: {city}, State: {state_abbr} in U.S. CSV.")
            return None, None

    def lookup(self, address):
        """
        Cleans up an address string and provides city, state, latitude, longitude, and country.

        Args:
            address (str): The address string to process.

        Returns:
            dict: Dictionary with 'city', 'state_full', 'latitude', 'longitude', and 'country', or None if failed.
        """
        # Create the prompt
        prompt = (
            f"Extract the City, State or Province, from the following address: '{address}'. Based on the City and State or Province determine the country. If the country is Canada write Canada, if the country is America write America. Write the State in full form, no abbreviations. Also determine the abbreviation of the state or province."
            "Return the result in JSON format with keys 'city', 'state_or_province', 'state_or_province_abbreviation' and 'country'. "
            "Only output the JSON object. Do not include any explanatory text."
        )

        # Invoke either local or remote Llama model
        if not self.remote:
            response = self.llm.invoke(prompt)  # Local invocation
        else:
            response = self.llm({"prompt": prompt})  # Remote invocation

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
                    latitude, longitude = self.lookup_lat_long_canada(city, state_abbr)
                elif country == 'America':
                    latitude, longitude = self.lookup_lat_long_us(city, state_abbr)
                else:
                    latitude, longitude = None, None

                # Return the result in the desired format
                if latitude is not None and longitude is not None:
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

