import os
import re

def check_invalid_ip_ranges(config_data):
    if not re.search(r"router bgp \d+", config_data, re.IGNORECASE):
        print("\033[33mKhông Áp Dụng:\033[0m Thiết bị không cấu hình BGP.")
        return

    invalid_ip_patterns = [
        r"10\.0\.0\.0/8",
        r"172\.16\.0\.0/12",
        r"192\.168\.0\.0/16",
        r"fc00::/7",
        r"0\.0\.0\.0/0 ge 25 le 32",
        r"::/0 ge 49 le 128"
    ]

    violations = []
    for pattern in invalid_ip_patterns:
        if not re.search(pattern, config_data, re.IGNORECASE):
            violations.append(pattern)

    if violations:
        print("\033[31mKhông Tuân Thủ:\033[0m Không chặn việc quảng bá/nhận quảng bá các dải IP không hợp lệ. Các dải IP chưa được cấu hình chặn:")
        for ip in violations:
            print(f"  - {ip}")
    else:
        print("\033[32mTuân Thủ:\033[0m Đã chặn việc quảng bá/nhận quảng bá các dải IP không hợp lệ.")

# Hàm gọi kiểm tra file log
def run_module(folder_path):
    log_files = [f for f in os.listdir(folder_path) if f.endswith('.log') or f.endswith('.txt')]

    if not log_files:
        print("Không tìm thấy file log nào.")
        return

    for log_file in log_files:
        print(f"\nĐang kiểm tra file: {log_file}")
        with open(os.path.join(folder_path, log_file), "r", encoding="utf-8") as file:
            config_data = file.read()
            check_invalid_ip_ranges(config_data)

# Chạy module
if __name__ == "__main__":
    folder_path = r"C:\Users\admin\Desktop\automation\Test"  # Thay đường dẫn tới thư mục file log của bạn
    run_module(folder_path)
