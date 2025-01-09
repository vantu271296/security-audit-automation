#!/usr/bin/env python3

import os
import re

def is_mgmt_interface(interface_block: str) -> bool:
    """
    Kiểm tra liệu block cấu hình interface này có phải cổng mgmt không.
    Tiêu chí:
      1) Tên interface chứa 'mgmt' hoặc 'management'
         (vd: interface mgmt0, interface Management0)
         HOẶC
      2) Có description chứa 'mgmt', 'oob', 'management'
         HOẶC
      3) Có dòng 'vrf forwarding mgmt' hoặc 'vrf forwarding management'

    Thêm tùy chỉnh theo nhu cầu thực tế.
    """
    # Lấy dòng đầu tiên (interface <tên>) để xem tên
    first_line_match = re.search(r"(?im)^(interface\s+(\S+))", interface_block)
    if first_line_match:
        iface_name = first_line_match.group(2).lower()  # Tên interface
        # Tiêu chí 1: tên interface chứa mgmt, management
        if "mgmt" in iface_name or "management" in iface_name:
            return True
    
    # Tiêu chí 2: Tìm description có từ khóa mgmt, management, oob
    desc_match = re.search(r"(?im)^description\s+(.*)", interface_block)
    if desc_match:
        desc_text = desc_match.group(1).lower()
        if any(keyword in desc_text for keyword in ("mgmt", "management", "oob")):
            return True

    # Tiêu chí 3: ip vrf forwarding mgmt/management
    # (hoặc 'vrf forwarding mgmt' ... tùy Cisco IOS/IOS XE)
    vrf_match = re.search(r"(?im)^(ip\s+vrf\s+forwarding\s+(mgmt|management))", interface_block)
    if vrf_match:
        return True

    # Chưa thỏa mãn tiêu chí => return False
    return False


def check_5_3_1_mgmt_blocks(config_data: str):
    """
    Tách cấu hình thành từng block 'interface ... !'
    Tìm interface mgmt theo tiêu chí is_mgmt_interface()
    Trả về danh sách block mgmt + danh sách block không mgmt
    """
    # Regex tách block interface:
    #   - 1) Tìm 'interface <something>' + các dòng tiếp theo đến trước '!' hoặc 'interface ' kế tiếp
    #   - 2) Dùng re.DOTALL/multiline
    # Cách 1: Split theo regex "^(?=interface )" => cắt block. 
    # Cách 2: findall => group ...
    
    # Tạm dùng split:
    blocks = re.split(r"(?im)^interface\s", config_data)
    mgmt_blocks = []
    other_blocks = []

    for blk in blocks:
        blk = blk.strip()
        if not blk:
            continue
        # Gom lại 'interface ' vào đầu cho dễ đọc:
        blk_full = "interface " + blk

        if is_mgmt_interface(blk_full):
            mgmt_blocks.append(blk_full)
        else:
            other_blocks.append(blk_full)
    
    return mgmt_blocks, other_blocks


def check_5_3_1_in_all_files(folder_path: str):
    """
    Quét tất cả file .txt, .log.
    Với mỗi file, tách block interface, xác định interface mgmt.
    In ra bằng chứng: block interface mgmt.
    """
    items = os.listdir(folder_path)
    txt_log_files = []
    for item in items:
        if item.lower().endswith((".txt", ".log")):
            full_path = os.path.join(folder_path, item)
            if os.path.isfile(full_path):
                txt_log_files.append(full_path)

    if not txt_log_files:
        print(f"[Thông báo] Không có file .txt/.log nào trong thư mục: {folder_path}")
        return

    for file_path in txt_log_files:
        print(f"\n=== Kiểm tra 5.3.1 cho file: {file_path} ===")
        try:
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
        except Exception as e:
            print(f"[Lỗi] Không thể đọc {file_path}: {e}")
            continue

        mgmt_blocks, other_blocks = check_5_3_1_mgmt_blocks(content)
        if mgmt_blocks:
            print(f"[OK] Tìm thấy {len(mgmt_blocks)} interface mgmt. Bằng chứng:")
            for idx, block in enumerate(mgmt_blocks, start=1):
                # In block, cắt ngắn nếu quá dài
                lines = block.strip().splitlines()
                if len(lines) > 10:
                    # In gọn
                    print(f"--- MGMT BLOCK #{idx} (chỉ in 10 dòng) ---")
                    for line in lines[:10]:
                        print("   ", line)
                    print("   ... (cắt bớt)")
                else:
                    print(f"--- MGMT BLOCK #{idx} ---")
                    for line in lines:
                        print("   ", line)
        else:
            print(f"[CẢNH BÁO] Không tìm thấy interface mgmt nào.")


def main():
    folder_path = r"C:\Users\admin\Desktop\automation\Test"
    if not os.path.isdir(folder_path):
        print(f"[Lỗi] Thư mục không tồn tại: {folder_path}")
        return

    check_5_3_1_in_all_files(folder_path)

if __name__ == "__main__":
    main()
