import os
import re

def analyze_user_isolation(config_data):
    """
    Phân tích cấu hình isolate trên các cổng để ngăn chặn kết nối ngang hàng.
    Args:
        config_data (str): Nội dung cấu hình.

    Returns:
        dict: Danh sách các cổng được cấu hình hoặc không cấu hình isolate.
    """
    isolation_status = {
        "isolated": [],
        "not_isolated": []
    }

    # Regex để phân tích lệnh
    interface_pattern = r"^interface (\S+)"
    isolate_pattern = r"switchport protected"
    gateway_pattern = r"switchport mode trunk|ip address"

    current_interface = None
    current_config = []

    for line in config_data.splitlines():
        line = line.strip()

        # Xác định interface
        if match := re.match(interface_pattern, line):
            # Kiểm tra trạng thái isolate trên interface trước đó
            if current_interface:
                is_isolated = any(re.match(isolate_pattern, config) for config in current_config)
                is_gateway = any(re.match(gateway_pattern, config) for config in current_config)
                if is_gateway:
                    isolation_status["not_isolated"].append(current_interface)
                elif is_isolated:
                    isolation_status["isolated"].append(current_interface)
                else:
                    isolation_status["not_isolated"].append(current_interface)

            # Chuyển sang interface mới
            current_interface = match.group(1)
            current_config = []

        # Thu thập cấu hình của interface
        if current_interface:
            current_config.append(line)

        # Kết thúc cấu hình interface
        if line.startswith("!") and current_interface:
            is_isolated = any(re.match(isolate_pattern, config) for config in current_config)
            is_gateway = any(re.match(gateway_pattern, config) for config in current_config)
            if is_gateway:
                isolation_status["not_isolated"].append(current_interface)
            elif is_isolated:
                isolation_status["isolated"].append(current_interface)
            else:
                isolation_status["not_isolated"].append(current_interface)
            current_interface = None
            current_config = []

    # Xử lý interface cuối cùng
    if current_interface:
        is_isolated = any(re.match(isolate_pattern, config) for config in current_config)
        is_gateway = any(re.match(gateway_pattern, config) for config in current_config)
        if is_gateway:
            isolation_status["not_isolated"].append(current_interface)
        elif is_isolated:
            isolation_status["isolated"].append(current_interface)
        else:
            isolation_status["not_isolated"].append(current_interface)

    return isolation_status


def process_user_isolation_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra cấu hình isolate người dùng.
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
            isolation_status = analyze_user_isolation(config_data)

            # Hiển thị kết quả
            print("\033[1mCấu hình isolate người dùng:\033[0m")
            if isolation_status["isolated"]:
                print("\033[32mCác cổng được cấu hình isolate:\033[0m")
                for interface in isolation_status["isolated"]:
                    print(f"- {interface}")
            else:
                print("\033[33mKhông có cổng nào được cấu hình isolate.\033[0m")

            if isolation_status["not_isolated"]:
                print("\033[31mCác cổng không được cấu hình isolate:\033[0m")
                for interface in isolation_status["not_isolated"]:
                    print(f"- {interface}")
            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_user_isolation_logs(folder_path)
