import json
import os
import re

def load_json(file_path):
    """加载 JSON 文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def update_json(base_json, sites_data, lives_data):
    """更新 JSON 数据，将新内容追加到原内容前面"""
    if sites_data:
        # 将新内容追加到 `sites` 数据的前面
        if "sites" in base_json:
            base_json["sites"] = sites_data + base_json["sites"]
        else:
            base_json["sites"] = sites_data
    if lives_data:
        # 将新内容追加到 `lives` 数据的前面
        if "lives" in base_json:
            base_json["lives"] = lives_data + base_json["lives"]
        else:
            base_json["lives"] = lives_data
    return base_json

def save_json(file_path, data):
    """保存 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def check_updates(directory):
    """检查目录中的 pg. 开头的 ZIP 文件，并提取版本号"""
    latest_version = None
    latest_zip = None
    for filename in os.listdir(directory):
        if filename.startswith("pg.") and filename.endswith(".zip"):
            # 提取版本号，假设版本号是 pg.X.X.X.zip 格式
            match = re.search(r'pg\.([^\s]+)\.zip', filename)
            if match:
                version = match.group(1)
                if not latest_version or version > latest_version:
                    latest_version = version
                    latest_zip = os.path.join(directory, filename)
    return latest_zip, latest_version

def replace_placeholder(data, placeholder, version):
    """递归替换 JSON 中的占位符"""
    if isinstance(data, dict):
        for key in data:
            if isinstance(data[key], dict) or isinstance(data[key], list):
                replace_placeholder(data[key], placeholder, version)
            elif isinstance(data[key], str) and placeholder in data[key]:
                data[key] = data[key].replace(placeholder, version)
    elif isinstance(data, list):
        for item in data:
            if isinstance(item, dict) or isinstance(item, list):
                replace_placeholder(item, placeholder, version)
            elif isinstance(item, str) and placeholder in item:
                idx = data.index(item)
                data[idx] = item.replace(placeholder, version)

def main():
    # 设置文件路径
    base_path = os.path.dirname(os.path.abspath(__file__))  # 获取脚本所在目录
    pgdown_dir = os.path.join(base_path, "pgdown")  # 子目录 pgdown
    jsm_path = os.path.join(pgdown_dir, "jsm.json")
    sites_path = os.path.join(pgdown_dir, "sites.json")
    lives_path = os.path.join(pgdown_dir, "lives.json")
    output_path = os.path.join(pgdown_dir, "t1.json")  # 保存到 pgdown 子目录

    # 如果 pgdown 子目录不存在，则创建
    if not os.path.exists(pgdown_dir):
        os.makedirs(pgdown_dir)

    # 获取最新的 ZIP 文件和版本号
    zip_path, version = check_updates(base_path)
    if not zip_path:
        print("未找到以 pg. 开头的 ZIP 文件。")
        return

    try:
        # 加载基础文件 jsm.json
        base_json = load_json(jsm_path)
        
        # 加载 sites.json 文件
        sites_data = load_json(sites_path)
        print(f"加载 sites.json 数据完成。")  # 提示加载成功
        
        # 加载 lives.json 文件
        lives_data = load_json(lives_path)
        print(f"加载 lives.json 数据完成。")  # 提示加载成功
        
        # 更新 JSON 数据
        updated_json = update_json(base_json, sites_data["sites"], lives_data["lives"])
        
        # 替换占位符“版本号”为实际版本号
        replace_placeholder(updated_json, "版本号", version)
        
        # 保存为 t1.json
        save_json(output_path, updated_json)
        print(f"t1.json 文件已生成，保存路径: {output_path}。")
    except FileNotFoundError as e:
        print(f"错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")

if __name__ == "__main__":
    main()