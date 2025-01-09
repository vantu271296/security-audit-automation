import os
import re

def analyze_igp_authentication(config_data):
    """
    Phân tích cấu hình của các giao thức định tuyến IGP (RIP, OSPF, ISIS).
    Args:
        config_data (str): Nội dung cấu hình.

    Returns:
        dict: Thông tin về trạng thái cấu hình và xác thực của các giao thức RIP, OSPF, và ISIS.
    """
    authentication_status = {
        "RIP": {"configured": False, "authenticated": False},
        "OSPF": {"configured": False, "authenticated": False},
        "ISIS": {"configured": False, "authenticated": False}
    }

    # Regex kiểm tra cấu hình giao thức
    rip_config_pattern = r"^router rip$"
    ospf_config_pattern = r"^router ospf \d+"
    isis_config_pattern = r"^router isis"

    # Regex kiểm tra xác thực
    rip_auth_pattern = r"ip rip authentication mode md5"
    ospf_auth_pattern = r"area \d+ authentication(?: message-digest)?"
    isis_auth_pattern = r"isis authentication (?:mode md5|key \S+)"

    # Kiểm tra cấu hình giao thức
    if re.search(rip_config_pattern, config_data, re.MULTILINE | re.IGNORECASE):
        authentication_status["RIP"]["configured"] = True
        if re.search(rip_auth_pattern, config_data, re.MULTILINE | re.IGNORECASE):
            authentication_status["RIP"]["authenticated"] = True

    if re.search(ospf_config_pattern, config_data, re.MULTILINE | re.IGNORECASE):
        authentication_status["OSPF"]["configured"] = True
        if re.search(ospf_auth_pattern, config_data, re.MULTILINE | re.IGNORECASE):
            authentication_status["OSPF"]["authenticated"] = True

    if re.search(isis_config_pattern, config_data, re.MULTILINE | re.IGNORECASE):
        authentication_status["ISIS"]["configured"] = True
        if re.search(isis_auth_pattern, config_data, re.MULTILINE | re.IGNORECASE):
            authentication_status["ISIS"]["authenticated"] = True

    return authentication_status


def process_igp_authentication_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra cấu hình của các giao thức định tuyến IGP.
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
            auth_status = analyze_igp_authentication(config_data)

            # Hiển thị kết quả
            print("\033[1mKết quả kiểm tra cấu hình giao thức IGP:\033[0m")
            for protocol, status in auth_status.items():
                if status["configured"]:
                    if status["authenticated"]:
                        print(f"\033[32m{protocol} được cấu hình và có xác thực.\033[0m")
                    else:
                        print(f"\033[33m{protocol} được cấu hình nhưng không có xác thực.\033[0m")
                else:
                    print(f"\033[31m{protocol} không được cấu hình.\033[0m")

            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_igp_authentication_logs(folder_path)
