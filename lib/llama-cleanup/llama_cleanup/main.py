import re
import json
import unicodedata  # For handling accents
import pandas as pd
import numpy as np
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI  # Import for remote model
from spellchecker import SpellChecker  # Corrected import
from thefuzz import process

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
        
        # Initialize spell checker with custom dictionary
        canadian_cities = self.canadian_postal_codes['CITY'].dropna().unique().tolist()
        us_cities = self.us_zip_codes['City'].dropna().unique().tolist()
        all_cities = set([city.lower() for city in canadian_cities + us_cities])

        self.spell_checker = SpellChecker()
        self.spell_checker.word_frequency.load_words(all_cities)

        # Mapping of full state/province names to abbreviations
        self.state_province_abbreviations = self._load_state_province_abbreviations()

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

    def _load_state_province_abbreviations(self):
        # Define mappings for Canadian provinces and US states
        province_abbreviations = {
            # Canadian provinces and territories
            'ALBERTA': 'AB',
            'BRITISH COLUMBIA': 'BC',
            'MANITOBA': 'MB',
            'NEW BRUNSWICK': 'NB',
            'NEWFOUNDLAND AND LABRADOR': 'NL',
            'NOVA SCOTIA': 'NS',
            'ONTARIO': 'ON',
            'PRINCE EDWARD ISLAND': 'PE',
            'QUEBEC': 'QC',
            'SASKATCHEWAN': 'SK',
            'NORTHWEST TERRITORIES': 'NT',
            'NUNAVUT': 'NU',
            'YUKON': 'YT',
            # US states
            'ALABAMA': 'AL',
            'ALASKA': 'AK',
            'ARIZONA': 'AZ',
            'ARKANSAS': 'AR',
            'CALIFORNIA': 'CA',
            'COLORADO': 'CO',
            'CONNECTICUT': 'CT',
            'DELAWARE': 'DE',
            'FLORIDA': 'FL',
            'GEORGIA': 'GA',
            'HAWAII': 'HI',
            'IDAHO': 'ID',
            'ILLINOIS': 'IL',
            'INDIANA': 'IN',
            'IOWA': 'IA',
            'KANSAS': 'KS',
            'KENTUCKY': 'KY',
            'LOUISIANA': 'LA',
            'MAINE': 'ME',
            'MARYLAND': 'MD',
            'MASSACHUSETTS': 'MA',
            'MICHIGAN': 'MI',
            'MINNESOTA': 'MN',
            'MISSISSIPPI': 'MS',
            'MISSOURI': 'MO',
            'MONTANA': 'MT',
            'NEBRASKA': 'NE',
            'NEVADA': 'NV',
            'NEW HAMPSHIRE': 'NH',
            'NEW JERSEY': 'NJ',
            'NEW MEXICO': 'NM',
            'NEW YORK': 'NY',
            'NORTH CAROLINA': 'NC',
            'NORTH DAKOTA': 'ND',
            'OHIO': 'OH',
            'OKLAHOMA': 'OK',
            'OREGON': 'OR',
            'PENNSYLVANIA': 'PA',
            'RHODE ISLAND': 'RI',
            'SOUTH CAROLINA': 'SC',
            'SOUTH DAKOTA': 'SD',
            'TENNESSEE': 'TN',
            'TEXAS': 'TX',
            'UTAH': 'UT',
            'VERMONT': 'VT',
            'VIRGINIA': 'VA',
            'WASHINGTON': 'WA',
            'WEST VIRGINIA': 'WV',
            'WISCONSIN': 'WI',
            'WYOMING': 'WY',
            # District of Columbia
            'DISTRICT OF COLUMBIA': 'DC',
        }
        return province_abbreviations

    def correct_spelling(self, word):
        if word is None:
            return None
        # Normalize accents before spelling correction
        word_normalized = unicodedata.normalize('NFKD', word).encode('ASCII', 'ignore').decode('utf-8')
        corrected = self.spell_checker.correction(word_normalized.lower())
        return corrected.title() if corrected else word_normalized

    def fuzzy_city_lookup(self, city, cities_list):
        if city is None or len(cities_list) == 0:
            return city
        best_match = process.extractOne(city, cities_list)
        if best_match and best_match[1] > 80:  # Confidence threshold
            return best_match[0]
        else:
            return city  # Return the original city if no good match is found

    def clean_address(self, address):
        if address is None:
            return ''
        return re.sub(r'[^A-Za-z0-9 ,.-]+', ' ', address)

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
        province_abbr = province_abbr.upper()
        cities_in_province = self.canadian_postal_codes[
            self.canadian_postal_codes['PROVINCE_ABBR'] == province_abbr
        ]['CITY'].unique()
        city = self.correct_spelling(city)
        city = self.fuzzy_city_lookup(city, cities_in_province)

        result = self.canadian_postal_codes[
            (self.canadian_postal_codes['PROVINCE_ABBR'] == province_abbr) &
            (self.canadian_postal_codes['CITY'] == city)
        ]
        if not result.empty:
            latitude = float(result.iloc[0]['LATITUDE'])
            longitude = float(result.iloc[0]['LONGITUDE'])
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
        state_abbr = state_abbr.upper()
        cities_in_state = self.us_zip_codes[
            self.us_zip_codes['State'] == state_abbr
        ]['City'].unique()
        city = self.correct_spelling(city)
        city = self.fuzzy_city_lookup(city, cities_in_state)

        result = self.us_zip_codes[
            (self.us_zip_codes['State'] == state_abbr) &
            (self.us_zip_codes['City'] == city)
        ]
        if not result.empty:
            latitude = float(result.iloc[0]['ZipLatitude'])
            longitude = float(result.iloc[0]['ZipLongitude'])
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
        address = self.clean_address(address)
        prompt = (
            f"Extract the following information from the address: '{address}'. "
            "1. 'city' (ensure correct spelling), "
            "2. 'state_or_province' (full name), "
            "3. 'state_or_province_abbreviation', "
            "4. 'country' (either 'Canada' or 'America'. State the country in this exact format.). "
            "Ensure that none of the values are null or missing. "
            "If any information is uncertain, make the best guess based on the address provided. "
            "Return the result strictly in JSON format with these keys: "
            "'city', 'state_or_province', 'state_or_province_abbreviation', 'country'. "
            "Do not include any explanatory text."
        )

        try:
            if not self.remote:
                response = self.llm.invoke(prompt)  # Local invocation
            else:
                response = self.llm({"prompt": prompt})  # Remote invocation

            # Extract JSON object from the response
            json_match = re.search(r'\{.*?\}', response, re.DOTALL)
            if json_match:
                json_text = json_match.group(0)
                data = json.loads(json_text)

                # Ensure all required keys are present
                required_keys = {'city', 'state_or_province', 'state_or_province_abbreviation', 'country'}
                if not required_keys.issubset(data.keys()):
                    missing_keys = required_keys - data.keys()
                    print(f"Missing keys in JSON response: {missing_keys}")
                    return None

                # If 'state_or_province_abbreviation' is None, try to derive it
                if data['state_or_province_abbreviation'] is None and data['state_or_province']:
                    state_full = data['state_or_province'].upper()
                    data['state_or_province_abbreviation'] = self.state_province_abbreviations.get(state_full)
                    if data['state_or_province_abbreviation'] is None:
                        print(f"Could not find abbreviation for state/province: {state_full}")
                        return None

                if any(data[key] is None for key in required_keys):
                    print(f"One or more required fields are None in the response: {data}")
                    return None

                city = self.correct_spelling(data['city'])
                state_full = data['state_or_province']
                state_abbr = data['state_or_province_abbreviation']
                country = data['country']

                if country == 'Canada':
                    latitude, longitude = self.lookup_lat_long_canada(city, state_abbr)
                elif country == 'America':
                    latitude, longitude = self.lookup_lat_long_us(city, state_abbr)
                else:
                    print(f"Unknown country: {country}")
                    return None

                if latitude is not None and longitude is not None:
                    return {
                        'city': city,
                        'state_full': state_full,
                        'latitude': latitude,
                        'longitude': longitude
                    }
                else:
                    print(f"Failed to find coordinates for: {city} / {state_full}")
                    return None

            else:
                print(f"No JSON object found in Llama response: {response}")
                return None

        except Exception as e:
            print(f"An error occurred during lookup: {e}")
            return None

