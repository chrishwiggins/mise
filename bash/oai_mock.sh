#!/bin/bash

# Read the input filename from the command line
if [ $# -eq 0 ]; then
  echo "Usage: $0 input_file" >&2
  exit 1
fi

input_file=$1

# Check that the input file exists
if [ ! -f "$input_file" ]; then
  echo "Error: input file not found" >&2
  exit 1
fi

# Read the prompt from the input file
prompt=$(cat "$input_file")

# Escape the input using jq to handle special characters
escaped_input=$(printf '%s' "$prompt" | jq -Rs '.')

# Create a temporary file to store the JSON data
json_file="/tmp/oai_json_$$.json"

# Write the JSON data to the temporary file
cat > "${json_file}" <<EOF
{
  "model": "gpt-3.5-turbo",
  "messages": [
    {
      "role": "user",
      "content": ${escaped_input}
    }
  ]
}
EOF

#  "options": {
#    "temperature": 0.8,
#    "max_tokens": 100
#  }

# Save the API request JSON data for debugging purposes
# cp "${json_file}" "/tmp/oai_`date +%s`.in"

# Execute the curl request with the JSON data from the temporary file
# The curl output is stored in a temporary file
curl_output_file="/tmp/curl_output_$$.txt"
api_response_file="/tmp/api_response_$$.json"
curl --verbose --location --request POST 'https://api.openai.com/v1/chat/completions' \
--header 'Authorization: Bearer sk-KEY' \
--header 'Content-Type: application/json' \
--data "@${json_file}" 2> >(grep -v Bearer > "${curl_output_file}") > "${api_response_file}"

# Save the curl verbose output (without the API key) for debugging purposes
# cp "${curl_output_file}" "/tmp/curl_output_`date +%s`.txt"

# Save the complete API response for debugging purposes
# cp "${api_response_file}" "/tmp/api_response_`date +%s`.json"

# Process the output with jq to extract the content
output=$(cat "${api_response_file}" | jq '.choices[].message.content')

# Remove escape sequences, quotes, and other formatting
echo "${output}" | sed -e 's/\\n/\n/g' -e 's/\\"/"/g' -e 's/^"//' -e 's/"$//' > /tmp/oai_$$.out
fold -s -b -w 65 < /tmp/oai_$$.out

echo "ein:" $input_file
echo "aus:" /tmp/oai_$$.out

# Save the processed output for debugging purposes
# cp "/tmp/oai_$$.out" "/tmp/oai_`date +%s`.out"
 
 
# change to
# {
#  "messages": [
#    {"role": "system", "content": "Your system message here"},
#    {"role": "user", "content": "Your user message here"}
#  ],
#  "options": {
#    "temperature": 0.8,
#    "max_tokens": 100
#  }
#}

