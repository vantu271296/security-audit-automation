import os
import re

def analyze_encryption_strength(config_data):
    encryption_status = {
        "BGP": {"strong": [], "weak": [], "cleartext": [], "no_auth": True},
        "OSPF": {"strong": [], "weak": [], "cleartext": [], "no_auth": True},
        "RIP": {"strong": [], "weak": [], "cleartext": [], "no_auth": True}
    }

    # BGP pattern kiểm tra cả cleartext và encrypted
    bgp_patterns = {
        'encrypted': r"neighbor \S+ password \S*(?:md5|sha)\S* (\S+)",
        'cleartext': r"neighbor \S+ password (?!.*(?:md5|sha))(\S+)"
    }
    
    # OSPF patterns
    ospf_patterns = {
        'strong': r"area \d+ authentication message-digest (?:sha256|sha384|sha512)",
        'weak': r"area \d+ authentication message-digest (?:md5|sha1)",
        'cleartext': r"area \d+ authentication"
    }
    
    # RIP patterns
    rip_patterns = {
        'encrypted': r"key-string \S*(?:md5|sha)\S* (\S+)",
        'cleartext': r"key-string (?!.*(?:md5|sha))(\S+)"
    }

    # Kiểm tra BGP
    for neighbor in re.finditer(bgp_patterns['encrypted'], config_data, re.MULTILINE | re.IGNORECASE):
        if 'md5' in neighbor.group().lower():
            encryption_status["BGP"]["weak"].append(neighbor.group(1))
        else:
            encryption_status["BGP"]["strong"].append(neighbor.group(1))
        encryption_status["BGP"]["no_auth"] = False

    for neighbor in re.finditer(bgp_patterns['cleartext'], config_data, re.MULTILINE | re.IGNORECASE):
        encryption_status["BGP"]["cleartext"].append(neighbor.group(1))
        encryption_status["BGP"]["no_auth"] = False

    # Kiểm tra OSPF
    if re.search(ospf_patterns['strong'], config_data, re.MULTILINE | re.IGNORECASE):
        encryption_status["OSPF"]["strong"].append("SHA256/384/512")
        encryption_status["OSPF"]["no_auth"] = False
    elif re.search(ospf_patterns['weak'], config_data, re.MULTILINE | re.IGNORECASE):
        encryption_status["OSPF"]["weak"].append("MD5/SHA1")
        encryption_status["OSPF"]["no_auth"] = False
    elif re.search(ospf_patterns['cleartext'], config_data, re.MULTILINE | re.IGNORECASE):
        encryption_status["OSPF"]["cleartext"].append("Simple authentication")
        encryption_status["OSPF"]["no_auth"] = False

    # Kiểm tra RIP
    for key in re.finditer(rip_patterns['encrypted'], config_data, re.MULTILINE | re.IGNORECASE):
        if 'md5' in key.group().lower():
            encryption_status["RIP"]["weak"].append(key.group(1))
        else:
            encryption_status["RIP"]["strong"].append(key.group(1))
        encryption_status["RIP"]["no_auth"] = False

    for key in re.finditer(rip_patterns['cleartext'], config_data, re.MULTILINE | re.IGNORECASE):
        encryption_status["RIP"]["cleartext"].append(key.group(1))
        encryption_status["RIP"]["no_auth"] = False

    return encryption_status

log_files = [
    r"D:\automation\Test\10.22.122.10HN-22HV-ROUTER-WIFI.log",
    r"D:\automation\Test\10.22.203.102-HN-22HV-SW-ACCESS-02-20250106.log"
]

for file_path in log_files:
    print(f"\nĐang xử lý file: {file_path}")
    
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            config_data = file.read()

        encryption_status = analyze_encryption_strength(config_data)

        print("\033[1mKết quả kiểm tra xác thực:\033[0m")
        for protocol, status in encryption_status.items():
            print(f"\033[1m{protocol}:\033[0m")
            if status["no_auth"]:
                print("  \033[33mKhông tìm thấy chuỗi xác thực\033[0m")
            else:
                if status["strong"]:
                    print(f"  \033[32mMã hóa mạnh:\033[0m {', '.join(status['strong'])}")
                if status["weak"]:
                    print(f"  \033[33mMã hóa yếu:\033[0m {', '.join(status['weak'])}")
                if status["cleartext"]:
                    print(f"  \033[31mKhông có mã hóa:\033[0m {', '.join(status['cleartext'])}")

        print("-" * 50)
    except Exception as e:
        print(f"Lỗi khi xử lý {file_path}: {e}")