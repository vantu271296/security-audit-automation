import os
import re

def analyze_non_admin_usernames(log_content):
    """
    Phân tích và liệt kê các tài khoản không phải admin từ file log.
    Args:
        log_content (str): Nội dung file log.

    Returns:
        dict: Kết quả phân tích danh sách username.
    """
    results = {
        "admin_accounts": [],
        "non_admin_accounts": [],
        "evidence": []
    }

    # Tìm tất cả các dòng cấu hình username
    username_pattern = r"^username (\S+).*"
    usernames = re.findall(username_pattern, log_content, re.MULTILINE | re.IGNORECASE)

    # Phân loại tài khoản
    for username in usernames:
        if username.lower() == "admin":
            results["admin_accounts"].append(username)
        else:
            results["non_admin_accounts"] = set(results.get("usernames", []))  # Chuyển thành set để loại bỏ trùng lặp
            results["non_admin_accounts"].update(usernames)

    return results

def process_logs_for_non_admin_usernames(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra danh sách tài khoản không phải admin.
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

            results = analyze_non_admin_usernames(log_content)

            # In kết quả
            print("Danh sách tài khoản phát hiện:")
            if results["admin_accounts"]:
                print(f"  + Tài khoản admin: {', '.join(results['admin_accounts'])}")
            else:
                print("  + Không tìm thấy tài khoản admin.")

            if results["non_admin_accounts"]:
                print("  + Tài khoản không phải admin:")
                for account in results["non_admin_accounts"]:
                    print(f"    - {account}")
            else:
                print("  + Không tìm thấy tài khoản không phải admin.")

            # # Hiển thị bằng chứng
            # if results["evidence"]:
            #     print("\nBằng chứng phát hiện:")
            #     for evidence in results["evidence"]:
            #         print(f"  - {evidence}")

        except Exception as e:
            print(f"Lỗi khi xử lý file {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"test"  # Thay bằng đường dẫn tới thư mục file log
    process_logs_for_non_admin_usernames(folder_path)
