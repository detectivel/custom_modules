import http.client
import json
import base64
import logging
import os

# vCenter variables
VCENTER_USERNAME = os.getenv('VCENTER_USERNAME')
VCENTER_PASSWORD = os.getenv('VCENTER_PASSWORD')
VCENTER_URL = os.getenv('VCENTER_URL')
REQUEST_URL = f"https://{VCENTER_URL}/api/vcenter/vm/"
VM_NAME = os.getenv('VM_NAME')
CONNECTION_STATUS = os.getenv('STATUS')

# Setup Logging
logging.basicConfig(level=logging.INFO)


def perform_api_call(conn, method, url, body=None, headers=None):
    try:
        conn.request(method, url, body=body, headers=headers)
        response = conn.getresponse()
        data = response.read()
        return response, data
    except Exception as e:
        logging.error(f"API call error: {e}")
        raise


def encode_credentials(username, password):
    credentials = f'{username}:{password}'
    return base64.b64encode(credentials.encode()).decode()


def manage_vcenter_vm(vcenter_conn, session_token, vm_name, status):
    headers_with_token = {'vmware-api-session-id': session_token}
    response, data = perform_api_call(vcenter_conn, "GET", "/rest/vcenter/vm", headers=headers_with_token)
    data_dict = json.loads(data.decode("utf-8"))

    for vm in data_dict['value']:
        if vm['name'] == vm_name:
            if status == 'enable':
                vm_on = REQUEST_URL + str(vm['vm']) + "/power?action=start"
                perform_api_call(vcenter_conn, "POST", vm_on, headers=headers_with_token)
            elif status == 'disable':
                vm_off = REQUEST_URL + str(vm['vm']) + "/guest/power?action=shutdown"
                perform_api_call(vcenter_conn, "POST", vm_off, headers=headers_with_token)
            elif status == 'status':
                vm_itself = REQUEST_URL + str(vm['vm'])
                response, vm_data = perform_api_call(vcenter_conn, "GET", vm_itself, headers=headers_with_token)
                vm_info = json.loads(vm_data.decode("utf-8"))
                logging.info(f"VM Name: {vm_info['name']}, Power State: {vm_info['power_state']}")
            break


try:
    # vCenter Flow
    vcenter_conn = http.client.HTTPSConnection(VCENTER_URL)
    encoded_credentials = encode_credentials(VCENTER_USERNAME, VCENTER_PASSWORD)
    headers = {'Authorization': f'Basic {encoded_credentials}'}
    response, data = perform_api_call(vcenter_conn, "POST", "/rest/com/vmware/cis/session", headers=headers)
    session_token = json.loads(data.decode("utf-8"))['value']
    manage_vcenter_vm(vcenter_conn, session_token, VM_NAME, CONNECTION_STATUS)
    vcenter_conn.close()

except Exception as e:
    logging.error(f"An error occurred: {e}")
