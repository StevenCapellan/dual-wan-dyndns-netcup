import pycurl
import pause
from io import BytesIO
import requests
import json
from dotenv import load_dotenv
import os

# import the .env and the variables in it into the program
load_dotenv('.env')
customer_number = os.environ.get('customer_number')
api_key = os.environ.get('api_key')
api_password = os.environ.get('api_password')
client_request_id = os.environ.get('client_request_id')
domain_name = os.environ.get('domain_name')
public_ip_url = os.environ.get('public_ip_url')
subdomain_one = os.environ.get('subdomain_one')
subdomain_two = os.environ.get('subdomain_two')

# predefine the domain hoster url and create the global objects
netcup_api = "https://ccp.netcup.net/run/webservice/servers/endpoint.php?JSON"
session = ""
content_cable = "not yet determined, because the program has just started"
content_dsl = "not yet determined, because the program has just started"


# function to perform a login request to the server and obtain a session id
def api_login():
    global session
    login_json = {
        "action": "login",
        "param": {
            "customernumber": customer_number,
            "apikey": api_key,
            "apipassword": api_password,
            "clientrequestid": client_request_id
        }
    }
    login_json = json.dumps(login_json)
    response = requests.post(netcup_api, json=json.loads(login_json))
    session = response.json()["responsedata"]["apisessionid"]
    print(f"api login successful with session-id: {session}")


# function to logout of the session and invalidate the session id
def api_logout():
    global session
    logout_json = {
        "action": "logout",
        "param": {
            "customernumber": customer_number,
            "apikey": api_key,
            "clientrequestid": client_request_id
        }
    }
    logout_json["param"]["apisessionid"] = session
    logout_json = json.dumps(logout_json)
    requests.post(netcup_api, json=json.loads(logout_json))
    print(f"api logout of session-id: {session} ")
    session = ""


# function to obtain the current dns record settings
def api_dnsrecordsinfo():
    dnsinfo_json = {
        "action": "infoDnsRecords",
        "param": {
            "customernumber": customer_number,
            "apikey": api_key,
            "clientrequestid": client_request_id,
            "domainname": domain_name
        }
    }
    dnsinfo_json["param"]["apisessionid"] = session
    dnsinfo_json = json.dumps(dnsinfo_json)
    response = requests.post(netcup_api, json=json.loads(dnsinfo_json))
    print(f"DNS records info. Status: {response.json()['status']}, shortmessage: {response.json()['shortmessage']}")
    return response.json()


# function to update the dns record through the api
def api_updatednsrecord(ip, subdomain):
    dnsupdate_json = {
        "action": "updateDnsRecords",
        "param": {
            "customernumber": customer_number,
            "apikey": api_key,
            "clientrequestid": client_request_id,
            "domainname": domain_name
        }
    }
    # obtain the current dns record settings
    dns_data = api_dnsrecordsinfo()["responsedata"]["dnsrecords"]

    # analyse the dns record settings to find the correct entry to change
    counter = 0
    changed_value = -1
    for item in dns_data:
        if item["hostname"] == subdomain:
            dns_data[counter]["destination"] = ip
            changed_value = counter
            counter += 1
        else:
            counter += 1
    dnsupdate_json["param"]["apisessionid"] = session
    dnsupdate_json["param"]["dnsrecordset"] = {"dnsrecords": [dns_data[changed_value]]}
    dnsupdate_json = json.dumps(dnsupdate_json)
    response = requests.post(netcup_api, json=json.loads(dnsupdate_json))
    print(f"Update DNS record. Status: {response.json()['status']}, shortmessage: {response.json()['shortmessage']}")


# Main function to repeat every 5 minutes
while True:
    # Check cable IP
    b_obj = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.URL, public_ip_url)
    crl.setopt(crl.WRITEDATA, b_obj)
    crl.setopt(crl.LOCALPORT, 55000)
    crl.setopt(crl.LOCALPORTRANGE, 20)
    try:
        crl.perform()
    except:
        crl.close()
    crl.close()
    get_body = b_obj.getvalue().decode("utf-8")
    print(f"Current cable ip is {get_body}. The one pushed to DNS settings is {content_cable}.")
    if content_cable == get_body:
        print("Cable IP's are the same.")
    else:
        print(f"Cable IP's have changed. Will push the new IP {get_body} to the DNS settings.")
        content_cable = get_body
        api_login()
        api_updatednsrecord(get_body, subdomain_one)
        api_logout()

    # Check DSL IP
    b_obj = BytesIO()
    crl = pycurl.Curl()
    crl.setopt(crl.URL, public_ip_url)
    crl.setopt(crl.WRITEDATA, b_obj)
    crl.setopt(crl.LOCALPORT, 55020)
    crl.setopt(crl.LOCALPORTRANGE, 20)
    try:
        crl.perform()
    except:
        crl.close()
    crl.close()
    get_body = b_obj.getvalue().decode("utf-8")
    print(f"Current DSL ip is {get_body}. The one pushed to DNS settings is {content_dsl}.")
    if content_dsl == get_body:
        print("DSL IP's are the same.")
    else:
        print(f"DSL IP's have changed. Will push the new IP {get_body} to the DNS settings.")
        content_dsl = get_body
        api_login()
        api_updatednsrecord(get_body, subdomain_two)
        api_logout()

    print("Cycle done. Will sleep for 5 minutes.\n")
    pause.minutes(5)
