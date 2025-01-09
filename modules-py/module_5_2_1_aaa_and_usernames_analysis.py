import os
import re

def analyze_aaa_and_usernames(log_content):

    results = {
        "tacacs_servers": [],
        "radius_servers": [],
        "usernames": [],
        "issues": [],
        "evidence": []
    }


    # Tìm server TACACS
    tacacs_pattern = r"tacacs server (\S+)"
    tacacs_servers = re.findall(tacacs_pattern, log_content, re.IGNORECASE)
    if tacacs_servers:
        results["tacacs_servers"].extend(tacacs_servers)
        results["evidence"].append(f"Tìm thấy server TACACS: {', '.join(tacacs_servers)}")
    else:
        results["issues"].append("Không tìm thấy server TACACS trong cấu hình.")

    # Tìm server RADIUS
    radius_pattern = r"radius server (\S+)"
    radius_servers = re.findall(radius_pattern, log_content, re.IGNORECASE)
    if radius_servers:
        results["radius_servers"].extend(radius_servers)
        results["evidence"].append(f"Tìm thấy server RADIUS: {', '.join(radius_servers)}")
    else:
        results["issues"].append("Không tìm thấy server RADIUS trong cấu hình.")

    # Tìm tất cả các dòng cấu hình username
    username_pattern = r"^username .*"
    usernames = re.findall(username_pattern, log_content, re.MULTILINE | re.IGNORECASE)
    results["usernames"] = set(results.get("usernames", []))  # Chuyển thành set để loại bỏ trùng lặp
    results["usernames"].update(usernames)
    return results

def process_logs_for_aaa_and_usernames(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra cấu hình AAA và username.
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

            results = analyze_aaa_and_usernames(log_content)

         

            if results["tacacs_servers"]:
                print(f"- TACACS servers được cấu hình: {', '.join(results['tacacs_servers'])}")
            else:
                print("- Không Tuân Thủ: Không tìm thấy server TACACS.")

            if results["radius_servers"]:
                print(f"- RADIUS servers được cấu hình: {', '.join(results['radius_servers'])}")
            else:
                print("- Không Tuân Thủ: Không tìm thấy server RADIUS.")

            # Hiển thị username
            if results["usernames"]:
                print("Các dòng cấu hình username được phát hiện:")
                for username in results["usernames"]:
                    print(f"  + {username}")
            else:
                print("Không tìm thấy bất kỳ cấu hình username nào.")

            # Hiển thị vấn đề phát hiện
            if results["issues"]:
                print("\nCác vấn đề phát hiện:")
                for issue in results["issues"]:
                    print(f"  - {issue}")
            else:
                print("Cấu hình AAA và username tuân thủ.")

        except Exception as e:
            print(f"Lỗi khi xử lý file {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"test"  # Thay bằng đường dẫn tới thư mục file log
    process_logs_for_aaa_and_usernames(folder_path)
