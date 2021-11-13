# CSE 534 Project: Far Beyond Wi-Fi

## Instructions
1. `virtualenv venv`
2. `pip install -r requirements.txt`
3. Note down the following information:
    - Location: which campus building you're currently in. Could be granular to floor-location if you want, **but string cannot have spaces**)
        - For example, if you are in Schomburg A, the location string would be `SchomburgA`, or if you want to be specific, you can make the string `SchomburgA-F1-A123`
        - Similarly, if you are in Frey Hall, the location string would be `FreyHall`, or if you want to be specific, you can make the string `FreyHall-F1-Lobby`
    - Use Apple Maps (preferred) or Google Maps, and retrieve the latitude and longitude values of your current location
        - For example, in Schomburg B, an example location has a latitude of 40.XXXXXX and longitude of -73.XXXXX. Note these values down
    - Shut off your Wi-Fi, wait 10 seconds, then connect to either `WolfieNet-Secure` or `eduroam`. **It is imperative that the network names are spelled correctly as shown on your computer, otherwise the script will fail**. Note down the network name
4. Run the script, which is 
    ```bash
    python script.py <LOCATION> <LATITUDE> <LONGITUDE> <WIFI-NAME>
    ```
    - example:
        ```bash
        python script.py SchomburgA 40.XXXXXX -73.XXXXX WolfieNet-Secure
        ```
5. Update the repo with the generated CSVs