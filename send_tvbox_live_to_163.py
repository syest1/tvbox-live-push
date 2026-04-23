import requests
import yagmail
import os
import tempfile
from datetime import datetime

EMAIL = os.environ.get("YOUR_EMAIL")
PASSWORD = os.environ.get("YOUR_PASSWORD")
TO_EMAIL = os.environ.get("TO_EMAIL")

def fetch_chinese_m3u():
    url = "https://raw.githubusercontent.com/iptv-org/iptv/master/streams/cn.m3u"
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    return response.text

def filter_good_sources(m3u_content, max_num=60):
    lines = m3u_content.splitlines()
    new_lines = [lines[0]]
    count = 0
    for i in range(1, len(lines)):
        if lines[i].startswith("#EXTINF"):
            if i + 1 < len(lines) and lines[i+1].startswith("http"):
                new_lines.append(lines[i])
                new_lines.append(lines[i+1])
                count += 1
        if count >= max_num:
            break
    return "\n".join(new_lines)

def send_mail(m3u_path):
    yag = yagmail.SMTP(user=EMAIL, password=PASSWORD, host='smtp.163.com')
    subject = "TVbox直播源（自动推送）"
    body = f"最新直播源，自动推送，时间：{datetime.now().strftime('%Y-%m-%d %H:%M')}"
    yag.send(
        to=TO_EMAIL,
        subject=subject,
        contents=body,
        attachments=[m3u_path],
    )

def main():
    m3u_raw = fetch_chinese_m3u()
    m3u_good = filter_good_sources(m3u_raw, max_num=60)
    with tempfile.NamedTemporaryFile(suffix=".m3u8", delete=False, mode='w', encoding='utf-8') as f:
        f.write(m3u_good)
        m3u_file = f.name
    send_mail(m3u_file)
    os.remove(m3u_file)

if __name__ == '__main__':
    main()
