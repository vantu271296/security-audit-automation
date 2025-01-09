import re
from pathlib import Path

def check_firmware_version(log_data):
    """
    Phân tích dữ liệu log để xác định phiên bản firmware của thiết bị Cisco.
    
    Args:
        log_data (str): Nội dung của file log.
        
    Returns:
        dict: Từ điển chứa thông tin về phiên bản firmware.
    """
    results = {}

    # Mẫu regex cho Cisco IOS-XE
    ios_xe_pattern = r"Cisco IOS[- ]XE Software.*Version\s+([\d\.\(\)\w\-]+)"
    ios_xe_match = re.search(ios_xe_pattern, log_data, re.IGNORECASE)
    if ios_xe_match:
        results['Cisco IOS-XE'] = ios_xe_match.group(1)

    # Nếu không tìm thấy IOS-XE, tìm kiếm Cisco IOS
    if not ios_xe_match:
        ios_pattern = r"Cisco IOS Software.*Version\s+([\d\.\(\)\w\-]+)"
        ios_match = re.search(ios_pattern, log_data, re.IGNORECASE)
        if ios_match:
            results['Cisco IOS'] = ios_match.group(1)

    # Nếu không tìm thấy phiên bản nào
    if not results:
        results['Firmware Version'] = "Not Found"

    return results

def check_management_access(log_data):
    """
    Phân tích dữ liệu log để xác định phương thức quản trị thiết bị được cấu hình.
    
    Args:
        log_data (str): Nội dung của file log.
        
    Returns:
        dict: Từ điển chứa thông tin về các phương thức quản trị được cấu hình cùng bằng chứng.
    """
    results = {}
    
    # Các mẫu regex để kiểm tra cấu hình phương thức quản trị
    patterns = {
        'Console Connection': {
            'enable': r'^line\s+console\s+0\b.*',
            'disable': None  # Console thường không có lệnh disable
        },
        'SSHv2': {
            'enable': r'^\s*ip\s+ssh\s+version\s+2\b.*',
            'disable': r'^\s*no\s+ip\s+ssh\b.*'
        },
        'HTTPS': {
            'enable': r'^\s*ip\s+http\s+secure-server\b.*',
            'disable': r'^\s*no\s+ip\s+http\b.*'
        },
        'Telnet': {
            'enable': r'^\s*transport\s+input\s+telnet\b.*',
            'disable': r'^\s*transport\s+input\s+(?!telnet)\b.*'
        }
    }
    
    # Tách log_data thành các dòng để dễ dàng xử lý
    log_lines = log_data.splitlines()
    
    for method, cmds in patterns.items():
        evidence = None
        status = False  # Mặc định là không được cấu hình
        
        # Tìm kiếm lệnh enable
        if cmds['enable']:
            enable_pattern = re.compile(cmds['enable'], re.IGNORECASE)
            for line in log_lines:
                if enable_pattern.match(line.strip()):
                    evidence = line.strip()
                    status = True
                    break
        
        # Nếu không tìm thấy lệnh enable, kiểm tra lệnh disable nếu có
        if not status and cmds['disable']:
            disable_pattern = re.compile(cmds['disable'], re.IGNORECASE)
            for line in log_lines:
                if disable_pattern.match(line.strip()):
                    evidence = line.strip()
                    status = False
                    break
            else:
                # Nếu không tìm thấy lệnh disable, hiểu là phương thức không được cấu hình
                evidence = f"No configuration found for {method}."
        
        # Nếu không có lệnh disable và không tìm thấy lệnh enable
        if not status and not evidence:
            evidence = f"No configuration found for {method}."
        
        results[method] = {
            'Configured': status,
            'Evidence': evidence
        }
    
    # Đánh giá tuân thủ
    compliance = True
    non_secure_methods = []
    
    # Kiểm tra sự xuất hiện của các phương thức không an toàn
    if results.get('Telnet', {}).get('Configured', False):
        compliance = False
        non_secure_methods.append('Telnet')
    
    # Thêm thông tin tuân thủ vào kết quả
    if compliance:
        results['Compliance'] = "Compliant"
    else:
        results['Compliance'] = f"Non-Compliant - Insecure methods configured: {', '.join(non_secure_methods)}"
    
    return results

def display_results(file_path, versions, access_methods):
    """
    Hiển thị kết quả kiểm tra firmware và phương thức quản trị.
    
    Args:
        file_path (Path): Đường dẫn tới file log.
        versions (dict): Thông tin về phiên bản firmware.
        access_methods (dict): Thông tin về các phương thức quản trị.
    """
    print(f"--- Thông Tin từ '{file_path.name}' ---\n")
    
    print("Phiên Bản Firmware:")
    for key, value in versions.items():
        print(f"- {key}: {value}")
    
    print("\nPhương Thức Quản Trị:")
    for key, info in access_methods.items():
        if key != 'Compliance':
            status = 'Được cấu hình' if info['Configured'] else 'Không được cấu hình'
            print(f"- {key}: {status}")
            print(f"  Bằng chứng: {info['Evidence']}")
    print(f"- Tuân Thủ: {access_methods['Compliance']}")
    print("-" * 50)

# Hàm chính để kiểm tra log files
if __name__ == "__main__":
    log_files = [
        Path("test/10.22.122.10HN-22HV-ROUTER-WIFI.log"),  # Cập nhật đường dẫn tới file log
        Path("test/10.22.203.102-HN-22HV-SW-ACCESS-02-20250106.log")
    ]

    for file_path in log_files:
        try:
            with file_path.open("r", encoding="utf-8") as file_handle:
                log_data = file_handle.read()
        except FileNotFoundError:
            print(f"Lỗi: Không tìm thấy file '{file_path}'.")
            continue
        except IOError as e:
            print(f"Lỗi IO khi đọc file '{file_path}': {e}")
            continue

        # Kiểm tra phiên bản firmware
        versions = check_firmware_version(log_data)
        
        # Kiểm tra phương thức quản trị
        access_methods = check_management_access(log_data)

        # Hiển thị kết quả
        display_results(file_path, versions, access_methods)
