import requests
import re

usr_info = {
    "account": "",
    "password": "",
    "ak": "",  # 百度智能云OCR ak&sk
    "sk": ""
}

# 网址
url_map = {
    "bulletin": "https://gonggao.hpu.edu.cn/swfweb/hpugg.aspx",
    "login": "https://uia.hpu.edu.cn/cas/login?service=https%3A%2F%2Fwebvpn.hpu.edu.cn%2FCas%2Flogin.html#/",
    "login_2": "https://uia.hpu.edu.cn/cas/login",
    "API_host": f"https://aip.baidubce.com/oauth/2.0/token?grant_type=client_credentials&client_id={usr_info['ak']}&client_secret={usr_info['sk']}",
    "captcha": "https://uia.hpu.edu.cn/sso/apis/v2/open/captcha?type=ALPHABET"
}

# 请求头
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/102.0.0.0 "
                  "Safari/537.36 "
}


# api token获取
def access_api_token():
    response = requests.get(url_map['API_host'])
    return response.json()['access_token']


# 验证码识别
def img_ocr(img, token):
    request_url = "https://aip.baidubce.com/rest/2.0/ocr/v1/accurate_basic"
    params = {"image": img}
    access_token = token
    request_url = request_url + "?access_token=" + access_token
    headers_ocr = {'content-type': 'application/x-www-form-urlencoded'}
    response = requests.post(request_url, data=params, headers=headers_ocr)
    if response:
        return response.json()


# 登录Post表单
login_data = {
    "username": usr_info['account'],
    "password": usr_info['password'],
    "captcha": None,
    "token": None,
    "_eventId": "submit",
    "lt": None,
    "source": "cas",
    "execution": "e1s1"
}

# 创建session会话
session = requests.session()
resp = session.get(url=url_map['bulletin'], headers=headers)

if resp.url != url_map['bulletin']:  # 重新登录
    print("重新登录！")
    # 获取登录所需post的"lt"
    pattern = re.compile(r'<input class="for-form" type="hidden" name="lt" value="(?P<value>.*?)">', re.S)
    lt = pattern.findall(resp.text)
    login_data["lt"] = lt
    # 验证码以及验证码token获取
    req = session.get(url_map['captcha'], headers=headers)
    img = eval(req.content)['img']
    ocr_result = img_ocr(img, access_api_token())
    if 'words_result' in ocr_result:
        login_data['captcha'] = ocr_result['words_result'][0]['words']
        login_data['token'] = eval(req.content)['token']
    else:
        print("图像识别出现未知问题！")

session.post(url_map['login_2'], data=login_data, headers=headers)
response_access_suc = session.get(url_map['bulletin'])
print(response_access_suc.text)  # 为什么抓不到数据！！可恶！！
