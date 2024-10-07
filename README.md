<img src="https://github.com/user-attachments/assets/33fda36c-8414-4e3a-a040-ac1658ba8928" alt="Image description" width="300"/>
   
# Address Cleanup

This project provides a tool to process addresses and retrieve latitude and longitude based on city, state/province, and country information for both Canadian and U.S. addresses while cleaning out message noise. It uses data from postal code CSV files and a language model (`OllamaLLM`) to parse address components.

## Features

- Processes addresses from an input file and determines city, state/province, and country.
- Retrieves latitude and longitude based on city and state/province for Canadian and U.S. addresses using postal code datasets.
- Utilizes a language model (`OllamaLLM`) to extract city and state information from address strings.
- Outputs the result in the format: `City / State or Province / Latitude / Longitude`.
- Handles and logs failed lookups for further investigation.

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/AndrewGordienko/address-cleanup
   cd address-cleanup
   ```

2. **Install the required dependencies:**

   Make sure you have Python 3.8+ installed, then install the necessary packages using the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

3. **Prepare the postal code data:**

   - Unzip the `postal_codes.zip` file and extract its contents.
   - Ensure the extracted CSV files for Canadian and U.S. postal codes are placed in the specified directory (as defined in the `config.json` file).

4. **Set up the configuration:**

   - Edit the `config.json` file to match your setup. Example:
   
     ```json
     {
        "canadian_postal_codes_path": "CanadianPostalCodes202403.csv",
        "us_zip_codes_path": "USZIPCodes202409.csv",
        "llama_model": "llama3.1",
        "input_file": "messy.txt",
        "output_file": "output.txt"
      }
     ```

## Usage

Once everything is set up, you can run the script to process the addresses and retrieve latitude and longitude information:

```bash
python main.py
```

This will:

- Read the addresses from the input file (defined in `config.json`).
- Use the language model to extract city, state/province, and country from each address.
- Look up the latitude and longitude for the corresponding city and state.
- Save the results in the output file.

### Example Address File (`input_addresses.txt`)

```
789 Maple Dr., 2nd floor, Toronto, ON, M5V3L5
456 Pine St New York, NY, USA
12 Elm Street Vancouver BC V6B
105 River Blvd, Montreal QC H3B2Y
800 King Road, apt 3A, Chicago IL, buzzer 176
300 Oak Street, Dallas, Texas 75201
567 Park Ave, Suite #2, Calgary, AB T2P
23 Cedar Way, San Francisco, CA
890 Birch Ln, Ottawa, Ontario
210 Spruce Ave. Los Angeles, CA, USA
```

### Example Output (`output_results.txt`)

```
Toronto / Ontario / 43.688438 / -79.307762
New York / New York / 40.7508 / -73.996122
Vancouver / British Columbia / 49.227382 / -123.128265
Montreal / Quebec / 45.559978 / -73.608679
Chicago / Illinois / 41.88502 / -87.622387
Dallas / Texas / 32.787706 / -96.79985
Calgary / Alberta / 51.039352 / -114.093224
San Francisco / California / 37.779392 / -122.417738
Ottawa / Ontario / 45.358469 / -75.644724
Los Angeles / California / 33.973593 / -118.247897
```

## Handling Failed Lookups

Addresses that could not be parsed or matched to a postal code will be logged at the end of the output. You can inspect these addresses for errors or missing data.

## Configuration Details

The `config.json` file contains paths to necessary resources:

- `canadian_postal_codes_path`: Path to the CSV file containing Canadian postal codes.
- `us_zip_codes_path`: Path to the CSV file containing U.S. postal codes.
- `llama_model`: Name of the model used by `OllamaLLM` for processing addresses.
- `input_file`: Path to the file containing the list of addresses to process.
- `output_file`: Path to the file where results will be saved.

## Using as a Library

This project is also available as a Python library. You can install it via pip:

```bash
pip install llama-cleanup
```

### Example Usage:

```python
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
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
