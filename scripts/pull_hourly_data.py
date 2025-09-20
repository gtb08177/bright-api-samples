## python script for pulling hourly data since moving into Jane Drive

import datetime
import http.client
import os
import argparse

BRIGHT_APP_ID = "b0f1b774-a586-4f72-9edd-27ead8aa7a8d" # the application id of the Bright client app, DO NOT CHANGE THIS

def get_utc_start_of_month(year, month):
    return datetime.datetime(year, month, 1).strftime("%Y-%m-%dT%H:%M:%S")

def get_utc_end_of_month(year, month):
    # Get the first day of the next month
    if month == 12:
        next_month = datetime.datetime(year + 1, 1, 1)
    else:
        next_month = datetime.datetime(year, month + 1, 1)
    
    # Subtract one second to get the last moment of the current month
    end_of_month = next_month - datetime.timedelta(seconds=1)
    
    return end_of_month.strftime("%Y-%m-%dT%H:%M:%S")

def retrieve_data_from_api(start, end, resource_id, token):
    conn = http.client.HTTPSConnection("api.glowmarkt.com")

    headers = {
        'content-type': "application/json",
        'token': token,
        'applicationid': BRIGHT_APP_ID
    }

    conn.request("GET", "/api/v0-1/resource/"+ resource_id + "/readings?period=PT1H&function=sum&from=" + start + "&to=" + end, headers=headers)

    res = conn.getresponse()
    return res.read()


def generate_monthly_ranges(overall_start_month=5, overall_start_year=2024):
    now = datetime.datetime.now()
    current_year = now.year
    current_month = now.month
    
    months = []
    for year in range(overall_start_year, current_year + 1):
        start_month = overall_start_month if year == overall_start_year else 1 
        end_month = current_month if year == current_year else 12
        for starting_month_number in range(start_month, end_month + 1):
            start = get_utc_start_of_month(year, starting_month_number)
            end = get_utc_end_of_month(year, starting_month_number)
            months.append((start, end))
    
    return months

def setup_cost_file():
    output_file_cost = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_hourly_data_cost.txt"
    
    if os.path.exists(output_file_cost):
        os.remove(output_file_cost)
    
    return output_file_cost

def setup_consumption_file():
    output_file_consumption = f"{datetime.datetime.now().strftime('%Y-%m-%d')}_hourly_data_consumption.txt"

    if os.path.exists(output_file_consumption):
        os.remove(output_file_consumption)

    return output_file_consumption

def main():
    parser = argparse.ArgumentParser(description="Creates two files that contain JSON dumps for smart electricity meter readings in hourly intervals")
    parser.add_argument("--token", required=True, help="Your API token for Glowmarkt")
    parser.add_argument("--move-in-date", required=True, help="Your move-in date in MM-YYYY format")
    
    # TODO - Allow username/password to be used to fetch token automatically
    # parser.add_argument("--username", required=True, help="Your username for Glowmarkt")
    # parser.add_argument("--password", required=True, help="Your password for Glowmarkt")

    # TODO - Allow resource IDs to be passed in as arguments
    res_id_elec_cost = "83cbdbc1-d18f-4fb1-96ac-520cd2eb1876"
    res_id_elec_consumption = "36f21351-aac6-4109-9f95-2307bc453e1d" 

    args = parser.parse_args()
    
    token = args.token
    moved_in_month, moved_in_year = map(int, args.move_in_date.split("-"))

    output_file_cost = setup_cost_file()
    output_file_consumption = setup_consumption_file()
    
    months = generate_monthly_ranges(moved_in_month, moved_in_year)

    for start, end in months:
        print(f"Retrieving cost data for {start} to {end}")
        data = retrieve_data_from_api(start, end, res_id_elec_cost, token)

        print(f"Cost data for {start} to {end} written to {output_file_cost}")
        open(output_file_cost, "a").write(data.decode("utf-8") + "\n")

        print(f"\nRetrieving consumption data for {start} to {end}")
        data = retrieve_data_from_api(start, end, res_id_elec_consumption, token)

        print(f"Consumption data for {start} to {end} written to {output_file_consumption}")
        open(output_file_consumption, "a").write(data.decode("utf-8") + "\n")

        print("\n================================\n")

if __name__ == "__main__":
    main()