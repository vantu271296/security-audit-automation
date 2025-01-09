import os
import re

def analyze_bgp_authentication(config_data):
    """
    Phân tích cấu hình xác thực của BGP giữa các peer.
    Args:
        config_data (str): Nội dung cấu hình.

    Returns:
        dict: Thông tin về trạng thái cấu hình và xác thực của BGP.
    """
    bgp_status = {
        "configured": False,
        "peers": [],
        "authenticated_peers": [],
        "non_authenticated_peers": []
    }

    # Regex kiểm tra cấu hình BGP
    bgp_config_pattern = r"^router bgp \d+"
    peer_pattern = r"neighbor (\S+)"
    auth_pattern = r"neighbor (\S+) password \S+"

    # Kiểm tra cấu hình BGP
    if re.search(bgp_config_pattern, config_data, re.MULTILINE | re.IGNORECASE):
        bgp_status["configured"] = True

        # Tìm tất cả các peer
        peers = re.findall(peer_pattern, config_data, re.MULTILINE | re.IGNORECASE)
        bgp_status["peers"].extend(peers)

        # Tìm các peer được cấu hình xác thực
        authenticated_peers = re.findall(auth_pattern, config_data, re.MULTILINE | re.IGNORECASE)
        bgp_status["authenticated_peers"].extend(authenticated_peers)

        # Xác định các peer không được cấu hình xác thực
        for peer in peers:
            if peer not in authenticated_peers:
                bgp_status["non_authenticated_peers"].append(peer)

    return bgp_status

def process_bgp_authentication_logs(folder_path):
    """
    Duyệt qua tất cả các file log trong thư mục và kiểm tra xác thực của BGP.
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
            bgp_status = analyze_bgp_authentication(config_data)

            # Hiển thị kết quả
            print("\033[1mKết quả kiểm tra cấu hình BGP:\033[0m")
            if bgp_status["configured"]:
                print("\033[32mBGP được cấu hình.\033[0m")
                if bgp_status["peers"]:
                    print(f"Tổng số peer: {len(bgp_status['peers'])}")
                    if bgp_status["authenticated_peers"]:
                        print("\033[32mPeer có xác thực:\033[0m")
                        for peer in bgp_status["authenticated_peers"]:
                            print(f"- {peer}")
                    if bgp_status["non_authenticated_peers"]:
                        print("\033[31mPeer không có xác thực:\033[0m")
                        for peer in bgp_status["non_authenticated_peers"]:
                            print(f"- {peer}")
                else:
                    print("\033[33mKhông phát hiện peer nào trong cấu hình BGP.\033[0m")
            else:
                print("\033[31mBGP không được cấu hình.\033[0m")

            print("-" * 50)

        except Exception as e:
            print(f"An error occurred while processing {file_path}: {e}")

if __name__ == "__main__":
    folder_path = r"D:\\automation\\Test"  # Thay bằng đường dẫn thư mục chứa file log của bạn
    process_bgp_authentication_logs(folder_path)
