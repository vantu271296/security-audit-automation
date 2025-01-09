import os
import re

def analyze_show_dhcp_snooping(config_data):
    """
    Phân tích kết quả từ lệnh 'show ip dhcp snooping'.
    Args:
        config_data (str): Nội dung lệnh 'show ip dhcp snooping'.

    Returns:
        dict: Trạng thái DHCP Snooping, VLANs được bật, và danh sách cổng tin cậy.
    """
    dhcp_snooping_status = {
        "enabled": False,
        "configured_vlans": "",
        "operational_vlans": "",
        "trusted_ports": []
    }

    # Regex để phân tích nội dung
    snooping_enabled_pattern = r"Switch DHCP snooping is enabled"
    configured_vlan_pattern = r"DHCP snooping is configured on following VLANs:\s*([\d,\- ]+)"
    operational_vlan_pattern = r"DHCP snooping is operational on following VLANs:\s*([\d,\- ]+)"
    trusted_port_pattern = r"^(\S+)\s+yes\s+"

    # Kiểm tra trạng thái DHCP Snooping
    if re.search(snooping_enabled_pattern, config_data, re.IGNORECASE):
        dhcp_snooping_status["enabled"] = True

    # Lấy các VLAN được cấu hình
    configured_vlan_match = re.search(configured_vlan_pattern, config_data, re.IGNORECASE)
    if configured_vlan_match:
        dhcp_snooping_status["configured_vlans"] = configured_vlan_match.group(1).strip()

    # Lấy các VLAN đang hoạt động
    operational_vlan_match = re.search(operational_vlan_pattern, config_data, re.IGNORECASE)
    if operational_vlan_match:
        dhcp_snooping_status["operational_vlans"] = operational_vlan_match.group(1).strip()

    # Tìm cổng Trusted
    trusted_matches = re.finditer(trusted_port_pattern, config_data, re.IGNORECASE | re.MULTILINE)
    for match in trusted_matches:
        dhcp_snooping_status["trusted_ports"].append(match.group(1))

    return dhcp_snooping_status


def process_show_dhcp_snooping_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và phân tích lệnh 'show ip dhcp snooping'.
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
            dhcp_snooping_status = analyze_show_dhcp_snooping(config_data)

            # Hiển thị kết quả
            print("\033[1mKết quả phân tích 'show ip dhcp snooping':\033[0m")
            if dhcp_snooping_status["enabled"]:
                print("\033[32mDHCP Snooping được bật.\033[0m")
                if dhcp_snooping_status["configured_vlans"]:
                    print(f"DHCP snooping is configured on following VLANs: {dhcp_snooping_status['configured_vlans']}")
                else:
                    print("\033[33mKhông tìm thấy VLAN nào được cấu hình DHCP Snooping.\033[0m")

                if dhcp_snooping_status["operational_vlans"]:
                    print(f"DHCP snooping is operational on following VLANs: {dhcp_snooping_status['operational_vlans']}")
                else:
                    print("\033[33mKhông có VLAN nào đang hoạt động với DHCP Snooping.\033[0m")

                if dhcp_snooping_status["trusted_ports"]:
                    print("\033[1mCổng tin cậy (Trusted Ports):\033[0m")
                    for port in dhcp_snooping_status["trusted_ports"]:
                        print(f"- {port}")
                else:
                    print("\033[33mKhông có cổng tin cậy nào được cấu hình.\033[0m")
            else:
                print("\033[31mDHCP Snooping chưa được bật.\033[0m")
            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_show_dhcp_snooping_logs(folder_path)
