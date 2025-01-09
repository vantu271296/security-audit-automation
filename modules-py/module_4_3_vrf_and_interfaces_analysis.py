import os
import re
from ipaddress import ip_address, ip_network

def is_public_ip(ip):
    """
    Kiểm tra xem một IP có phải là public hay không.
    Args:
        ip (str): Địa chỉ IP cần kiểm tra.

    Returns:
        bool: True nếu IP là public, ngược lại False.
    """
    private_networks = [
        ip_network("10.0.0.0/8"),
        ip_network("172.16.0.0/12"),
        ip_network("192.168.0.0/16"),
        ip_network("127.0.0.0/8"),
        ip_network("169.254.0.0/16"),  # APIPA
        ip_network("0.0.0.0/8"),
    ]
    try:
        ip_obj = ip_address(ip)
        return not any(ip_obj in network for network in private_networks)
    except ValueError:
        return False

def parse_interfaces_and_vrf(log_content):
    """
    Phân tích interface public, MGMT và kiểm tra VRF.
    Args:
        log_content (str): Nội dung log chứa kết quả cấu hình.

    Returns:
        dict: Thông tin interface public, MGMT và VRF.
    """
    public_interfaces = set()
    mgmt_interfaces = set()
    vrf_definitions = set()
    vrf_mapping = {}

    # Tìm các định nghĩa VRF
    vrf_pattern = r"vrf definition (\S+)"
    vrf_matches = re.findall(vrf_pattern, log_content)
    vrf_definitions.update(vrf_matches)

    # Tìm các interface gắn VRF
    interface_vrf_pattern = r"interface (\S+)\n(?:.*?\n)*? vrf forwarding (\S+)"
    vrf_interface_matches = re.findall(interface_vrf_pattern, log_content, re.IGNORECASE)

    for interface, vrf in vrf_interface_matches:
        vrf_mapping[interface] = vrf

    # Tìm các interface có IP public và phân loại MGMT
    interface_ip_pattern = r"interface (\S+)\n(?:.*?\n)*? ip address (\d+\.\d+\.\d+\.\d+)"
    ip_matches = re.findall(interface_ip_pattern, log_content, re.IGNORECASE)

    for interface, ip_address in ip_matches:
        if ip_address != "unassigned" and is_public_ip(ip_address):
            if "mgmt" in interface.lower():
                mgmt_interfaces.add(interface)
            else:
                public_interfaces.add(interface)

    return {
        "public_interfaces": list(public_interfaces),
        "mgmt_interfaces": list(mgmt_interfaces),
        "vrf_definitions": list(vrf_definitions),
        "vrf_mapping": vrf_mapping,
    }

def check_vrf_separation(log_content, results):
    """
    Kiểm tra các interface public có gắn VRF hay không.
    Args:
        log_content (str): Nội dung log chứa cấu hình.
        results (dict): Thông tin phân tích interface và VRF.

    Returns:
        str: Kết quả kiểm tra VRF.
    """
    if not results["vrf_definitions"]:
        return "\033[31mKhông Tuân Thủ:\033[0m Không tìm thấy VRF nào được cấu hình."

    public_interfaces_with_vrf = [
        interface for interface in results["public_interfaces"]
        if interface in results["vrf_mapping"]
    ]

    if not public_interfaces_with_vrf:
        return "\033[31mKhông Tuân Thủ:\033[0m Các interface public không được gắn VRF."

    # Kiểm tra sự tồn tại của ít nhất 2 VRF riêng biệt (SERVICE và OAM)
    if len(results["vrf_definitions"]) < 2:
        return "\033[31mKhông Tuân Thủ:\033[0m Không có đủ VRF để tách lớp dịch vụ và lớp giám sát."

    return f"\033[32mTuân Thủ:\033[0m Các interface public được gắn VRF và VRF đã được tách riêng."

def check_interfaces_and_vrf_from_logs(folder_path):
    """
    Kiểm tra các interface public, MGMT và VRF từ các file log.
    Args:
        folder_path (str): Đường dẫn tới thư mục chứa file log.

    Returns:
        None
    """
    log_files = [f for f in os.listdir(folder_path) if f.endswith(".log") or f.endswith(".txt")]

    if not log_files:
        print("Không tìm thấy file log nào trong thư mục.")
        return

    for log_file in log_files:
        file_path = os.path.join(folder_path, log_file)
        print(f"\nĐang kiểm tra file: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                log_content = file.read()

            # Phân tích interface và VRF
            results = parse_interfaces_and_vrf(log_content)

            # Kiểm tra thiết bị có interface public hoặc MGMT
            if not results["public_interfaces"] and not results["mgmt_interfaces"]:
                print("\033[33mKhông Áp Dụng:\033[0m Thiết bị không có các interface public hoặc MGMT.")
                continue

            # Kiểm tra VRF
            vrf_check_result = check_vrf_separation(log_content, results)

            # Hiển thị kết quả
            if results["public_interfaces"]:
                print("\033[32mInterface public:\033[0m", ", ".join(results["public_interfaces"]))
            if results["mgmt_interfaces"]:
                print("\033[34mInterface MGMT:\033[0m", ", ".join(results["mgmt_interfaces"]))
            print(vrf_check_result)

        except Exception as e:
            print(f"Lỗi khi xử lý file {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"C:\Users\admin\Desktop\automation\Test"  # Thay đường dẫn tới thư mục file log
    check_interfaces_and_vrf_from_logs(folder_path)
