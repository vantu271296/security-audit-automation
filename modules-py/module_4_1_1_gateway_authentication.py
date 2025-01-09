import os
import re

def analyze_gateway_authentication(config_data):
    """
    Phân tích cấu hình xác thực của các giao thức dự phòng gateway.
    Args:
        config_data (str): Nội dung cấu hình.

    Returns:
        dict: Thông tin xác thực của các giao thức VRRP, HSRP, GLBP, và NSRP.
    """
    authentication_status = {
        "VRRP": [],
        "HSRP": [],
        "GLBP": [],
        "NSRP": [],
        "non_authenticated": [],
        "configured_protocols": False
    }

    # Regex cho các giao thức và xác thực
    vrrp_pattern = r"vrrp \d+ authentication (\S+)"
    hsrp_pattern = r"standby \d+ authentication (\S+)"
    glbp_pattern = r"glbp \d+ authentication (\S+)"
    nsrp_pattern = r"set nsrp vsd-group id \d+.*authentication (\S+)"
    protocol_patterns = [vrrp_pattern, hsrp_pattern, glbp_pattern, nsrp_pattern]

    # Kiểm tra từng giao thức và xác thực
    for pattern, protocol in zip(protocol_patterns, ["VRRP", "HSRP", "GLBP", "NSRP"]):
        matches = re.finditer(pattern, config_data, re.IGNORECASE)
        for match in matches:
            authentication_status[protocol].append(match.group(1))
            authentication_status["configured_protocols"] = True  # Đánh dấu rằng giao thức được cấu hình

    # Xác định giao thức không có cấu hình xác thực
    for protocol in ["VRRP", "HSRP", "GLBP", "NSRP"]:
        if not authentication_status[protocol]:
            authentication_status["non_authenticated"].append(protocol)

    return authentication_status


def process_gateway_authentication_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra xác thực của các giao thức dự phòng gateway.
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
            auth_status = analyze_gateway_authentication(config_data)

            # Hiển thị kết quả
            print("\033[1mKết quả kiểm tra xác thực giao thức dự phòng gateway:\033[0m")
            if auth_status["configured_protocols"]:
                for protocol, keys in auth_status.items():
                    if protocol != "non_authenticated" and protocol != "configured_protocols":
                        if keys:
                            print(f"\033[32m{protocol} có xác thực:\033[0m {', '.join(keys)}")
                        else:
                            print(f"\033[31m{protocol} không có cấu hình xác thực.\033[0m")

                if auth_status["non_authenticated"]:
                    print("\033[31mCảnh báo: Các giao thức không có xác thực:\033[0m")
                    print(", ".join(auth_status["non_authenticated"]))
            else:
                print("\033[33mKhông phát hiện giao thức dự phòng nào được cấu hình.\033[0m")

            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_gateway_authentication_logs(folder_path)
