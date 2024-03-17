import requests
import json

# Replace these variables with your actual data
FORTIGATE_IP = 'YOUR_FORTIGATE_IP'
API_TOKEN = 'FORTIGATE_API_TOKEN'
CA = 'PATH_TO_CA_FILE'
SUBNET = "10.0.0."
DOMAIN = 'example.com'  # my domain in DNS server in Fortigate
RECORD_TO_CREATE = 'test-record'  # subdomain/record
HOST_END_IP = 13  # the host address

# Fortigate API URL components
base_url = f"https://{FORTIGATE_IP}/api/v2/cmdb"
dns_db_url = f"{base_url}/system/dns-database"
dns_record_url = f"{dns_db_url}/{DOMAIN}"  # Adjusted to target the specific domain's DNS database

# Headers for the request
headers = {
    'Authorization': f'Bearer {API_TOKEN}',
    'Content-Type': 'application/json'
}


def add_dns_record(subnet, ip, record):
    # New DNS record to add
    new_dns_record = {
        "status": "enable",
        "type": "A",
        "ttl": 60,  # Adjust TTL as needed
        "ip": f"{subnet}{ip}",  # The IP address for the new record
        "hostname": f"www.{record}",  # The hostname for the new record
    }

    # First, fetch the current DNS database to get existing entries
    response = requests.get(dns_record_url, headers=headers, verify=CA)
    if response.status_code == 200:
        dns_database = response.json()
        existing_entries = dns_database['results'][0]['dns-entry']
        # Add the new record to existing entries
        existing_entries.append(new_dns_record)
        # Prepare the updated database object
        updated_dns_database = {
            "dns-entry": existing_entries
        }
        # Send the update request
        update_response = requests.put(
            dns_record_url,
            headers=headers,
            data=json.dumps(updated_dns_database),
            verify=CA)
        if update_response.status_code == 200:
            print("DNS record added successfully.")
        else:
            print(
                f"Failed to add DNS record. Status code: {update_response.status_code}, "
                f"Response: {update_response.text}")
    else:
        print(f""
              f"Failed to fetch current DNS database. Status code: {response.status_code}, "
              f"Response: {response.text}")


# Call the functions

add_dns_record(SUBNET, HOST_END_IP, RECORD_TO_CREATE)
