import llama_cleanup.main as mp

# Define the paths for the CSV files, Llama model, input, and output
canadian_postal_codes_path = "CanadianPostalCodes202403.csv"
us_zip_codes_path = "USZIPCodes202409.csv"
llama_model = "llama3.1"
input_file = "messy.txt"
output_file = "output.txt"

# Call the process_addresses function from your package
mp.process_addresses(
    canadian_postal_codes_path,
    us_zip_codes_path,
    llama_model,
    input_file,
    output_file
)

print(f"Processed addresses and saved results to {output_file}")
