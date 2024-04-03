import requests
import os
import json


ADMIN_USERNAME = os.getenv('CONF_USER')
ADMIN_PASSWORD = os.getenv('CONF_PASS')
CONFLUENCE_BASE_URL = os.getenv('CONF_URL')
CERT = os.getenv('CERT')
"""
This script fixes issue in Confluence 7.0.3 when the top navbar being disabled.
Plugins that are fixed is:
soyTemplateRendererHelperContext
velocity.helper
siteLogoHelperContext
"""

def make_get_request(endpoint, token=None):
    # Append the token to the URL if provided
    if token:
        endpoint += f"?token={token}"
    response = requests.get(
        f"{CONFLUENCE_BASE_URL}/rest/plugins/1.0/{endpoint}",
        auth=(ADMIN_USERNAME, ADMIN_PASSWORD),
        headers={'Accept': 'application/vnd.atl.plugins.installed+json'} if not token else {},
        verify=CERT
    )
    return response



def get_plugin_status(connection):
    try:
        if connection.ok:
            print("*****************************************")
            print("*****************************************")
            # Assume plugin_keys is defined
            try:
                for plugin_key in plugin_keys:
                    try:
                        response = make_get_request(plugin_key, UPM_TOKEN)
                        data = response.json()
                    except Exception as e:
                        print(f"Error fetching data for {plugin_key}: {e}")
                        continue  # Skip to the next plugin_key

                    plugin_name = plugin_key.split('/')
                    if 'enabled' in data and not data['enabled']:
                        print(f'"{plugin_name}" is disabled.')
                        print(f'Enabling plugin {plugin_name}')
                        if UPM_TOKEN:
                            try:
                                modified_data = fetch_and_modify_plugin_data(plugin_key)
                                if modified_data:
                                    update_plugin_module(plugin_key, modified_data)
                            except Exception as e:
                                print(f"Error modifying plugin data for {plugin_key}: {e}")
                    else:
                        print(f'The plugin "{plugin_name[-1]}" is enabled.')
            except Exception as e:
                print(f"Error processing plugins: {e}")
        else:
            print(f'Connection error: {connection}')
            raise Exception("Connection to the server failed.")
    except Exception as e:
        print(f"Unexpected error occurred: {e}")


def fetch_and_modify_plugin_data(plugin_key):
    """Fetch plugin data, modify it, and return the modified version."""
    plugin_name = plugin_key.split('/')
    try:
        try:
            response = requests.get(
                f"{CONFLUENCE_BASE_URL}/rest/plugins/1.0/{plugin_key}?token={UPM_TOKEN}",
                auth=(ADMIN_USERNAME, ADMIN_PASSWORD),
                verify=CERT
            )
        except requests.exceptions.RequestException as e:
            print(f"HTTP request error for {plugin_name[-1]}: {e}")
            return None

        if response.ok:
            try:
                data = response.json()
            except json.JSONDecodeError as e:
                print(f"Error parsing JSON response for {plugin_name[-1]}: {e}")
                return None

            # Assuming the 'enabled' key needs to be modified.
            if 'enabled' in data:
                data['enabled'] = True
            else:
                print(f"The 'enabled' key was not found for {plugin_name[-1]}.")
            return json.dumps(data)
        else:
            print(f"Error fetching plugin data for {plugin_name[-1]}: {response.text}")
            return None
    except Exception as e:
        # Catch-all for any other unforeseen errors
        print(f"Unexpected error occurred while modifying plugin data for {plugin_name[-1]}: {e}")
        return None


def update_plugin_module(plugin_key, modified_data):
    """Update the plugin module with the modified data."""
    try:
        response = requests.put(
            f"{CONFLUENCE_BASE_URL}/rest/plugins/1.0/{plugin_key}?token={UPM_TOKEN}",
            auth=(ADMIN_USERNAME, ADMIN_PASSWORD),
            headers={'Content-Type': 'application/vnd.atl.plugins.plugin.module+json'},
            data=modified_data,
            verify=CERT
        )
    except requests.exceptions.RequestException as e:
        # This captures all exceptions that are requests-related
        print(f"HTTP request error while updating {plugin_key}: {e}")
        return

    if response.ok:
        print(f"Successfully updated {plugin_key}.")
    else:
        # This includes any kind of error responses from the server (4xx and 5xx status codes)
        print(f"Failed to update {plugin_key}. Response: {response.text}")



# Initial request to get the status
response = make_get_request('?', None)

# List of plugin keys to check
plugin_keys = [
    'com.atlassian.confluence.plugins.soy-key/modules/soyTemplateRendererHelperContext-key',
    'com.atlassian.confluence.extra.officeconnector-key/modules/velocity.helper-key',
    'com.atlassian.confluence.plugins.confluence-lookandfeel-key/modules/siteLogoHelperContext-key',
]

if response.ok:
    UPM_TOKEN = response.headers.get('upm-token', '').strip()
    get_plugin_status(response)
else:
    print("Failed to fetch UPM token.")
