import os
import re

def check_tcp_port_filter(config_data):
    if not re.search(r"router bgp \d+", config_data, re.IGNORECASE):
        print("\033[33mKhông Áp Dụng:\033[0m Thiết bị không cấu hình BGP.")
        return

    acl_patterns = [
        r"access-list .* permit tcp \S+ \S+ eq 179",
        r"access-list .* deny tcp any any eq 179"
    ]

    compliance = [pattern for pattern in acl_patterns if re.search(pattern, config_data, re.IGNORECASE)]

    if compliance:
        print("\033[32mTuân Thủ:\033[0m Đã cấu hình filter cho TCP port 179 trên các interface đấu nối eBGP.")
    else:
        print("\033[31mKhông Tuân Thủ:\033[0m Không cấu hình filter cho TCP port 179 trên các interface đấu nối eBGP.")

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
            check_tcp_port_filter(config_data)

# Chạy module
if __name__ == "__main__":
    folder_path = r"C:\Users\admin\Desktop\automation\Test"  # Thay đường dẫn tới thư mục file log của bạn
    run_module(folder_path)
