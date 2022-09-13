from collections import defaultdict

from log_parser.get_user_agent import convert_user_agent_to_list
from log_parser.other_headers import (
    get_api_status,
    get_date_and_time,
    get_method_header,
    get_url,
)
from log_parser.get_ips import get_ips

import requests
import csv


def find_user_info(ips_list, filename):
    """Takes in a list of IP addresses and a file (expects a log file).
    It then iterates through the list of IP addresses and uses the user_agent_info list to find the device and browser used.
    Then it uses the ips_list list to find the country name and state of the IP address.
    Uses helper functions to add data to the final dictionary output.

    Args:
        ips_list (list): the list of IP addresses we want to track
        filename (file): the name of the file that contains the logs

    Returns:
        dictionary: A dictionary with the key being the index of the IP address in the list of IP addresses.
        The value is a list of tuples. Each tuple contains the IP address, country name, state, and user agent info (device and browser)
    """

    user_agent_info = convert_user_agent_to_list(filename)
    method_info = get_method_header(filename)
    api_status_info = get_api_status(filename)
    get_date_and_time_info = get_date_and_time(filename)
    get_url_info = get_url(filename)

    output = defaultdict(list)
    temp_list = []

    for index, ip in enumerate(ips_list):
        response = requests.get(f"https://geolocation-db.com/json/{ip}").json()
        country_name = response["country_name"]
        state = response["state"]

        if state == None:
            state = "Not Found"

        temp_list.append(
            (
                ip,
                country_name,
                state,
                user_agent_info[index - 1],
                method_info[index - 1],
                api_status_info[index - 1],
                get_date_and_time_info[index - 1],
                get_url_info[index - 1],
            )
        )

    for index, info in enumerate(temp_list):
        output[index].append(info)

    return output


def export_to_csv(dict):
    """Takes a dictionary and their associated information and exports it to a CSV file

    Args:
        dict (dictionary): the dictionary to be exported to csv
    """

    with open("output.csv", "w") as csvfile:
        writer = csv.writer(csvfile)

        headers = [
            "IP",
            "Country Name",
            "State",
            "Browser",
            "Device",
            "Method",
            "Status Code",
            "Date and Time",
            "URL",
        ]

        writer.writerow(headers)

        for item in dict.items():
            ip = item[1][0][0]
            country_name = item[1][0][1]
            state = item[1][0][2]
            user_agent_browser = item[1][0][3][0]
            user_agent_device = item[1][0][3][1]
            method = item[1][0][4]
            status_code = item[1][0][5]
            date_and_time = item[1][0][6]
            url = item[1][0][7]

            writer.writerow(
                (
                    ip,
                    country_name,
                    state,
                    user_agent_browser,
                    user_agent_device,
                    method,
                    status_code,
                    date_and_time,
                    url,
                )
            )


# runs file
if __name__ == "__main__":
    export_to_csv(find_user_info(get_ips("log2.log"), "log2.log"))