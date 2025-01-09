import os
import re

def analyze_backup_configuration(log_content):
    """
    Phân tích cấu hình sao lưu từ log.
    Args:
        log_content (str): Nội dung log chứa cấu hình.

    Returns:
        dict: Kết quả phân tích sao lưu.
    """
    results = {
        "backup_path": None,
        "schedule": None,
        "compliant": False,
        "issues": set()  # Sử dụng `set` để tránh lặp thông báo
    }

    # Kiểm tra vị trí sao lưu
    backup_path_pattern = r"archive path (\S+)"
    backup_path_match = re.search(backup_path_pattern, log_content, re.IGNORECASE)
    if backup_path_match:
        results["backup_path"] = backup_path_match.group(1)
        if any(keyword in results["backup_path"].lower() for keyword in ["ftp", "scp", "tftp"]):
            # Lưu cấu hình ở vị trí hợp lệ
            pass
        else:
            results["issues"].add("Không tuân thủ: Vị trí lưu cấu hình không phải máy chủ từ xa (FTP/SCP/TFTP).")
    else:
        results["issues"].add("Không tìm thấy cấu hình vị trí lưu sao lưu.")

    # Kiểm tra lịch sao lưu
    schedule_pattern = r"archive time-period (\d+)"
    schedule_match = re.search(schedule_pattern, log_content, re.IGNORECASE)
    if schedule_match:
        period = int(schedule_match.group(1))
        if period <= 7:  # Kiểm tra định kỳ tối thiểu 1 lần/tuần
            results["schedule"] = f"{period} ngày/lần"
        else:
            results["issues"].add("Không tuân thủ: Lịch sao lưu không đủ thường xuyên (hơn 7 ngày/lần).")
    else:
        results["issues"].add("Không tìm thấy cấu hình lịch sao lưu.")

    # Đánh giá tuân thủ
    if results["backup_path"] and results["schedule"]:
        if len(results["issues"]) == 0:
            results["compliant"] = True

    return results

def process_backup_logs(folder_path):
    """
    Kiểm tra cấu hình sao lưu từ các file log.
    Args:
        folder_path (str): Đường dẫn tới thư mục chứa file log.

    Returns:
        None
    """
    log_files = [f for f in os.listdir(folder_path) if f.endswith(".log") or f.endswith(".txt")]

    if not log_files:
        print("Không tìm thấy file log nào trong thư mục.")
        return

    for log_file in log_files:
        file_path = os.path.join(folder_path, log_file)
        print(f"\nĐang kiểm tra file: {file_path}")
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                log_content = file.read()

            # Phân tích cấu hình sao lưu
            results = analyze_backup_configuration(log_content)

            # In kết quả
            if results["compliant"]:
                print("\033[32mTuân Thủ:\033[0m Cấu hình sao lưu đầy đủ.")
                print(f"  - Vị trí sao lưu: {results['backup_path']}")
                print(f"  - Lịch sao lưu: {results['schedule']}")
            else:
                print("\033[31mKhông Tuân Thủ:\033[0m Cấu hình sao lưu không đầy đủ.")
                for issue in sorted(results["issues"]):  # Sắp xếp để in ra gọn gàng
                    print(f"  - {issue}")

        except Exception as e:
            print(f"Lỗi khi xử lý file {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"C:\Users\admin\Desktop\automation\Test"  # Thay đường dẫn tới thư mục file log
    process_backup_logs(folder_path)
