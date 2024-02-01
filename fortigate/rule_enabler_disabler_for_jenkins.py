import http.client
import json
import logging
import os

# Forti variables
FORTI_API_KEY = os.getenv('FORTIGATE_API_KEY')
FORTI_RULE_NAME = os.getenv('FORTI_RULE_NAME')
FORTI_URL = os.getenv('FORTI_URL')
RULES = "/api/v2/cmdb/firewall/policy"
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


def process_forti_response(response, data):
    if response.status == 200:
        policies = json.loads(data)
        for policy in policies.get("results", []):
            if policy.get("name") == FORTI_RULE_NAME:
                return policy.get("policyid")
    else:
        logging.error(f"Failed to retrieve policies: {response.status}")
        return None


def set_fortigate_rule(forti_conn, rule_id, status):
    rule = RULES + "/" + str(rule_id)
    forti_payload = json.dumps({"status": status})
    headers = {'Authorization': f'Bearer {FORTI_API_KEY}', 'Content-Type': 'application/json'}
    response, data = perform_api_call(forti_conn, "PUT", rule, forti_payload, headers)
    logging.info(data.decode("utf-8"))


def get_fortigate_rule_status(forti_conn, rule_id):
    rule = RULES + "/" + str(rule_id)
    headers = {'Authorization': f'Bearer {FORTI_API_KEY}', 'Content-Type': 'application/json'}
    response, data = perform_api_call(forti_conn, "GET", rule, headers=headers)
    rule_data = json.loads(data.decode("utf-8"))
    if 'results' in rule_data and isinstance(rule_data['results'], list):
        for policy in rule_data['results']:
            if policy.get('policyid') == rule_id:
                return policy.get('status', 'Unknown')
    return "Unknown"


try:
    # FortiGate Flow
    forti_conn = http.client.HTTPSConnection(FORTI_URL)
    headers = {'Authorization': f'Bearer {FORTI_API_KEY}', 'Content-Type': 'application/json'}
    response, data = perform_api_call(forti_conn, "GET", RULES, headers=headers)
    rule_id = process_forti_response(response, data)

    if rule_id:
        if CONNECTION_STATUS == 'status':
            rule_status = get_fortigate_rule_status(forti_conn, rule_id)
            logging.info(f"Rule Status: {rule_status}")
        else:
            set_fortigate_rule(forti_conn, rule_id, CONNECTION_STATUS)

    forti_conn.close()

except Exception as e:
    logging.error(f"An error occurred: {e}")
