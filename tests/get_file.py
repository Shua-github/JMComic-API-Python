import requests

def save_file(file_data: str, file_name: str):
    """将Base64数据解码并保存为文件"""
    import base64
    with open(file_name, "wb") as f:
        f.write(base64.b64decode(file_data))

def download_file(jm_id: int, file_type: str, file_pwd: str, no_cache: bool, return_method: str):
    """
    发送请求到FastAPI服务器并下载文件
    """
    url = "http://127.0.0.1:5000/get/file"
    params = {
        "jm_id": jm_id,
        "file_type": file_type,
        "file_pwd": file_pwd,
        "no_cache": str(no_cache).lower(),
        "return_method": return_method
    }

    try:
        response = requests.get(url, params=params)
        if response.status_code == 200:
            data = response.json()
            file_data = data['data'].get('file_base64')
            if file_data:
                file_name = f"{jm_id}.{file_type}"
                save_file(file_data, file_name)
                print(f"文件已保存: {file_name}")
            else:
                print("未获取到文件数据")
        else:
            print(f"请求失败: {response.status_code}")
    except Exception as e:
        print(f"发生异常: {e}")


if __name__ == "__main__":
    jm_id = 114514
    file_type = 'pdf'
    file_pwd = '123'
    no_cache = 'false'
    return_method = 'base64'
    
    download_file(jm_id, file_type, file_pwd, no_cache, return_method)