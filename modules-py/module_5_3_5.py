# modules/module_5_3_5.py

import re
import argparse
from pathlib import Path

def check_management_ip_restriction(log_data):
    """
    Phân tích dữ liệu log để xác định giới hạn quản trị theo địa chỉ IP và liệt kê các IP được phép.
    
    Args:
        log_data (str): Nội dung của file log.
        
    Returns:
        dict: Từ điển chứa thông tin về giới hạn quản trị theo địa chỉ IP và danh sách các IP được phép.
    """
    results = {}
    
    # Mẫu regex để tìm các lệnh access-class trên VTY lines
    access_class_pattern = r'^\s*access-class\s+(\d+)\s+in'
    
    # Mẫu regex để tìm các định nghĩa access-list
    access_list_pattern = r'^\s*access-list\s+(\d+)\s+permit\s+(\d+\.\d+\.\d+\.\d+)\s+(\d+\.\d+\.\d+\.\d+)'
    
    # Tách log_data thành các dòng để dễ dàng xử lý
    log_lines = log_data.splitlines()
    
    access_class_ids = []
    access_lists = {}
    
    # Tìm các access-class được áp dụng trên VTY lines
    for line in log_lines:
        match = re.match(access_class_pattern, line.strip(), re.IGNORECASE)
        if match:
            acl_id = match.group(1)
            access_class_ids.append(acl_id)
    
    # Tìm các định nghĩa access-list
    for line in log_lines:
        match = re.match(access_list_pattern, line.strip(), re.IGNORECASE)
        if match:
            acl_id = match.group(1)
            permit_ip = f"{match.group(2)} {match.group(3)}"
            if acl_id not in access_lists:
                access_lists[acl_id] = []
            access_lists[acl_id].append(permit_ip)
    
    # Thu thập tất cả các IP được phép từ các access-class
    allowed_ips = []
    evidence = []
    for acl_id in access_class_ids:
        permitted_ips = access_lists.get(acl_id, [])
        allowed_ips.extend(permitted_ips)
        if permitted_ips:
            evidence.append(f"access-class {acl_id} in - Permitted IPs: {', '.join(permitted_ips)}")
        else:
            evidence.append(f"access-class {acl_id} in - Không có IP nào được phép.")
    
    if access_class_ids and allowed_ips:
        results['Management IP Restriction'] = {
            'Configured': True,
            'Allowed_IPs': allowed_ips,
            'Evidence': "; ".join(evidence)
        }
        results['Compliance'] = "Configured - Giới hạn quản trị theo địa chỉ IP đã được cấu hình."
    else:
        results['Management IP Restriction'] = {
            'Configured': False,
            'Allowed_IPs': [],
            'Evidence': "Không tìm thấy cấu hình giới hạn quản trị theo địa chỉ IP."
        }
        results['Compliance'] = "Not Configured - Giới hạn quản trị theo địa chỉ IP chưa được cấu hình."
    
    return results

def display_results(ip_restriction):
    """
    Hiển thị kết quả kiểm tra giới hạn quản trị theo địa chỉ IP.
    
    Args:
        ip_restriction (dict): Thông tin về giới hạn quản trị theo địa chỉ IP.
    """
    print("\nGiới Hạn Quản Trị Theo Địa Chỉ IP:")
    ip_info = ip_restriction.get('Management IP Restriction', {})
    if ip_info.get('Configured'):
        print(f"- Giới Hạn Quản Trị: Đã được cấu hình.")
        print(f"  Bằng chứng: {ip_info.get('Evidence')}")
        print(f"- Các Địa Chỉ IP Được Phép Quản Trị: {', '.join(ip_info.get('Allowed_IPs'))}")
        print(f"- Tuân Thủ Giới Hạn Quản Trị: {ip_restriction['Compliance']}")
    else:
        print(f"- Giới Hạn Quản Trị: Không được cấu hình đúng.")
        print(f"  Bằng chứng: {ip_info.get('Evidence')}")
        print(f"- Tuân Thủ Giới Hạn Quản Trị: {ip_restriction['Compliance']}")
    print()

def main():
    parser = argparse.ArgumentParser(description="Kiểm tra giới hạn quản trị chỉ cho phép từ các địa chỉ IP cụ thể và liệt kê các IP được phép.")
    parser.add_argument("logfile", type=str, help="Đường dẫn tới file log cấu hình thiết bị Cisco.")
    args = parser.parse_args()
    
    log_path = Path(args.logfile)
    
    if not log_path.is_file():
        print(f"Lỗi: Không tìm thấy file '{log_path}'.")
        return
    
    try:
        with log_path.open("r", encoding="utf-8") as file_handle:
            log_data = file_handle.read()
    except IOError as e:
        print(f"Lỗi IO khi đọc file '{log_path}': {e}")
        return
    
    # Kiểm tra giới hạn quản trị theo địa chỉ IP
    ip_restriction = check_management_ip_restriction(log_data)
    
    # Hiển thị kết quả
    display_results(ip_restriction)

if __name__ == "__main__":
    main()
