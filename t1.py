import json
import os
import zipfile
import time

def load_json(file_path):
    """加载 JSON 文件"""
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"文件未找到: {file_path}")
    with open(file_path, 'r', encoding='utf-8') as file:
        return json.load(file)

def update_json(base_json, sites_data, lives_data, version):
    """更新 JSON 数据，将新内容追加到原内容前面，并添加版本号"""
    # 添加版本号
    updated_json = {"version": version}
    # 更新 sites 数据
    if sites_data:
        updated_json["sites"] = sites_data + base_json.get("sites", [])
    # 更新 lives 数据
    if lives_data:
        updated_json["lives"] = lives_data + base_json.get("lives", [])
    # 合并其他字段
    for key, value in base_json.items():
        if key not in ["sites", "lives"]:
            updated_json[key] = value
    return updated_json

def save_json(file_path, data):
    """保存 JSON 文件"""
    with open(file_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)

def get_latest_zip_file(directory):
    """获取最新的以 pg. 开头的 ZIP 文件"""
    zip_files = [f for f in os.listdir(directory) if f.startswith("pg.") and f.endswith(".zip")]
    if not zip_files:
        return None, None
    # 按修改时间排序，获取最新的 ZIP 文件
    latest_file = max(zip_files, key=lambda f: os.path.getmtime(os.path.join(directory, f)))
    version = latest_file[len("pg."):-len(".zip")]  # 提取版本号
    return latest_file, version

def check_zip_updated(zip_file, last_modified_file="last_modified.txt"):
    """检查 ZIP 文件是否有更新"""
    if not os.path.exists(last_modified_file):
        return True  # 如果记录文件不存在，说明 ZIP 文件是新的
    with open(last_modified_file, 'r') as file:
        last_modified = float(file.read().strip())
    current_modified = os.path.getmtime(zip_file)
    return current_modified > last_modified

def update_last_modified(zip_file, last_modified_file="last_modified.txt"):
    """更新 ZIP 文件的最后修改时间记录"""
    current_modified = os.path.getmtime(zip_file)
    with open(last_modified_file, 'w') as file:
        file.write(str(current_modified))

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
    zip_file, version = get_latest_zip_file(base_path)
    if not zip_file:
        print("未找到以 pg. 开头的 ZIP 文件。")
        return

    # 检查 ZIP 文件是否有更新
    if not check_zip_updated(os.path.join(base_path, zip_file)):
        print(f"ZIP 文件 {zip_file} 未更新，跳过任务。")
        return

    try:
        # 加载基础文件 jsm.json
        base_json = load_json(jsm_path)
        
        # 加载 sites.json 文件
        sites_data = load_json(sites_path)["sites"]
        print(f"加载 sites.json 数据: {sites_data}")  # 打印加载的 sites 数据
        
        # 加载 lives.json 文件
        lives_data = load_json(lives_path)["lives"]
        print(f"加载 lives.json 数据: {lives_data}")  # 打印加载的 lives 数据
        
        # 更新 JSON 数据，并添加版本号
        updated_json = update_json(base_json, sites_data, lives_data, version)
        
        # 保存为 t1.json
        save_json(output_path, updated_json)
        print(f"t1.json 文件已生成，保存路径: {output_path}。")
        print("基础 JSON 数据（更新后）：")
        print(json.dumps(updated_json, ensure_ascii=False, indent=4))  # 打印最终数据

        # 更新 ZIP 文件的最后修改时间记录
        update_last_modified(os.path.join(base_path, zip_file))
        print(f"已更新 ZIP 文件 {zip_file} 的最后修改时间记录。")
    except FileNotFoundError as e:
        print(f"错误: {e}")
    except json.JSONDecodeError as e:
        print(f"JSON 解析错误: {e}")

if __name__ == "__main__":
    main()