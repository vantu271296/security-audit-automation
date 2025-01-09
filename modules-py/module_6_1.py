# modules/module_6.py

import re
from pathlib import Path

# Định nghĩa đường dẫn tới thư mục log
LOG_DIR = Path("test/")  # Thay đổi thành đường dẫn thực tế tới thư mục log

def check_ntp(log_data):
    """
    6.1: Yêu cầu cấu hình NTP.
    Mô tả: Đồng bộ thời gian theo tối thiểu 01 máy chủ thời gian (NTP server).
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về cấu hình NTP và đánh giá tuân thủ.
    """
    ntp_servers = re.findall(r'^\s*ntp\s+server\s+([\d\.]+)', log_data, re.MULTILINE | re.IGNORECASE)
    configured = len(ntp_servers) >= 1
    return {
        'NTP Configuration': {
            'Configured': configured,
            'NTP_Servers': ntp_servers,
            'Evidence': f"Configured NTP servers: {', '.join(ntp_servers)}" if ntp_servers else "No NTP servers configured."
        },
        'Compliance': "Compliant - At least one NTP server is configured." if configured else "Non-Compliant - No NTP server is configured."
    }

def check_logging(log_data):
    """
    6.2: Yêu cầu cấu hình Log.
    Mô tả: Thiết bị phải được thiết lập bật chế độ ghi log và cấu hình lưu log tập trung.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về cấu hình Logging và đánh giá tuân thủ.
    """
    logging_enabled = False
    logging_hosts = []
    for line in log_data.splitlines():
        if re.match(r'^\s*logging\s+on\b', line, re.IGNORECASE):
            logging_enabled = True
        match = re.match(r'^\s*logging\s+host\s+([\d\.]+)', line, re.IGNORECASE)
        if match:
            logging_hosts.append(match.group(1))
    
    configured = logging_enabled and len(logging_hosts) >= 1
    evidence = []
    if logging_enabled:
        evidence.append("Logging is enabled.")
    else:
        evidence.append("Logging is not enabled.")
    if logging_hosts:
        evidence.append(f"Centralized logging hosts: {', '.join(logging_hosts)}")
    else:
        evidence.append("No centralized logging hosts configured.")
    
    return {
        'Logging Configuration': {
            'Configured': configured,
            'Logging_Enabled': logging_enabled,
            'Logging_Hosts': logging_hosts,
            'Evidence': "; ".join(evidence)
        },
        'Compliance': "Compliant - Logging is enabled and centralized logging is configured." if configured else "Non-Compliant - Logging is not enabled or centralized logging is not configured."
    }

def check_snmp_configured(log_data):
    """
    Kiểm tra xem SNMP có được cấu hình hay không.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        bool: True nếu SNMP được cấu hình, False nếu không.
    """
    snmp_configured = bool(re.search(r'^\s*snmp-server\b', log_data, re.MULTILINE | re.IGNORECASE))
    return snmp_configured

def check_snmp_v3(log_data):
    """
    6.3.1: Yêu cầu cấu hình SNMP phiên bản v3.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về cấu hình SNMP v3 và đánh giá tuân thủ.
    """
    # Tìm các nhóm SNMP v3
    snmp_v3_groups = re.findall(r'^\s*snmp-server\s+group\s+\S+\s+v3\b', log_data, re.MULTILINE | re.IGNORECASE)
    configured = len(snmp_v3_groups) >= 1
    return {
        'SNMP v3 Configuration': {
            'Configured': configured,
            'SNMP_v3_Groups': snmp_v3_groups,
            'Evidence': f"SNMP v3 groups: {', '.join(snmp_v3_groups)}" if snmp_v3_groups else "No SNMP v3 groups configured."
        },
        'Compliance': "Compliant - SNMP v3 is configured." if configured else "Non-Compliant - SNMP v3 is not configured."
    }

def check_snmp_read_only(log_data):
    """
    6.3.2: Yêu cầu cấu hình SNMP theo chế độ read-only.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về cấu hình SNMP read-only và đánh giá tuân thủ.
    """
    # Tìm các cộng đồng SNMP read-only
    snmp_ro = re.findall(r'^\s*snmp-server\s+community\s+\S+\s+RO\b', log_data, re.MULTILINE | re.IGNORECASE)
    configured = len(snmp_ro) >= 1
    return {
        'SNMP Read-Only Configuration': {
            'Configured': configured,
            'SNMP_RO': snmp_ro,
            'Evidence': f"SNMP Read-Only communities: {', '.join(snmp_ro)}" if snmp_ro else "No SNMP Read-Only communities configured."
        },
        'Compliance': "Compliant - SNMP read-only mode is configured." if configured else "Non-Compliant - SNMP read-only mode is not configured."
    }

def check_snmp_read_write(log_data):
    """
    Kiểm tra xem có cấu hình SNMP cộng đồng với quyền Read-Write (RW) hay không.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về cấu hình SNMP Read-Write và đánh giá tuân thủ.
    """
    # Tìm các cộng đồng SNMP với quyền RW
    snmp_rw = re.findall(r'^\s*snmp-server\s+community\s+\S+\s+RW\b', log_data, re.MULTILINE | re.IGNORECASE)
    configured = len(snmp_rw) == 0  # Không có cộng đồng RW thì compliant
    return {
        'SNMP Read-Write Configuration': {
            'Configured': configured,
            'SNMP_RW': snmp_rw,
            'Evidence': f"Found Read-Write SNMP communities: {', '.join(snmp_rw)}" if snmp_rw else "No Read-Write SNMP communities configured."
        },
        'Compliance': "Compliant - No Read-Write SNMP communities are configured." if configured else f"Non-Compliant - Read-Write SNMP communities are present: {', '.join(snmp_rw)}."
    }

def check_snmp_no_default_community(log_data):
    """
    6.3.3: Yêu cầu xóa bỏ community string mặc định.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về việc xóa bỏ community string mặc định và đánh giá tuân thủ.
    """
    # Kiểm tra sự hiện diện của các community string mặc định như 'public', 'private'
    default_communities = ['public', 'private']
    found_defaults = []
    for comm in default_communities:
        if re.search(rf'^\s*snmp-server\s+community\s+{re.escape(comm)}\b', log_data, re.MULTILINE | re.IGNORECASE):
            found_defaults.append(comm)
    configured = len(found_defaults) == 0
    return {
        'SNMP Default Community Removal': {
            'Configured': configured,
            'Found_Defaults': found_defaults,
            'Evidence': f"Found default communities: {', '.join(found_defaults)}" if found_defaults else "Default community strings have been removed."
        },
        'Compliance': "Compliant - Default community strings have been removed." if configured else f"Non-Compliant - Default community strings are still present: {', '.join(found_defaults)}."
    }

def check_snmp_access_restriction(log_data):
    """
    6.3.4: Yêu cầu chỉ cho phép truy cập SNMP từ máy chủ giám sát.
    
    Args:
        log_data (str): Nội dung của file log.
    
    Returns:
        dict: Thông tin về giới hạn truy cập SNMP và đánh giá tuân thủ.
    """
    # Tìm các máy chủ được phép truy cập SNMP
    snmp_hosts = re.findall(r'^\s*snmp-server\s+host\s+([\d\.]+)', log_data, re.MULTILINE | re.IGNORECASE)
    configured = len(snmp_hosts) >= 1
    return {
        'SNMP Access Restriction': {
            'Configured': configured,
            'SNMP_Hosts': snmp_hosts,
            'Evidence': f"SNMP access hosts: {', '.join(snmp_hosts)}" if snmp_hosts else "No SNMP access hosts configured."
        },
        'Compliance': "Compliant - SNMP access is restricted to specific hosts." if configured else "Non-Compliant - SNMP access is not restricted to specific hosts."
    }

def display_snmp_results(results, snmp_configured):
    """
    Hiển thị kết quả kiểm tra các yêu cầu SNMP, bao gồm cả Read-Write.
    
    Args:
        results (dict): Kết quả từ các kiểm tra SNMP.
        snmp_configured (bool): Thông tin liệu SNMP có được cấu hình hay không.
    """
    print("=== Cấu Hình SNMP ===")
    
    if snmp_configured:
        # 6.3.1 SNMP v3
        snmp_v3_info = results.get('SNMP v3 Configuration', {})
        if snmp_v3_info.get('Configured'):
            print("- SNMP v3 được cấu hình.")
            print(f"  Bằng chứng: {snmp_v3_info.get('Evidence')}")
        else:
            print("- SNMP v3 không được cấu hình.")
            print(f"  Bằng chứng: {snmp_v3_info.get('Evidence')}")
        print(f"  Tuân Thủ SNMP v3: {snmp_v3_info.get('Compliance')}\n")
        
        # 6.3.2 SNMP Read-Only
        snmp_ro_info = results.get('SNMP Read-Only Configuration', {})
        if snmp_ro_info.get('Configured'):
            print("- SNMP được cấu hình ở chế độ read-only.")
            print(f"  Bằng chứng: {snmp_ro_info.get('Evidence')}")
        else:
            print("- SNMP không được cấu hình ở chế độ read-only.")
            print(f"  Bằng chứng: {snmp_ro_info.get('Evidence')}")
        print(f"  Tuân Thủ SNMP Read-Only: {snmp_ro_info.get('Compliance')}\n")
        
        # 6.3.3 SNMP Default Community Removal
        snmp_default_info = results.get('SNMP Default Community Removal', {})
        if snmp_default_info.get('Configured'):
            print("- Xóa bỏ community string mặc định.")
            print(f"  Bằng chứng: {snmp_default_info.get('Evidence')}")
        else:
            print("- Không xóa bỏ community string mặc định.")
            print(f"  Bằng chứng: {snmp_default_info.get('Evidence')}")
        print(f"  Tuân Thủ SNMP Default Community Removal: {snmp_default_info.get('Compliance')}\n")
        
        # 6.3.4 SNMP Access Restriction
        snmp_access_info = results.get('SNMP Access Restriction', {})
        if snmp_access_info.get('Configured'):
            print("- SNMP được giới hạn truy cập từ các máy chủ cụ thể.")
            print(f"  Bằng chứng: {snmp_access_info.get('Evidence')}")
        else:
            print("- SNMP không được giới hạn truy cập từ các máy chủ cụ thể.")
            print(f"  Bằng chứng: {snmp_access_info.get('Evidence')}")
        print(f"  Tuân Thủ SNMP Access Restriction: {snmp_access_info.get('Compliance')}\n")
        
        # 6.3.5 SNMP Read-Write
        snmp_rw_info = results.get('SNMP Read-Write Configuration', {})
        if snmp_rw_info.get('Configured'):
            print("- Không có cộng đồng SNMP Read-Write nào được cấu hình.")
            print(f"  Bằng chứng: {snmp_rw_info.get('Evidence')}")
        else:
            print("- Có cộng đồng SNMP Read-Write được cấu hình.")
            print(f"  Bằng chứng: {snmp_rw_info.get('Evidence')}")
        print(f"  Tuân Thủ SNMP Read-Write: {snmp_rw_info.get('Compliance')}\n")
    else:
        print("- SNMP không được sử dụng (không có cấu hình SNMP nào).")
        print("- Tuân Thủ SNMP: Non-Compliant - SNMP không được sử dụng.\n")
    
    print("-" * 50)

def display_results(results, log_file, snmp_configured):
    """
    Hiển thị kết quả kiểm tra các yêu cầu 6.1, 6.2, và 6.3.
    
    Args:
        results (dict): Kết quả từ các kiểm tra.
        log_file (Path): Đường dẫn tới file log.
        snmp_configured (bool): Thông tin liệu SNMP có được cấu hình hay không.
    """
    print(f"--- Kết Quả từ '{log_file.name}' ---\n")
    
    print("=== Cấu Hình NTP ===")
    ntp_info = results.get('NTP Configuration', {})
    if ntp_info.get('Configured'):
        print("- NTP được cấu hình.")
        print(f"  Bằng chứng: {ntp_info.get('Evidence')}")
    else:
        print("- NTP không được cấu hình.")
        print(f"  Bằng chứng: {ntp_info.get('Evidence')}")
    print(f"- Tuân Thủ NTP: {ntp_info.get('Compliance')}\n")
    
    print("=== Cấu Hình Logging ===")
    logging_info = results.get('Logging Configuration', {})
    if logging_info.get('Configured'):
        print("- Logging được bật và lưu trữ tập trung.")
        print(f"  Bằng chứng: {logging_info.get('Evidence')}")
    else:
        print("- Logging không được bật hoặc không lưu trữ tập trung.")
        print(f"  Bằng chứng: {logging_info.get('Evidence')}")
    print(f"- Tuân Thủ Logging: {logging_info.get('Compliance')}\n")
    
    # Kiểm tra SNMP
    display_snmp_results(results, snmp_configured)

def main():
    """
    Hàm chính để chạy các kiểm tra 6.1, 6.2, và 6.3 trên tất cả các file log trong thư mục LOG_DIR.
    """
    if not LOG_DIR.is_dir():
        print(f"Lỗi: Không tìm thấy thư mục log tại '{LOG_DIR}'.")
        return
    
    # Lấy tất cả các file log trong LOG_DIR (giả sử file log có đuôi .log)
    log_files = list(LOG_DIR.glob("*.log"))
    if not log_files:
        print(f"Lỗi: Không có file log nào trong thư mục '{LOG_DIR}'.")
        return
    
    for log_file in log_files:
        print(f"\n--- Kiểm Tra File Log: '{log_file.name}' ---")
        try:
            with log_file.open("r", encoding="utf-8") as f:
                log_data = f.read()
        except IOError as e:
            print(f"Lỗi IO khi đọc file '{log_file}': {e}")
            continue
       
        # Thực hiện các kiểm tra từ Module 6
        ntp_result = check_ntp(log_data)
        logging_result = check_logging(log_data)
        
        # Kiểm tra liệu SNMP có được cấu hình hay không
        snmp_configured = check_snmp_configured(log_data)
        
        # Thực hiện kiểm tra SNMP nếu SNMP được cấu hình
        if snmp_configured:
            snmp_v3_result = check_snmp_v3(log_data)
            snmp_ro_result = check_snmp_read_only(log_data)
            snmp_default_result = check_snmp_no_default_community(log_data)
            snmp_access_result = check_snmp_access_restriction(log_data)
            snmp_rw_result = check_snmp_read_write(log_data)
            
            # Tập hợp kết quả SNMP
            snmp_results = {}
            snmp_results.update(snmp_v3_result)
            snmp_results.update(snmp_ro_result)
            snmp_results.update(snmp_default_result)
            snmp_results.update(snmp_access_result)
            snmp_results.update(snmp_rw_result)
        else:
            snmp_results = {}
        
        # Tập hợp kết quả từ Module 6
        results = {}
        results.update(ntp_result)
        results.update(logging_result)
        results.update(snmp_results)
        
        # Hiển thị kết quả tổng hợp
        display_results(results, log_file, snmp_configured)

if __name__ == "__main__":
    main()
