import subprocess
import sys
import pingparsing
import json
import numpy as np
import speedtest
import platform
import os
import pandas as pd
from pprint import pprint
from datetime import datetime


def run_latency_and_jitter_and_packet_loss_tests(website: str, num_pings=60) -> tuple:
    """
    Given a website perform an evaluation on, run a latency, jitter, and 
    packet loss tests using the given website

    :param str website: the website to run the test on
    :param int num_pings: the number of pings to perform before expiry 
    """
    #ping_parser = pingparsing.PingParsing()
    #transmitter = pingparsing.PingTransmitter()
    #transmitter.destination = website
    #transmitter.count = num_pings
    #result = transmitter.ping()
    #result_dict = json.dumps(ping_parser.parse(result).as_dict(), indent=4)

    #https://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
    # Latency test
    subprocess_list = []
    if platform.system() == "Linux":
        subprocess_list = ["python3", "-m"]
    subprocess_list.extend(["pingparsing", website, "--icmp-reply"])
    subprocess_list.extend(["-c", str(num_pings)])
    latency_dict = json.loads((subprocess.check_output(subprocess_list)).decode("utf-8"))
    print(f"Latency Test:")
    pprint(latency_dict)
    print("-" * 60)

    # Jitter test
    # Extract timestamps
    timestamps = [d["time"] for d in latency_dict[website]["icmp_replies"]]

    # Calculate the absolute differences between the timestamps
    # via https://stackoverflow.com/questions/2400840/python-finding-differences-between-elements-of-a-list
    abs_diffs = [abs(j-i) for i,j in zip(timestamps, timestamps[1:])]

    # Perform the mean of the absolute differences and report as jitter
    jitter = -1
    if abs_diffs:
        jitter = np.mean(abs_diffs)
    jitter_dict = {
        "jitter": jitter
    }

    print(f"Jitter Test:")
    pprint(jitter_dict)
    print("-" * 60)

    # Print results of packet loss test
    loss_dict = {
        "loss_rate": latency_dict[website]['packet_loss_rate'],
        "loss_count": latency_dict[website]['packet_loss_count']
    }
    print(f"Packet Loss Test:")
    pprint(loss_dict)
    return latency_dict, jitter_dict, loss_dict


def run_signal_strength_test(wifi_name: str) -> dict:
    """
    Run a signal strength test on the given network and report the results

    :param str wifi_name: the name of the wifi network to check when the test is run
    """
    # macos command
    # /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'agrCtlRSSI\|agrCtlNoise\|SSID'
    # Extract agrCtlRSSI and agrCtlNoise, can also SSID (wifi network)
    signal_strength_dict = {}
    command_to_run = None
    if platform.system() == "Windows":
        # Do Windows stuff here
        pass
    #https://superuser.com/questions/442307/iwconfig-does-not-show-noise-level-for-wireless
    elif platform.system() == "Linux":
        command_to_run = "iwconfig | grep 'Signal level\|Link Quality\|SSID'"
    else:
        command_to_run = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'agrCtlRSSI\|SSID'"
    
    popen_cmd = subprocess.Popen(command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    signal_strength_result = [s.strip() for s in (popen_cmd.communicate()[0]).decode("utf-8").split("\n")]
    if platform.system() == "Linux":
        signal_strength_result = signal_strength_result[-3:-1]
        for attr in signal_strength_result:
            if attr and "ESSID:" in attr:
                data = attr.split(" ")[-1]
                key, val = data.split(":")
                key, val = map_key_and_val_from_results(key, val, wifi_name)
                signal_strength_dict[key] = val
            elif attr and "Signal level=" in attr:
                data = attr.split(" ")[-2]
                key, val = data.split("=")
                print(key, val)
                key, val = map_key_and_val_from_results(key, val, wifi_name)
                signal_strength_dict[key] = val
    else:
        for attr in signal_strength_result:
            if attr:
                key, val = attr.split(": ")
                if key != "BSSID":
                    key, val = map_key_and_val_from_results(key, val, wifi_name)
                    signal_strength_dict[key] = val
    
    pprint(signal_strength_dict)
    return signal_strength_dict


def map_key_and_val_from_results(key: str, val: str, wifi_name: str) -> tuple:
    kv_map = {
        "agrCtlRSSI": "signal_strength",
        "SSID": "ssid",
        "level": "signal_strength",
        "ESSID": "ssid"
    }

    if key == "agrCtlRSSI":
        val = int(val)
    if key == "level":
        # values in dbm
        val = int(val)
    if key == "ESSID":
        val = val.replace("\"", "")

    if kv_map[key] == "ssid" and wifi_name != val:
        raise Exception(f"Wi-Fi network {val} does not match CLI arg {wifi_name}")

    return kv_map[key], val

def run_network_bandwidth_test() -> dict:
    """
    Run a bandwidth test on the given network and report the results in the form of download/upload metrics
    """

    s = speedtest.Speedtest()
    download_result = s.download()
    upload_result = s.upload()

    bandwidth_dict = {
        "download": download_result,
        "upload": upload_result
    }
    print(f"Bandwidth Test:")
    pprint(bandwidth_dict)
    return bandwidth_dict

def combine_signal_and_bandwith(signal_strength_dict: dict, bandwidth_dict: dict):
    merged_dict = signal_strength_dict.update(bandwidth_dict)
    return merged_dict

def main(location: str, latitude: float, longitude: float, wifi_name: str) -> None:
    """
    Main method for script execution
    """
    start = datetime.now()
    print(f"Program Args Loaded:\n\tLocation: {location}\n\tLatitude, Longitude: ({latitude},{longitude})\n\tWi-Fi Name to Test: {wifi_name}")
    # Borrowed from alexa.com
    websites_to_test = [
        # 25 websites from top 50 listed on alexa.com/topsites
        "google.com",
        "youtube.com",
        "tmall.com",
        "facebook.com",
        "qq.com",
        "baidu.com",
        "sohu.com",
        "taobao.com",
        "360.cn",
        "jd.com",
        "amazon.com",
        "yahoo.com",
        "wikipedia.org",
        "weibo.com",
        "sina.com.cn",
        "alipay.com",
        "bing.com", 
        "live.com",
        "twitter.com",
        "twitch.tv",
        "reddit.com",
        "office.com",
        "instagram.com",
        "panda.tv",
        "zhanqi.tv",

        # SBU-specific (possible) [7 total]
        "blackboard.stonybrook.edu",
        "messenger.com",
        "classroom.google.com",
        "chegg.com",
        "coursehero.com",
        "discord.com",
        "quizlet.com",
        "github.com"
        "psns.cc.stonybrook.edu"
        "stackoverflow.com"
    ]

    dir = f"./results/{location}/{str(latitude).replace('.', '_')}/{str(longitude).replace('.', '_')}/{wifi_name}"
    filename_websites = "{:%Y_%m_%d_%H_%M_%S}".format(start) + f"_websites.csv"
    filename_network = "{:%Y_%m_%d_%H_%M_%S}".format(start) + f"_network.csv"

    if not os.path.exists(dir):
        os.makedirs(dir)

    print("-" * 60)
    print(f"Running signal strength test...")
    signal_strength_dict = run_signal_strength_test(wifi_name=wifi_name)
    print("-" * 60)
    print(f"Running network bandwidth test...")
    bandwidth_dict = run_network_bandwidth_test()
    print("-" * 60)
    print(f"Running latency, jitter, and packet loss tests...")
    latency_jitter_loss_data = []
    for website in websites_to_test:
        print(f"Testing {website}...")
        latency_dict, jitter_dict, loss_dict = run_latency_and_jitter_and_packet_loss_tests(website=website)
        data_to_append = {
            **latency_dict[website],
            **jitter_dict,
            **loss_dict
        }
        data_to_append["location"] = location
        data_to_append["latitude"] = latitude
        data_to_append["longitude"] = longitude
        data_to_append["wifi_name"] = wifi_name
        del data_to_append["icmp_replies"]
        latency_jitter_loss_data.append(
            data_to_append
        )
        print("-" * 60)
    print("-" * 60)
    end = datetime.now()
    print(f"Total time taken to perform network assessment: {end - start}")

    ## Consolidate data
    print(f"Saving signal and bandwidth data to {dir + '/' + filename_network}...")
    signal_strength_df = signal_strength_dict.update(bandwidth_dict)
    signal_strength_df["location"] = location
    signal_strength_df["latitude"] = latitude
    signal_strength_df["longitude"] = longitude
    signal_strength_df["wifi_name"] = wifi_name
    pd.DataFrame.from_dict(signal_strength_df).to_csv(dir + '/' + filename_network, index=False)

    print(f"Saving latency, jitter, and packet loss data to {dir + '/' + filename_websites}...")
    pd.DataFrame(latency_jitter_loss_data).to_csv(dir + "/" + filename_websites, index=False)

if __name__ == "__main__":
    # Program args:
    # - name of location
    # - latitude
    # - longitude
    # - wifi network name
    arg_list = sys.argv
    if len(arg_list) != 5:
        print("Missing some arguments")
        print("Example: 'script.py Schomburg-A 40.91339 -73.13221 WolfieNet-Secure'")
    location = arg_list[1]
    latitude = float(arg_list[2])
    longitude = float(arg_list[3])
    wifi_name = arg_list[4]
    main(location=location, latitude=latitude, longitude=longitude, wifi_name=wifi_name)