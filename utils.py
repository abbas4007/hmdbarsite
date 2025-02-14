import requests

def send_sms(phone_number, message):
    url = "https://api.ghasedak.io/v2/sms/send/simple"
    headers = {
        "apikey": "YOUR_API_KEY",
        "Content-Type": "application/x-www-form-urlencoded"
    }
    data = {
        "message": message,
        "receptor": phone_number,
        "linenumber": "10008566"  # شماره خط اختصاصی شما
    }
    response = requests.post(url, headers=headers, data=data)
    return response.json()