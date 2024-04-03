import requests
import json
import argparse

# Initialize parser
parser = argparse.ArgumentParser()

# Adding arguments
parser.add_argument("--fortigate_ip", required=True)
parser.add_argument("--api_token", required=True)
parser.add_argument("--CA", required=True)
parser.add_argument("--interface_name", required=True)
parser.add_argument("--action", required=True)

# Parse known args to determine the action first
args, unknown = parser.parse_known_args()

# Based on the action, require different arguments
if args.action == "create":
    parser.add_argument("--reservation_ip", required=True)
    parser.add_argument("--reservation_mac", required=True)
    parser.add_argument("--description", required=True)
elif args.action == "delete":
    parser.add_argument("--reservation_ip", required=True)
    parser.add_argument("--reservation_mac", required=False)
    parser.add_argument("--description", required=False)
elif args.action == "get":
    # For 'get', these arguments are not required
    parser.add_argument("--reservation_ip", required=False)
    parser.add_argument("--reservation_mac", required=False)
    parser.add_argument("--description", required=False)

# Re-parse the arguments with the new set of required/optional arguments
args = parser.parse_args()

# Configuration variables from arguments
fortigate_ip = args.fortigate_ip
api_token = args.api_token
CA = args.CA
interface_name = args.interface_name
action = args.action

# Optional arguments may not be present
reservation_ip = getattr(args, 'reservation_ip', None)
reservation_mac = getattr(args, 'reservation_mac', None)
description = getattr(args, 'description', None)


# Base URL and headers
base_url = f'https://{fortigate_ip}/api/v2/cmdb/system.dhcp/server/'
headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {api_token}'
}


# Function to get DHCP servers
def get_dhcp_servers():
    response = requests.get(f'{base_url}?access_token={api_token}', headers=headers, verify=CA)
    if response.status_code == 200:
        return response.json().get('results', [])
    else:
        print("Failed to retrieve DHCP servers from FortiGate. Status code:", response.status_code)
        return []


# Function to find a DHCP server for a specific interface
def find_dhcp_server(interface_name):
    for server in get_dhcp_servers():
        if server.get('interface') == interface_name:
            return server
    print(f"No DHCP server found for interface {interface_name}.")
    return None


# Function to create a DHCP reservation
def create_dhcp_reservation(server_id, ip, mac, description):
    data = json.dumps({
        'ip': ip,
        'mac': mac,
        'description': description
    })
    response = requests.post(f'{base_url}{server_id}/reserved-address/?access_token={api_token}',
                             headers=headers, data=data, verify=CA)
    if response.status_code in [200, 201]:
        print(f"DHCP reservation created successfully for IP: {ip}.")
    else:
        print(f"Failed to create DHCP reservation. Status code: {response.status_code}")


# Function to update a DHCP reservation
# def update_dhcp_reservation(server_id, reservation_id, new_ip, new_mac, new_description):
#     data = json.dumps({
#         'ip': new_ip,
#         'mac': new_mac,
#         'description': new_description
#     })
#     response = requests.put(f'{base_url}{server_id}/reserved-address/{reservation_id}/?access_token={api_token}',
#                             headers=headers,
#                             data=data,
#                             verify=CA)
#     if response.status_code in [200, 204]:
#         print(f"DHCP reservation {reservation_id} updated successfully to {new_ip}.")
#     else:
#         print(f"Failed to update DHCP reservation. Status code: {response.status_code}")


# Function to delete a DHCP reservation
def delete_dhcp_reservation(server_id, reservation_id):
    response = requests.delete(f'{base_url}{server_id}/reserved-address/{reservation_id}/?access_token={api_token}',
                               headers=headers, verify=CA)
    if response.status_code in [200, 204]:
        print(f"DHCP reservation {reservation_id} deleted successfully.")
    else:
        print(f"Failed to delete DHCP reservation. Status code: {response.status_code}")


def list_reservations(interface_name):
    server = find_dhcp_server(interface_name)
    if server:
        reservations = server.get('reserved-address', [])
        for reservation in reservations:
            print(f" - IP: {reservation.get('ip')}, "
                  f"MAC: {reservation.get('mac')}, "
                  f"Description: {reservation.get('description')}")


# Main logic to demonstrate usage of the functions
server = find_dhcp_server(interface_name)
# print(server)
print(f"The server ID: {server.get('id')} and it's IP address: {server.get('default-gateway')}\n"
      f"Start DHCP range: {server['ip-range'][0]['start-ip']}\n"
      f"End DHCP range: {server['ip-range'][0]['end-ip']}\n")

if action == "get":
    list_reservations(interface_name)

if action == "create":
    create_dhcp_reservation(server.get('id'), reservation_ip, reservation_mac, description)

# if operation == "update":
#     reservations = server.get('reserved-address', [])
#     for reservation in reservations:
#         if reservation.get('ip') == reservation_ip or reservation.get(
#                 'mac').lower() == reservation_mac.lower():
#             # print(reservation.get('id'))
#             update_dhcp_reservation(server.get('id'),
#                                     reservation.get('id'),
#                                     new_reservation_ip,
#                                     new_reservation_mac,
#                                     new_description)

if action == "delete":
    reservations = server.get('reserved-address', [])
    for reservation in reservations:
        if reservation.get('ip') == reservation_ip:
            delete_dhcp_reservation(server.get('id'), reservation.get('id'))
