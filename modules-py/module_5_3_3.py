# modules/module_5_3_3.py

import re
import argparse
from pathlib import Path

def check_disable_insecure_protocols(log_data):
    """
    Phân tích dữ liệu log để xác định việc vô hiệu hóa các giao thức quản trị không an toàn.

    Args:
        log_data (str): Nội dung của file log.

    Returns:
        dict: Từ điển chứa thông tin về việc vô hiệu hóa các giao thức không an toàn.
    """
    results = {}
    
    # Các mẫu regex để kiểm tra việc vô hiệu hóa các giao thức không an toàn
    patterns = {
        'Disable Telnet': r'^\s*transport\s+input\s+(?!telnet\b).*',
        'Disable HTTP': r'^\s*no\s+ip\s+http\s+server\b.*'
    }
    
    # Tách log_data thành các dòng để dễ dàng xử lý
    log_lines = log_data.splitlines()
    
    for desc, pattern in patterns.items():
        match = False
        evidence = ""
        disable_pattern = re.compile(pattern, re.IGNORECASE)
        for line in log_lines:
            if disable_pattern.match(line.strip()):
                match = True
                evidence = line.strip()
                break
        if desc == 'Disable Telnet':
            results[desc] = {
                'Disabled': match,
                'Evidence': evidence if match else "Telnet vẫn được cấu hình hoặc không có cấu hình rõ ràng."
            }
        elif desc == 'Disable HTTP':
            results[desc] = {
                'Disabled': match,
                'Evidence': evidence if match else "HTTP vẫn được cấu hình hoặc không có cấu hình rõ ràng."
            }
    
    # Đánh giá tuân thủ
    compliance = True
    insecure_protocols = []
    
    if not results.get('Disable Telnet', {}).get('Disabled', False):
        compliance = False
        insecure_protocols.append('Telnet')
    
    if not results.get('Disable HTTP', {}).get('Disabled', False):
        compliance = False
        insecure_protocols.append('HTTP')
    
    if compliance:
        results['Compliance'] = "Compliant - Các giao thức không an toàn đã được vô hiệu hóa."
    else:
        results['Compliance'] = f"Non-Compliant - Các giao thức không an toàn chưa được vô hiệu hóa: {', '.join(insecure_protocols)}."
    
    return results

def display_results(disable_protocols):
    """
    Hiển thị kết quả kiểm tra việc vô hiệu hóa các giao thức không an toàn.

    Args:
        disable_protocols (dict): Thông tin về việc vô hiệu hóa các giao thức không an toàn.
    """
    print("\nVô Hiệu Hóa Giao Thức Không An Toàn:")
    for key, info in disable_protocols.items():
        if key == 'Compliance':
            continue  # Bỏ qua khóa 'Compliance' trong vòng lặp
        status = 'Đã vô hiệu hóa' if info['Disabled'] else 'Chưa vô hiệu hóa'
        print(f"- {key}: {status}")
        print(f"  Bằng chứng: {info['Evidence']}")
    print(f"- Tuân Thủ Vô Hiệu Hóa Giao Thức: {disable_protocols['Compliance']}\n")

def main():
    parser = argparse.ArgumentParser(description="Kiểm tra việc vô hiệu hóa các giao thức không an toàn (Telnet, HTTP).")
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
    
    # Kiểm tra việc vô hiệu hóa các giao thức không an toàn
    disable_protocols = check_disable_insecure_protocols(log_data)
    
    # Hiển thị kết quả
    display_results(disable_protocols)

if __name__ == "__main__":
    main()
