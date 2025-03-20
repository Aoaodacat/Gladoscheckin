import requests
import json
import os

# -------------------------------------------------------------------------------------------
# github workflows
# -------------------------------------------------------------------------------------------
if __name__ == '__main__':
    # PushPlus 发送 Token（从环境变量读取）
    pushplus_token = os.environ.get("SENDKEY", "")

    # 推送内容
    title = ""
    success, fail, repeats = 0, 0, 0  # 成功账号数量 失败账号数量 重复签到账号数量
    context = ""

    # glados 账号 cookie
    cookies = os.environ.get("COOKIES", "").split("&")
    
    if cookies[0] != "":
        check_in_url = "https://glados.space/api/user/checkin"  # 签到地址
        status_url = "https://glados.space/api/user/status"  # 账户状态

        referer = 'https://glados.space/console/checkin'
        origin = "https://glados.space"
        useragent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 Safari/537.36"
        payload = {'token': 'glados.one'}
        
        for cookie in cookies:
            try:
                checkin = requests.post(
                    check_in_url,
                    headers={'cookie': cookie, 'referer': referer, 'origin': origin,
                             'user-agent': useragent, 'content-type': 'application/json;charset=UTF-8'},
                    data=json.dumps(payload)
                )
                state = requests.get(
                    status_url,
                    headers={'cookie': cookie, 'referer': referer, 'origin': origin, 'user-agent': useragent}
                )

                message_status = ""
                points = 0
                message_days = ""
                
                if checkin.status_code == 200:
                    result = checkin.json()
                    check_result = result.get('message', '')
                    points = result.get('points', 0)

                    result = state.json()
                    leftdays = int(float(result['data']['leftDays']))
                    email = result['data']['email']
                    
                    if "Checkin! Got" in check_result:
                        success += 1
                        message_status = f"签到成功，会员点数 +{points}"
                    elif "Checkin Repeats!" in check_result:
                        repeats += 1
                        message_status = "重复签到，明天再来"
                    else:
                        fail += 1
                        message_status = "签到失败，请检查..."
                    
                    message_days = f"{leftdays} 天" if leftdays is not None else "error"
                else:
                    email = ""
                    message_status = "签到请求失败, 请检查..."
                    message_days = "error"
                
                context += f"账号: {email}, P: {points}, 剩余: {message_days} | "
            
            except requests.RequestException as e:
                print(f"请求出错: {e}")
                fail += 1
        
        title = f'Glados 签到结果: 成功{success}, 失败{fail}, 重复{repeats}'
        print("Send Content:\n", context)
    else:
        title = f'# 未找到 cookies!'

    print("PushPlus Token:", pushplus_token)
    
    # 推送消息
    if pushplus_token:
        pushplus_url = "http://www.pushplus.plus/send"
        pushplus_data = {
            "token": pushplus_token,
            "title": title,
            "content": context,
            "template": "json"
        }
        
        try:
            response = requests.post(pushplus_url, json=pushplus_data)
            print("PushPlus 推送结果:", response.text)
        except requests.RequestException as e:
            print(f"PushPlus 推送失败: {e}")
    else:
        print("未设置 PushPlus Token，无法推送通知！")
