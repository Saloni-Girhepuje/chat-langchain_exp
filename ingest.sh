#Code by Langchain

# Bash script to ingest data
# This involves scraping the data from the web and then cleaning up and putting in Weaviate.
# Error if any command fails
#set -e
#wget -r -A.html https://langchain.readthedocs.io/en/latest/
#python3 ingest.py


#Our Modified Code

#!/bin/bash

# Set the directory path
dir_path="/Users/yellow/Documents/Code/Alcade/Alcade/Alcade/Story/"

# Loop over all files in the directory
for file in "$dir_path"*
do
  # Check if the file is a PDF
  if [[ $file == *.pdf ]]
  then
    echo "Processing $file"
    python3 ingest.py "$file"
    # Add your processing commands here. For example:
    # python3 ingest.py "$file"
    # python3 ingest_examples.py "$file"
  fi
done