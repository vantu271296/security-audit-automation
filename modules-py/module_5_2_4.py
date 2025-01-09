import os
import re

def analyze_password_policies(log_content):
    results = {
        "policy_enabled": False,
        "policies": [],
        "issues": [],
        "evidence": [],
        "passwords":[]
    }

    # Tìm kiếm các cấu hình liên quan đến chính sách mật khẩu
    policies = {
        "service password-encryption": r"service password-encryption",
        "minimum password length": r"security passwords min-length (\d+)",
        "password complexity (AAA)": r"aaa password policy enable",
        "AAA password policy rules": r"aaa password policy (.*)",
        "sensitive keywords": r"\b(key|secret|password)\b"
    }

    lines = log_content.splitlines()
    
    for policy_name, pattern in policies.items():
        found = False
        for line in lines:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                results["policy_enabled"] = True
                found = True
                policy_entry = f"{policy_name}: {line.strip()}"
                evidence_entry = f"Tìm thấy cấu hình: {policy_name}. Dòng: {line.strip()}"
                
                if policy_entry not in results["policies"]:
                    results["policies"].append(policy_entry)
                if evidence_entry not in results["evidence"]:
                    results["evidence"].append(evidence_entry)
        if not found:
            results["issues"].append(f"Không tìm thấy cấu hình: {policy_name}")


    return results

def process_logs_for_password_policies(folder_path):
 
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

            results = analyze_password_policies(log_content)

            # In kết quả
            if results["policy_enabled"]:
                print("- Chính sách mật khẩu mạnh đã được bật với các cấu hình sau:")
                for policy in results["policies"]:
                    print(f"  + {policy}")
            else:
                print("- Không Tuân Thủ: Chính sách mật khẩu mạnh chưa được bật.")

            # Hiển thị vấn đề
            if results["issues"]:
                print("\nCác vấn đề phát hiện:")
                for issue in results["issues"]:
                    print(f"  - {issue}")

            # Hiển thị bằng chứng
            if results["evidence"]:
                print("\nBằng chứng cấu hình:")
                for evidence in results["evidence"]:
                    print(f"  - {evidence}")

        except Exception as e:
            print(f"Lỗi khi xử lý file {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"test"  # Thay bằng đường dẫn tới thư mục file log
    process_logs_for_password_policies(folder_path)
