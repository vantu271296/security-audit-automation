import os
import re

def analyze_route_filters(config_data):
    results = {
        "interfaces": [],
        "routing_protocols": set(),
        "filter_status": {
            "compliant": [],
            "non_compliant": []
        },
        "has_routing": False
    }
    
    # Tìm các giao thức định tuyến đang chạy
    routing_patterns = {
        "OSPF": r"router ospf \d+",
        "EIGRP": r"router eigrp \d+",
        "RIP": r"router rip",
        "BGP": r"router bgp \d+"
    }
    
    for protocol, pattern in routing_patterns.items():
        if re.search(pattern, config_data, re.IGNORECASE):
            results["routing_protocols"].add(protocol)
            results["has_routing"] = True
    
    # Nếu không có giao thức định tuyến, trả về kết quả sớm
    if not results["has_routing"]:
        return results
        
    # Tìm các interface end-user
    interface_pattern = r"interface (.+?)\n(?:.*?\n)*?(?=!)"
    for match in re.finditer(interface_pattern, config_data, re.MULTILINE):
        interface_config = match.group(0)
        interface_name = match.group(1)
        
        if (re.search(r"switchport mode access", interface_config, re.IGNORECASE) or 
            re.search(r"description.*?(client|end-user|customer)", interface_config, re.IGNORECASE)):
            results["interfaces"].append(interface_name)
    
    # Kiểm tra passive-interface và distribute-list
    for interface in results["interfaces"]:
        is_secure = False
        
        if any(re.search(rf"passive-interface {interface}", config_data, re.IGNORECASE) for _ in results["routing_protocols"]):
            results["filter_status"]["compliant"].append({
                "interface": interface,
                "method": "passive-interface",
                "details": "Interface được cấu hình passive"
            })
            is_secure = True
            
        if any(re.search(rf"distribute-list.*in.*{interface}", config_data, re.IGNORECASE) for _ in results["routing_protocols"]):
            results["filter_status"]["compliant"].append({
                "interface": interface,
                "method": "distribute-list",
                "details": "Có áp dụng distribute-list để lọc"
            })
            is_secure = True
            
        if any(re.search(rf"route-map.*in.*{interface}", config_data, re.IGNORECASE) for _ in results["routing_protocols"]):
            results["filter_status"]["compliant"].append({
                "interface": interface,
                "method": "route-map",
                "details": "Có áp dụng route-map để lọc"
            })
            is_secure = True
        
        if not is_secure:
            results["filter_status"]["non_compliant"].append({
                "interface": interface,
                "details": "Không có cấu hình lọc route"
            })
    
    return results

def process_config_files(folder_path):
    log_files = [f for f in os.listdir(folder_path) if f.endswith('.log')]
    
    for file_name in log_files:
        file_path = os.path.join(folder_path, file_name)
        print(f"\nĐang phân tích file: {file_path}")
        
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                config_data = file.read()
            
            results = analyze_route_filters(config_data)
            
            if not results["has_routing"]:
                print("\033[33mThiết bị không chạy giao thức định tuyến động\033[0m")
                print("-" * 50)
                continue
                
            print("\033[1mKết quả kiểm tra lọc route trên port end-user:\033[0m")
            print(f"\nThiết bị: {file_name}")
                
            print("\nGiao thức định tuyến đang chạy:")
            for protocol in results["routing_protocols"]:
                print(f"  - {protocol}")
            
            if results["interfaces"]:
                print("\nPort end-user được phát hiện:")
                for interface in results["interfaces"]:
                    print(f"  - {interface}")
                
                print("\n\033[32mPort đã cấu hình lọc route:\033[0m")
                for entry in results["filter_status"]["compliant"]:
                    print(f"  - {entry['interface']}: {entry['details']} ({entry['method']})")
                
                print("\n\033[31mPort chưa cấu hình lọc route:\033[0m")
                for entry in results["filter_status"]["non_compliant"]:
                    print(f"  - {entry['interface']}: {entry['details']}")
            else:
                print("\n\033[33mKhông phát hiện port end-user\033[0m")
            
            print("-" * 50)
            
        except Exception as e:
            print(f"Lỗi khi xử lý {file_path}: {e}")

# Chạy phân tích
folder_path = r"D:\automation\Test"
process_config_files(folder_path)