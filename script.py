import subprocess
import sys
import pingparsing
import json
import rssi
import numpy as np
import psutil
import speedtest
import platform
import re
import os
from pprint import pprint
from datetime import datetime


def run_latency_and_jitter_and_packet_loss_tests(website: str, num_pings=10):
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
    subprocess_list = ["pingparsing", website, "--icmp-reply"]
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


def read_data_from_cmd():
    """
    Pulled from here: https://github.com/s7jones/Wifi-Signal-Plotter/blob/master/WifiSignalPlotter.py
    """
    if platform.system() == 'Linux':
	    p = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    elif platform.system() == 'Windows':
	    p = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        #https://www.speedguide.net/faq/how-does-rssi-dbm-relate-to-signal-quality-percent-439
        #https://www.thewindowsclub.com/signal-strength-wi-fi-connection-windows
    else:
	    raise Exception('reached else of if statement')
    out = p.stdout.read().decode()

    if platform.system() == 'Linux':
        m = re.findall('(wlan[0-9]+).*?Signal level=(-[0-9]+) dBm', out, re.DOTALL)
    elif platform.system() == 'Windows':
        m = re.findall('Name.*?:.*?([A-z0-9 ]*).*?Signal.*?:.*?([0-9]*)%', out, re.DOTALL)
    else:
        raise Exception('reached else of if statement')

    p.communicate()

    return m


def run_signal_strength_test():
    """
    Run a signal strength test on the given network and report the results
    """
    # macos command
    # /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'agrCtlRSSI\|agrCtlNoise\|SSID'
    # Extract agrCtlRSSI and agrCtlNoise, can also SSID (wifi network)
    signal_strength_dict = {}
    if platform.system() == "Windows":
        # Do Windows stuff here
        pass
    else:
        command_to_run = "/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'agrCtlRSSI\|agrCtlNoise\|SSID'"
        popen_cmd = subprocess.Popen(command_to_run, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        signal_strength_result = [s.strip() for s in (popen_cmd.communicate()[0]).decode("utf-8").split("\n")]
        
        
        for attr in signal_strength_result:
            if attr:
                key, val = attr.split(": ")
                if isinstance(val, int):
                    signal_strength_dict[key] = int(val)
                else:
                    signal_strength_dict[key] = val
        
    pprint(signal_strength_dict)


def run_network_bandwidth_test():
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


def main():
    """
    Main method for script execution
    """
    start = datetime.now()

    # Borrowed from alexa.com
    websites_to_test = [
        # Top 25 listed on alexa.com/topsites
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
        "xinhuanet.com",
        "zoom.us",
        "live.com",
        "netflix.com",
        "microsoft.com",
        "reddit.com",
        "office.com",
        "instagram.com",
        "panda.tv",
        "zhanqi.tv",

        # SBU-specific (possible) [7 total]
        "blackboard.stonybrook.edu",
        "piazza.com",
        "classroom.google.com",
        "chegg.com",
        "coursehero.com",
        "groupme.com",
        "quizlet.com",
        "github.com"
    ]
    WEBSITE_TO_TEST = "google.com"

    print("-" * 60)
    print(f"Running latency, jitter, and packet loss tests for {WEBSITE_TO_TEST}...")
    run_latency_and_jitter_and_packet_loss_tests(website=WEBSITE_TO_TEST)
    print("-" * 60)
    print(f"Running signal strength test...")
    run_signal_strength_test()
    print("-" * 60)
    print(f"Running network bandwidth test...")
    run_network_bandwidth_test()
    print("-" * 60)
    # print(read_data_from_cmd())
    end = datetime.now()
    print(f"Total time taken to perform network assessment: {end - start}")


if __name__ == "__main__":
    main()