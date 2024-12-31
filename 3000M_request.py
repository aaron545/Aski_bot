import requests
import json
import subprocess
import time

def getResponse():
    # 用戶名和密碼
    username = "admin"
    password = r"$2a$11$W8/KspexdthEsSV3kVygMOd7PM/elg00VboxSkqsBaM5uw8pO4AFm"

    # 登入並獲取 AuthID
    login_url = "http://192.168.1.1/auth.fcgi"
    login_payload = {
        "AuthCmd": "Login",
        "UserName": username,
        "UserPW": password
    }

    try:
        # 發送 POST 請求
        response = requests.post(login_url, json=login_payload, headers={"Content-Type": "application/json"})
        response_data = response.json()
        status = response_data.get("Status", "").lower()

        if status == "ok":
            auth_id = response_data["Result"][0]["Login"]
            print("Login successful!")

            # 設置 Cookie
            cookies = {
                "expert": "true",
                "LANGUAGE": "1",
                "privilege": "0",
                "UID": auth_id
            }

            # 獲取 signal_info 配置
            get_signal_info_url = f"http://192.168.1.1/restful/lte/signal_info?AuthID={auth_id}"
            get_response = requests.get(get_signal_info_url, headers={"Content-Type": "application/json"}, cookies=cookies)

            if get_response.status_code == 200:
                signal_info = get_response.json()
                get_status = signal_info.get("Status", "").lower()

                if get_status == "ok":
                    print("Current signal_info Config:")
                    print(json.dumps(signal_info, indent=4))
                    return signal_info
                else:
                    print("Failed to get signal_info config.")
                    return "Fail"
            else:
                print(f"Failed to fetch signal_info. HTTP status code: {get_response.status_code}")
                return "Fail"

        else:
            print("Login failed!")
            return "Fail"

    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return "Fail"

if __name__ == "__main__":
    signal_info = getResponse()
    pci = signal_info.get('Result', {}).get('5g_pci', {})
    print(f"5G PCI: {pci}")
    while pci == "0" or pci == 'N/A':
        print("CPE is disconnect...")
        time.sleep(10)
        signal_info = getResponse() 
        pci = signal_info.get('Result', {}).get('5g_pci', {})
        print(f"5G PCI: {pci}")

    if pci != "0" and pci != 'N/A':
        print("start iperf")
        iperf_command = [
            "iperf3",
            "-c", "10.1.106.84",
            "-i", "5",
            "-P", "1",
            "-t", "30",
            "-p", "10602",
            "-R",
        ]
        try:
            for i in range(5):
                print("The "+str(i+1)+" time try :")
                result = subprocess.run(iperf_command, capture_output=True, text=True)
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                if result.stdout:
                    break

        except FileNotFoundError:
            print("iperf3 is not installed or not in PATH.")
        except Exception as e:
            print(f"Failed to execute iperf3: {e}")