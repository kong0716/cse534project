import subprocess
import sys
import pingparsing
import json
import rssi
import numpy
import psutil

def run_latency_test(website, num_pings = 2):
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = website
    transmitter.count = num_pings
    result = transmitter.ping()
    result_dict = json.dumps(ping_parser.parse(result).as_dict(), indent=4)
    print(f"Latency Test:\n{result_dict}")

def get_signal_strength():
    interface = 'wlp1s0'.encode('utf-8')
    rssi_scanner = rssi.RSSI_Scan(interface)
    ssids = ['dd-wrt','linksys']

    # sudo argument automatixally gets set for 'false', if the 'true' is not set manually.
    # python file will have to be run with sudo privileges.
    ap_info = rssi_scanner.getAPinfo(networks=ssids, sudo=True)

    print(f"Signal Strength Test:\n{ap_info}")

def get_network_bandwidth():
    # From here: https://stackoverflow.com/questions/8958614/measure-network-data-with-python
    bandwidth_result = psutil.net_io_counters(pernic=True)
    print(f"Network Bandwidth Test:\n{bandwidth_result}")

def main():
    print("Hello World!")
    #run_latency_test("google.com")
    # print("-" * 60)
    get_signal_strength()
    print("-" * 60)
    get_network_bandwidth()
    print("-" * 60)

if __name__ == "__main__":
    main()