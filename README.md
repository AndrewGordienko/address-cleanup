
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
   git clone https://github.com/yourusername/address-latlong-lookup.git
   cd address-latlong-lookup
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
       "canadian_postal_codes_path": "path/to/canadian_postal_codes.csv",
       "us_zip_codes_path": "path/to/us_zip_codes.csv",
       "input_file": "path/to/input_addresses.txt",
       "output_file": "path/to/output_results.txt",
       "llama_model": "your_llama_model_name"
     }
     ```

## Usage

Once everything is set up, you can run the script to process the addresses and retrieve latitude and longitude information:

```bash
python address_latlong_lookup.py
```

This will:

- Read the addresses from the input file (defined in `config.json`).
- Use the language model to extract city, state/province, and country from each address.
- Look up the latitude and longitude for the corresponding city and state.
- Save the results in the output file.

### Example Address File (`input_addresses.txt`)

```
123 Main St, Vancouver, BC
456 Elm St, Seattle, WA
```

### Example Output (`output_results.txt`)

```
Vancouver / British Columbia / 49.2827 / -123.1207
Seattle / Washington / 47.6062 / -122.3321
```

## Handling Failed Lookups

Addresses that could not be parsed or matched to a postal code will be logged at the end of the output. You can inspect these addresses for errors or missing data.

## Configuration Details

The `config.json` file contains paths to necessary resources:

- `canadian_postal_codes_path`: Path to the CSV file containing Canadian postal codes.
- `us_zip_codes_path`: Path to the CSV file containing U.S. postal codes.
- `input_file`: Path to the file containing the list of addresses to process.
- `output_file`: Path to the file where results will be saved.
- `llama_model`: Name of the model used by `OllamaLLM` for processing addresses.

## Contributing

1. Fork the repository.
2. Create a new branch for your feature (`git checkout -b feature-branch`).
3. Make your changes and commit them (`git commit -am 'Add new feature'`).
4. Push to the branch (`git push origin feature-branch`).
5. Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
