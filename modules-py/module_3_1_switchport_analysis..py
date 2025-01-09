import os
import re

def parse_switchport_info(config_data):
    """
    Phân tích thông tin từ lệnh 'show interface switchport' để tìm các interface vi phạm.
    Args:
        config_data (str): Nội dung lệnh 'show interface switchport'.

    Returns:
        dict: Cấu hình của các interface vi phạm liên quan đến VLAN 1.
    """
    interface_configs = {}
    current_interface = None
    current_config = {}

    # Regex để phân tích lệnh
    interface_pattern = r"^Name:\s+(?P<interface>\S+)"
    admin_mode_pattern = r"Administrative Mode:\s+(?P<admin_mode>.+)"
    access_vlan_pattern = r"Access Mode VLAN:\s+(?P<access_vlan>\d+)"
    trunk_native_vlan_pattern = r"Trunking Native Mode VLAN:\s+(?P<native_vlan>\d+)"
    trunk_allowed_vlans_pattern = r"Trunking VLANs Enabled:\s+(?P<allowed_vlans>[\d,]+)"

    for line in config_data.splitlines():
        line = line.strip()

        # Phát hiện tên interface
        if match := re.search(interface_pattern, line):
            # Lưu cấu hình interface trước đó nếu cần
            if current_interface and (
                current_config.get("admin_mode") == "static access" and current_config.get("access_vlan") == "1" or
                current_config.get("admin_mode") == "trunk" and (
                    current_config.get("native_vlan") == "1" or
                    "1" in current_config.get("allowed_vlans", "").split(","))
            ):
                interface_configs[current_interface] = current_config

            # Bắt đầu phân tích interface mới
            current_interface = match.group("interface")
            current_config = {}

        # Phân tích Administrative Mode
        if current_interface and (match := re.search(admin_mode_pattern, line)):
            current_config["admin_mode"] = match.group("admin_mode").strip()

        # Phân tích VLAN truy cập
        if current_interface and (match := re.search(access_vlan_pattern, line)):
            current_config["access_vlan"] = match.group("access_vlan")

        # Phân tích Native VLAN
        if current_interface and (match := re.search(trunk_native_vlan_pattern, line)):
            current_config["native_vlan"] = match.group("native_vlan")

        # Phân tích Allowed VLANs
        if current_interface and (match := re.search(trunk_allowed_vlans_pattern, line)):
            current_config["allowed_vlans"] = match.group("allowed_vlans")

    # Xử lý trường hợp cuối cùng
    if current_interface and (
        current_config.get("admin_mode") == "static access" and current_config.get("access_vlan") == "1" or
        current_config.get("admin_mode") == "trunk" and (
            current_config.get("native_vlan") == "1" or
            "1" in current_config.get("allowed_vlans", "").split(","))
    ):
        interface_configs[current_interface] = current_config

    return interface_configs


def process_switchport_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và phân tích thông tin từ 'show interface switchport'.
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
            interface_configs = parse_switchport_info(config_data)

            # Hiển thị kết quả
            if interface_configs:
                print("\033[1mCấu hình hiện tại của các interface vi phạm:\033[0m")
                for interface, config in interface_configs.items():
                    print(f"\nInterface: {interface}")
                    print(config)
            else:
                print("\033[33mKhông có interface nào vi phạm liên quan đến VLAN 1.\033[0m")
            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_switchport_logs(folder_path)
