# modules/module_5_3_4.py

import re
import argparse
from pathlib import Path

def check_session_timeout(log_data, max_timeout=15):
    """
    Phân tích dữ liệu log để xác định thời gian time-out của các phiên kết nối quản trị.
    
    Args:
        log_data (str): Nội dung của file log.
        max_timeout (int): Thời gian time-out tối đa (tính bằng phút).
        
    Returns:
        dict: Từ điển chứa thông tin về thời gian time-out và đánh giá tuân thủ.
    """
    results = {}
    
    # Mẫu regex để kiểm tra cấu hình time-out trên VTY lines
    # Giả sử cấu hình time-out được thiết lập thông qua lệnh "exec-timeout <minutes> <seconds>"
    timeout_pattern = r'^\s*exec-timeout\s+(\d+)\s+\d+'
    
    # Tách log_data thành các dòng để dễ dàng xử lý
    log_lines = log_data.splitlines()
    
    timeouts = []
    for line in log_lines:
        match = re.match(timeout_pattern, line.strip(), re.IGNORECASE)
        if match:
            minutes = int(match.group(1))
            timeouts.append(minutes)
    
    if timeouts:
        # Lấy time-out nhỏ nhất nếu có nhiều cấu hình
        min_timeout = min(timeouts)
        evidence = f"exec-timeout {min_timeout} phút"
        results['Session Timeout'] = {
            'Configured': min_timeout <= max_timeout,
            'Timeout': min_timeout,
            'Evidence': evidence
        }
    else:
        results['Session Timeout'] = {
            'Configured': False,
            'Timeout': None,
            'Evidence': "Không tìm thấy cấu hình thời gian time-out cho các phiên kết nối quản trị."
        }
    
    # Đánh giá tuân thủ
    if results['Session Timeout']['Configured']:
        results['Compliance'] = f"Compliant - Thời gian time-out là {results['Session Timeout']['Timeout']} phút."
    else:
        results['Compliance'] = "Non-Compliant - Thời gian time-out không được cấu hình đúng hoặc không có cấu hình rõ ràng."
    
    return results

def display_results(session_timeout):
    """
    Hiển thị kết quả kiểm tra thời gian time-out của các phiên kết nối quản trị.

    Args:
        session_timeout (dict): Thông tin về thời gian time-out của các phiên kết nối quản trị.
    """
    print("\nKiểm Tra Thời Gian Time-Out Của Phiên Kết Nối Quản Trị:")
    timeout_info = session_timeout.get('Session Timeout', {})
    if timeout_info.get('Configured'):
        print(f"- Thời Gian Time-Out: {timeout_info.get('Timeout')} phút")
        print(f"  Bằng chứng: {timeout_info.get('Evidence')}")
        print(f"- Tuân Thủ Time-Out: {session_timeout['Compliance']}\n")
    else:
        print(f"- Thời Gian Time-Out: Chưa cấu hình hoặc không đúng")
        print(f"  Bằng chứng: {timeout_info.get('Evidence')}")
        print(f"- Tuân Thủ Time-Out: {session_timeout['Compliance']}\n")

def main():
    parser = argparse.ArgumentParser(description="Kiểm tra thời gian time-out của các phiên kết nối quản trị.")
    parser.add_argument("logfile", type=str, help="Đường dẫn tới file log cấu hình thiết bị Cisco.")
    parser.add_argument("--max_timeout", type=int, default=15, help="Thời gian time-out tối đa (tính bằng phút). Mặc định là 15.")
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
    
    # Kiểm tra thời gian time-out của các phiên kết nối quản trị
    session_timeout = check_session_timeout(log_data, args.max_timeout)
    
    # Hiển thị kết quả
    display_results(session_timeout)

if __name__ == "__main__":
    main()
