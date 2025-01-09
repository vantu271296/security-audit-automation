import re

def check_firmware_version(log_data):
 
    results = {}

    # Tìm phiên bản Cisco IOS-XE trước
    ios_xe_pattern = r"Cisco IOS[- ]XE Software.*Version ([\d\.\(\)\w]+)"
    ios_xe_match = re.search(ios_xe_pattern, log_data)
    if ios_xe_match:
        results['Cisco IOS-XE'] = ios_xe_match.group(1)

    # Tìm phiên bản Cisco IOS nếu không tìm thấy IOS-XE
    if not ios_xe_match:
        ios_pattern = r"Cisco IOS Software.*Version ([\d\.\(\)\w]+)"
        ios_match = re.search(ios_pattern, log_data)
        if ios_match:
            results['Cisco IOS'] = ios_match.group(1)

    # Nếu không tìm thấy phiên bản nào
    if not results:
        results['Firmware Version'] = "Not Found"
    
    print(results)

    return results

# Test module
if __name__ == "__main__":
    log_files = [
        r"10.22.122.10HN-22HV-ROUTER-WIFI.log",  # Thay đổi đường dẫn tới file log
        r"10.22.203.102-HN-22HV-SW-ACCESS-02-20250106.log"
    ]

    for file in log_files:
        with open(file, "r") as file:
            log_data = file.read()
        versions = check_firmware_version(log_data)


        
        print(f"File: {file}")
        print("Firmware Versions:")
        for key, value in versions.items():
            print(f"- {key}: {value}")
        print()
