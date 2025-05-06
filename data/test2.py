import requests
import pandas as pd

api_url = "https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/selectWlfareInfo.do"
headers = {
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0"
}

results = []
seen_ids = set()
page = 1

while True:
    payload = {
        "dmScr": {
            "curScrId": "tbu/app/twat/twata/twataa/TWAT52005M",
            "befScrId": ""
        },
        "dmSearchParam": {
            "page": str(page),
            "onlineYn": "",
            "searchTerm": "",
            "tabId": "1",
            "orderBy": "date",
            "bkjrLftmCycCd": "",
            "daesang": "",
            "endYn": "N",
            "favoriteKeyword": "Y",
            "gungu": "",
            "jjim": "",
            "period": "",
            "region": "",
            "sido": "",
            "subject": ""
        }
    }

    try:
        res = requests.post(api_url, headers=headers, json=payload)
    except requests.exceptions.RequestException as e:
        print(f"[오류] 페이지 {page} 요청 실패: {e}")
        break

    if res.status_code != 200:
        print(f"[오류] 페이지 {page} 응답 실패 (status code {res.status_code})")
        break

    data = res.json()

    items = []
    for key in ["dsServiceList0", "dsServiceList1", "dsServiceList2", "dsServiceList3"]:
        items.extend(data.get(key, []))

    if not items:
        print(f"{page}페이지 이후로는 데이터 없음. 종료.")
        break

    print(f"페이지 {page}: {len(items)}개 항목 처리 중...")

    for item in items:
        info_id = item.get("WLFARE_INFO_ID")
        return_str = item.get("RETURN_STR", "")
        rel_cd = item.get("WLFARE_GDNC_TRGT_KCD", "01")

        if "임신·출산" not in return_str:
            continue
        if info_id in seen_ids:
            continue
        seen_ids.add(info_id)

        # 상세 URL 결정 로직
        if rel_cd == "01":
            detail_path = "moveTWAT52011M.do"
        elif rel_cd == "02":
            detail_path = "moveTWAT52012M.do"
        elif rel_cd == "03":
            detail_path = "moveTWAT52015M.do"
        else:
            detail_path = "moveTWAT52011M.do"

        detail_url = f"https://www.bokjiro.go.kr/ssis-tbu/twataa/wlfareInfo/{detail_path}?wlfareInfoId={info_id}&wlfareInfoReldBztpCd={rel_cd}"

        results.append({
            "id": info_id,
            "title": item.get("WLFARE_INFO_NM"),
            "summary": item.get("WLFARE_INFO_OUTL_CN"),
            "agency": item.get("BIZ_CHR_INST_NM"),
            "contact": item.get("RPRS_CTADR"),
            "detail_url": detail_url
        })

    page += 1

# 저장
df = pd.DataFrame(results)
df.to_csv("bokjiro_임신출산.csv", index=False, encoding="utf-8-sig")
print("임신·출산 포함된 항목 완료. 저장된 수:", len(df))
