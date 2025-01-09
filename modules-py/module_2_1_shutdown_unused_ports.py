import os

def extract_interface_brief(config_data):

    print()
    print("\033[1mMục 2.1: Yêu cầu phải shutdown port không sử dụng.\033[0m")
    
    try:
        if config_data is None:
            print("\033[31mKhông có dữ liệu để xử lý.\033[0m")
            return

        # Tách các dòng log
        config_lines = config_data.splitlines()
        start_idx = -1
        hostname = None

        # Tìm dòng lệnh "show ip interface brief"
        for i, line in enumerate(config_lines):
            cleaned_line = ' '.join(line.split()).strip()
            if hostname is None and "#" in cleaned_line:
                hostname = cleaned_line.split("#")[0].strip()

            if hostname and f"{hostname}#show ip interface brief" in cleaned_line:
                start_idx = i
                break  # Ngừng tìm kiếm sau khi tìm thấy lệnh

        if start_idx == -1:
            print("\033[31mKhông Tìm Thấy Lệnh 'show ip interface brief'.\033[0m")
            return

        unused_ports = []
        
        # Phân tích các dòng sau lệnh "show ip interface brief"
        for line in config_lines[start_idx + 1:]:
            if line.strip() == "":
                continue
            if "#" in line:
                break  # Kết thúc khi gặp lệnh khác
            if "down" in line.lower() and "administratively" not in line.lower():
                # Lấy tên interface từ dòng
                interface_name = line.split()[0]
                unused_ports.append(interface_name)

        # Hiển thị kết quả
        if unused_ports:
            print("\033[1mCác port không sử dụng nhưng chưa được shutdown:\033[0m")
            print(", ".join(unused_ports))  # Hiển thị theo danh sách ngắn gọn
            print(f"\033[1mTổng số cổng không tuân thủ: {len(unused_ports)}\033[0m")
        else:
            print("\033[32mTất cả các port không sử dụng đã được shutdown.\033[0m")
    except Exception as e:
        print(f"\033[31mLỗi khi in dữ liệu lệnh 'show ip interface brief': {e}\033[0m")


def process_logs_with_interface_brief(folder_path):


    # Duyệt qua tất cả file trong folder
    log_files = [file for file in os.listdir(folder_path) if file.endswith((".log", ".txt"))]
    for log_file in log_files:
        file_path = os.path.join(folder_path, log_file)
        print(f"\nProcessing File: {file_path}")

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                log_data = file.read()

            # Gọi hàm phân tích lệnh "show ip interface brief"
            extract_interface_brief(log_data)
        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\automation\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_logs_with_interface_brief(folder_path)
