import requests
import json

# Replace these variables with your actual data
fortigate_ip = 'YOUR_FORTIGATE_IP'
api_token = 'FORTIGATE_API_TOKEN'
CA = 'PATH_TO_CA_FILE'
domain = 'example.com'  # my domain in DNS server in Fortigate

# Fortigate API URL components
base_url = f"https://{fortigate_ip}/api/v2/cmdb"
dns_db_url = f"{base_url}/system/dns-database"
dns_record_url = f"{dns_db_url}/{domain}"  # Adjusted to target the specific domain's DNS database

# Headers for the request
headers = {
    'Authorization': f'Bearer {api_token}',
    'Content-Type': 'application/json'
}


# Function to view all DNS records for the domain
def view_dns_records():
    response = requests.get(dns_record_url, headers=headers, verify=CA)
    if response.status_code == 200:
        dns_database = response.json()
        existing_entries = dns_database['results'][0]['dns-entry']

        print("Current DNS records:")
        if existing_entries:
            for entry in existing_entries:
                print(
                    f"ID: {entry.get('id')}, "
                    f"Type: {entry.get('type')}, "
                    f"IP: {entry.get('ip')}, "
                    f"Hostname: {entry.get('hostname')}")
        else:
            print("No DNS records found.")
    else:
        print(f"Failed to fetch DNS records. Status code: {response.status_code}, Response: {response.text}")
