import requests

print("发送请求更新数据库...")

try:
    response = requests.post("http://localhost:5000/api/update")
    data = response.json()
    
    if data['code'] == 0:
        print(f"数据更新成功，已更新 {data['data']['updated_count']} 条问题数据")
        print("请刷新浏览器查看最新数据")
    else:
        print(f"更新失败: {data['msg']}")
except Exception as e:
    print(f"请求失败: {e}") 