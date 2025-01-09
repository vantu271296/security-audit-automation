import os
import re

def analyze_layer2_protection(config_data):
    """
    Phân tích cấu hình bảo vệ lớp 2 (static mapping, ARP inspection, port-security, 802.1x).
    Args:
        config_data (str): Nội dung cấu hình.

    Returns:
        dict: Thông tin chi tiết về các giải pháp được cấu hình.
    """
    protection_results = {
        "static_mapping": [],
        "arp_inspection": [],
        "port_security": [],
        "dot1x": []
    }

    # Kiểm tra Static Mapping (IP-MAC)
    static_mapping_pattern = r"ip source binding\s+(\S+)\s+(\S+)\s+(\S+)"
    static_matches = re.finditer(static_mapping_pattern, config_data)
    for match in static_matches:
        protection_results["static_mapping"].append({
            "ip_address": match.group(1),
            "mac_address": match.group(2),
            "vlan": match.group(3)
        })

    # Kiểm tra Dynamic ARP Inspection
    arp_inspection_pattern = r"ip arp inspection\s+vlan\s+([\d,]+)"
    if match := re.search(arp_inspection_pattern, config_data):
        protection_results["arp_inspection"] = match.group(1).split(",")

    # Kiểm tra Port Security
    port_security_pattern = r"interface (\S+)[\s\S]+?switchport port-security.*"
    port_security_matches = re.finditer(port_security_pattern, config_data, re.MULTILINE)
    for match in port_security_matches:
        interface = match.group(1)
        protection_results["port_security"].append(interface)

    # Kiểm tra 802.1X
    dot1x_pattern = r"dot1x system-auth-control"
    if re.search(dot1x_pattern, config_data):
        protection_results["dot1x"].append("Enabled")

    return protection_results


def process_layer2_protection_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra cấu hình bảo vệ lớp 2.
    Args:
        folder_path (str): Đường dẫn tới thư mục chứa file log.

    Returns:
        None: In kết quả cho từng file log.
    """
    if not os.path.exists(folder_path):
        print(f"Folder not found: {folder_path}")
        return

    # Duyệt qua tất cả file trong folder
    log_files = [file for file in os.listdir(folder_path) if file.endswith((".log", ".txt"))]

    if not log_files:
        print(f"No .log or .txt files found in folder: {folder_path}")
        return

    for log_file in log_files:
        file_path = os.path.join(folder_path, log_file)
        print(f"\nProcessing File: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                config_data = file.read()

            # Gọi hàm phân tích
            protection_results = analyze_layer2_protection(config_data)

            # Hiển thị kết quả
            print("\033[1mStatic Mapping (IP-MAC):\033[0m")
            for mapping in protection_results["static_mapping"]:
                print(f"IP: {mapping['ip_address']}, MAC: {mapping['mac_address']}, VLAN: {mapping['vlan']}")

            print("\033[1mDynamic ARP Inspection (DAI):\033[0m")
            if protection_results["arp_inspection"]:
                print(f"Protected VLANs: {', '.join(protection_results['arp_inspection'])}")
            else:
                print("No ARP inspection configured.")

            print("\033[1mPort Security:\033[0m")
            if protection_results["port_security"]:
                print(f"Protected Interfaces: {', '.join(protection_results['port_security'])}")
            else:
                print("No Port Security configured.")

            print("\033[1m802.1X:\033[0m")
            if protection_results["dot1x"]:
                print("802.1X is enabled.")
            else:
                print("802.1X is not configured.")
            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_layer2_protection_logs(folder_path)
