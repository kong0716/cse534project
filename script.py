import subprocess
import sys
import pingparsing
import json
import rssi
import numpy
import psutil
import speedtest
import platform
import re
import os

s = speedtest.Speedtest()


def run_latency_and_jitter_test(website, num_pings = 10):
    #ping_parser = pingparsing.PingParsing()
    #transmitter = pingparsing.PingTransmitter()
    #transmitter.destination = website
    #transmitter.count = num_pings
    #result = transmitter.ping()
    #result_dict = json.dumps(ping_parser.parse(result).as_dict(), indent=4)

    #https://stackoverflow.com/questions/1854/python-what-os-am-i-running-on
    subprocessList = ["pingparsing", website]
    subprocessList.extend(["-c", str(num_pings)])
    result = (subprocess.check_output(subprocessList)).decode("utf-8").split("\n")
    print(result)

    print(f"Latency Test:\n{result_dict}")

#https://github.com/s7jones/Wifi-Signal-Plotter/blob/master/WifiSignalPlotter.py
def read_data_from_cmd():
	if platform.system() == 'Linux':
		p = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	elif platform.system() == 'Windows':
		p = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
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

def get_signal_strength():
    # macos command
    # /System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I | grep 'agrCtlRSSI\|agrCtlNoise\|SSID'
    # Extract agrCtlRSSI and agrCtlNoise, can also SSID (wifi network)
    return

def get_network_bandwidth():
    print('My download speed is:', s.download())
    print('My upload speed is:', s.upload())

def main():
    run_latency_and_jitter_test("google.com")
    # print("-" * 60)
    #get_signal_strength()
    # print("-" * 60)
    #get_network_bandwidth()
    # print("-" * 60)
    # print(read_data_from_cmd())

if __name__ == "__main__":
    main()