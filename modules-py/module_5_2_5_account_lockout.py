import os
import re

def analyze_account_lockout(log_content):
    """
    Phân tích cấu hình khóa tài khoản sau một số lần đăng nhập sai.
    Args:
        log_content (str): Nội dung file log.

    Returns:
        dict: Kết quả phân tích cấu hình account lockout.
    """
    results = {
        "lockout_found": False,
        "attempts_limit": None,
        "lockout_duration": None,
        "issues": [],
        "evidence": []
    }

    # Tìm cấu hình login block-for
    lockout_pattern = r"login block-for (\d+) attempts (\d+) within (\d+)"
    match = re.search(lockout_pattern, log_content, re.IGNORECASE)

    if match:
        lockout_duration, attempts_limit, _ = match.groups()
        results["lockout_found"] = True
        results["attempts_limit"] = int(attempts_limit)
        results["lockout_duration"] = int(lockout_duration)
        results["evidence"].append(f"Tìm thấy cấu hình: {match.group(0)}")

        # Kiểm tra khuyến nghị
        if int(attempts_limit) > 5:
            results["issues"].append("Số lần đăng nhập sai trước khi khóa vượt quá 5 (khuyến nghị nhỏ hơn 5).")
        if int(lockout_duration) < 5:
            results["issues"].append("Thời gian khóa tài khoản nhỏ hơn 5 phút (khuyến nghị lớn hơn 5 phút).")
    else:
        results["issues"].append("Không tìm thấy cấu hình khóa tài khoản (login block-for).")

    return results

def process_logs_for_account_lockout(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra cấu hình khóa tài khoản.
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

            results = analyze_account_lockout(log_content)

            # In kết quả
            if results["lockout_found"]:
                print("- Tìm thấy cấu hình khóa tài khoản:")
                for evidence in results["evidence"]:
                    print(f"  + {evidence}")

                print(f"  + Số lần đăng nhập sai trước khi khóa: {results['attempts_limit']}")
                print(f"  + Thời gian khóa tài khoản: {results['lockout_duration']} phút")

                if results["issues"]:
                    print("\nCác vấn đề phát hiện:")
                    for issue in results["issues"]:
                        print(f"  - {issue}")
                else:
                    print("Cấu hình khóa tài khoản tuân thủ.")
            else:
                print("- Không Tuân Thủ: Không tìm thấy cấu hình khóa tài khoản.")

        except Exception as e:
            print(f"Lỗi khi xử lý file {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"test"  # Thay bằng đường dẫn tới thư mục file log
    process_logs_for_account_lockout(folder_path)
