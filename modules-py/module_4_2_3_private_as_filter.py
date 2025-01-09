import os
import re

def check_private_as_numbers(config_data):
    # Kiểm tra cấu hình BGP
    if not re.search(r"router bgp \d+", config_data, re.IGNORECASE):
        print("\033[33mKhông Áp Dụng:\033[0m Thiết bị không cấu hình BGP.")
        return

    private_as_numbers = list(range(64512, 65536))
    violations = []
    remove_private_as_compliance = False

    # Kiểm tra private AS numbers qua route-map hoặc as-path
    for as_number in private_as_numbers:
        if re.search(fr"^neighbor \S+.*as-path \d+.*{as_number}", config_data, re.MULTILINE):
            violations.append(as_number)

    # Kiểm tra sử dụng lệnh remove-private-as
    if re.search(r"neighbor \S+ remove-private-as", config_data, re.IGNORECASE):
        remove_private_as_compliance = True

    # In kết quả phân tích
    if remove_private_as_compliance:
        print("\033[32mTuân Thủ:\033[0m Đã chặn việc quảng bá bản tin BGP Update chứa thông tin private AS number.")
    elif violations:
        print("\033[31mKhông Tuân Thủ:\033[0m Không chặn việc quảng bá bản tin BGP Update chứa thông tin private AS number. Tìm thấy các AS private được quảng bá:")
        for asn in violations:
            print(f"  - AS {asn}")
    else:
        print("\033[31mKhông Tuân Thủ:\033[0m Không chặn việc quảng bá bản tin BGP Update chứa thông tin private AS number.")

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
            check_private_as_numbers(config_data)

# Chạy module
if __name__ == "__main__":
    folder_path = r"C:\Users\admin\Desktop\automation\Test"  # Thay đường dẫn tới thư mục file log của bạn
    run_module(folder_path)
