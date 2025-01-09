import os
import re

def analyze_bpdu_guard_and_portfast(config_data):
    """
    Phân tích trạng thái BPDU Guard và PortFast từ cấu hình và lệnh 'show spanning-tree summary'.
    Args:
        config_data (str): Nội dung cấu hình hoặc lệnh 'show spanning-tree summary'.

    Returns:
        dict: Trạng thái BPDU Guard và danh sách các cổng PortFast.
    """
    stp_summary = {
        "bpdu_guard_default": "unknown",
        "portfast_default": "unknown",
        "portfast_interfaces": {}
    }

    # Phân tích trạng thái BPDU Guard Default từ lệnh 'show spanning-tree summary'
    bpdu_guard_pattern = r"Portfast BPDU Guard Default\s+is\s+(enabled|disabled)"
    portfast_pattern = r"Portfast Default\s+is\s+(enabled|disabled)"

    if match := re.search(bpdu_guard_pattern, config_data, re.IGNORECASE):
        stp_summary["bpdu_guard_default"] = match.group(1).strip()

    if match := re.search(portfast_pattern, config_data, re.IGNORECASE):
        stp_summary["portfast_default"] = match.group(1).strip()

    # Phân tích cấu hình interface để tìm PortFast và BPDU Guard
    interface_pattern = r"^interface (\S+)"
    portfast_enable_pattern = r"spanning-tree portfast(?! disable)"
    bpdu_guard_enable_pattern = r"spanning-tree bpduguard enable"

    current_interface = None
    current_config = []

    for line in config_data.splitlines():
        line = line.strip()

        # Xác định interface
        if match := re.match(interface_pattern, line):
            # Xử lý interface trước đó
            if current_interface:
                has_portfast = any(re.match(portfast_enable_pattern, config) for config in current_config)
                has_bpdu_guard = any(re.match(bpdu_guard_enable_pattern, config) for config in current_config)
                if has_portfast:
                    stp_summary["portfast_interfaces"][current_interface] = {
                        "portfast": "enabled",
                        "bpdu_guard": "enabled" if has_bpdu_guard else "disabled"
                    }

            # Chuyển sang interface mới
            current_interface = match.group(1)
            current_config = []

        # Thu thập cấu hình interface
        if current_interface:
            current_config.append(line)

        # Kết thúc cấu hình interface
        if line.startswith("!") and current_interface:
            has_portfast = any(re.match(portfast_enable_pattern, config) for config in current_config)
            has_bpdu_guard = any(re.match(bpdu_guard_enable_pattern, config) for config in current_config)
            if has_portfast:
                stp_summary["portfast_interfaces"][current_interface] = {
                    "portfast": "enabled",
                    "bpdu_guard": "enabled" if has_bpdu_guard else "disabled"
                }
            current_interface = None
            current_config = []

    # Xử lý interface cuối cùng
    if current_interface:
        has_portfast = any(re.match(portfast_enable_pattern, config) for config in current_config)
        has_bpdu_guard = any(re.match(bpdu_guard_enable_pattern, config) for config in current_config)
        if has_portfast:
            stp_summary["portfast_interfaces"][current_interface] = {
                "portfast": "enabled",
                "bpdu_guard": "enabled" if has_bpdu_guard else "disabled"
            }

    return stp_summary


def process_stp_and_portfast_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra trạng thái BPDU Guard và PortFast.
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
            stp_summary = analyze_bpdu_guard_and_portfast(config_data)

            # Hiển thị kết quả
            print("\033[1mKết quả phân tích 'show spanning-tree summary' và PortFast:\033[0m")
            print(f"BPDU Guard Default: {stp_summary['bpdu_guard_default']}")
            print(f"Portfast Default: {stp_summary['portfast_default']}")

            if stp_summary["portfast_interfaces"]:
                print("\033[1mDanh sách cổng PortFast và trạng thái BPDU Guard:\033[0m")
                all_disabled = True
                for interface, status in stp_summary["portfast_interfaces"].items():
                    print(f"Interface: {interface}, PortFast: {status['portfast']}, BPDU Guard: {status['bpdu_guard']}")
                    if status['bpdu_guard'] == "enabled":
                        all_disabled = False
                if all_disabled:
                    print("\033[33mTất cả các cổng PortFast đều bị disable BPDU Guard.\033[0m")
            else:
                print("\033[33mKhông tìm thấy cổng PortFast nào được cấu hình.\033[0m")

            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    # Gọi tới thư mục chứa file log
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_stp_and_portfast_logs(folder_path)
