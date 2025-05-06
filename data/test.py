import requests
import re
import pandas as pd

from bs4 import BeautifulSoup as bs

headers = {
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "https://umppa.seoul.go.kr/hmpg/info/popt/poptListPage.do?bbs_no=7",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

base_url = "https://umppa.seoul.go.kr/hmpg/info/popt/poptListPgng.do"
data = {
    "miv_pageNo": 1,
    "miv_pageSize": None,
    "total_cnt": None,
    "LISTOP": None,
    "mode": "W",
    "sidx": "NTC_DT_YN DESC, REF_NO DESC, REF_STEP_NO",
    "sord": "ASC",
    "bbs_no": 7,
    "pst_no": None,
    "searchkey": "S",
    "searchtxt": None
}

board_page_response = requests.post(base_url, headers=headers, data=data)
borad_page_soup = bs(board_page_response.content, "html.parser")
print(borad_page_soup)

atags = borad_page_soup.select(".title a")
print(f"1페이지에서 {len(atags)}개 글 발견")

results = []
for atag in atags:
    title = atag.text
    onclick_attr = atag['onclick']
    match = re.search(r"poptDetail\('([^']+)'\)", onclick_attr)

    if match:
        extracted_id = match.group(1)
        print(extracted_id)
    else:
        print("값을 찾을 수 없습니다.")
        continue


    detail_url = "https://umppa.seoul.go.kr/hmpg/info/popt/poptDetail.do"


    # CSRFToken 포함해서 payload 보내기
    payload = {
        "miv_pageNo" : "",
        "miv_pageSize" : "",
        "total_cnt" : "",
        "LISTOP" : "",
        "mode" : "W",
        "sidx" : "NTC_DT_YN DESC, REF_NO DESC, REF_STEP_NO",
        "sord" : "ASC",
        "bbs_no" : 7,
        "searchkey" : "S",
        "searchtxt" : "",
        "_csrf" : "undefined",
        "pst_no": extracted_id
    }

    response = requests.post(detail_url, headers=headers, data=payload)

    if response.status_code == 200:
        try:
            content = bs(response.content, "html.parser").select_one(".content_box")
        except Exception:
            content = ""
    else:
        print(f"본문 가져오기 실패: {title}")
        content = ""

    results.append({
        "title": title,
        "content": content
    })

# 7. 결과 저장
df = pd.DataFrame(results)
df.to_csv("umppa_policies_selenium_detail.csv", index=False, encoding="utf-8-sig")

print("크롤링 완료!")