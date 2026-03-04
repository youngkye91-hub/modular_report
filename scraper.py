import json
import datetime
import os
import sys
import re

# [TODO] 외부 라이브러리 (requests, BeautifulSoup 등) 임포트 필요

def scrape_g2b_data(keyword, target_clients=None):
    """
    나라장터(G2B) 입찰 공고 검색 (OpenAPI 활용 권장)
    참고: 조달청 OpenAPI(data.go.kr)를 통해 키워드 기반 최근 공고 정보를 JSON/XML로 수집
    """
    client_info = f" (대상 기관: {', '.join(target_clients)})" if target_clients else ""
    print(f"[*] 나라장터 검색 중... 키워드: {keyword}{client_info}")
    # dummy_results = []
    # return dummy_results
    return []

def scrape_d2b_data(keyword):
    """
    국방전자조달(D2B) 입찰 공고 검색 로직
    """
    print(f"[*] 국방전자조달 검색 중... 키워드: {keyword}")
    return []

def generate_top3(all_tenders):
    """
    수집된 공고들을 기반으로 모듈러 적용 확률이 높은 TOP3 추출 알고리즘 (간단히 태그 매칭)
    """
    return []

def filter_recent_data(data_list, months=6):
    """
    공고일(date) 값을 파싱하여 최근 N개월 이내(혹은 미래)인 데이터만 남깁니다.
    파싱할 수 없는 날짜 문자열은 안전을 위해 제외하지 않고 유지합니다.
    """
    now = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    # n개월 전 대략적 계산 (30일 * months)
    limit_date = now - datetime.timedelta(days=30*months)
    limit_date = limit_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    
    filtered_list = []
    for item in data_list:
        date_str = item.get("date", "")
        if not date_str:
            filtered_list.append(item)
            continue
        
        # 'YYYY.MM.DD' 혹은 'YYYY.MM' 등에서 연도와 월 추출
        match = re.search(r'(\d{4})[./-](\d{1,2})', str(date_str))
        if match:
            year, month = int(match.group(1)), int(match.group(2))
            try:
                target_date = datetime.datetime(year, month, 1)
                if target_date >= limit_date:
                    filtered_list.append(item)
            except ValueError:
                # 월 값이 잘못된 경우 등 파싱 에러 시 기본 유지
                filtered_list.append(item)
        else:
            # 날짜 형식을 찾지 못하면(예: "연말 예정" 등) 유지
            filtered_list.append(item)
            
    return filtered_list

def main():
    # 1. 한국 시간(KST) 구하기
    now_kst = datetime.datetime.utcnow() + datetime.timedelta(hours=9)
    updated_time_str = now_kst.strftime("%Y년 %m월 %d일 %H:%M")
    
    print(f"업데이트 시작 시간: {updated_time_str}")

    base_dir = os.path.dirname(os.path.abspath(__file__))
    json_path = os.path.join(base_dir, 'data.json')

    # 2. 기존 data.json 데이터 열기
    existing_data = {}
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
    else:
        existing_data = {
            "last_updated": "",
            "bids": [],
            "pre_specs": [],
            "plans": [],
            "top3": []
        }

    # 3. 새로운 데이터 크롤링 시도 (여기에 반복문 + 수집 코드 작성)
    keywords = ["모듈러", "생활관", "기숙사", "병영생활관"]
    target_clients = ["SH", "서울주택도시공사", "IH", "인천도시공사", "LH", "한국토지주택공사", "GH", "경기주택도시공사"]
    
    # for keyword in keywords:
    #     new_g2b = scrape_g2b_data(keyword, target_clients)
    #     existing_data["bids"].extend(new_g2b)

    # 참고: 실제 구현 시 발주처(client) 필드를 조회하여 target_clients에 포함되는지 확인하는 필터링 로직 혹은
    # 각 기관의 독자 입찰시스템(예: LH 전자조달)을 별도로 크롤링하는 로직을 추가해야 합니다.

    # 4. 데이터 갱신 (현재는 아키텍처 데모 목적이므로 시간만 업데이트함)
    existing_data["last_updated"] = updated_time_str

    # 중복 제거 및 6개월 지난 데이터 필터링 로직 추가
    existing_data["bids"] = filter_recent_data(existing_data.get("bids", []))
    existing_data["pre_specs"] = filter_recent_data(existing_data.get("pre_specs", []))
    existing_data["plans"] = filter_recent_data(existing_data.get("plans", []))

    # 5. data.json 파일 덮어쓰기 저장
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(existing_data, f, ensure_ascii=False, indent=2)

    print(f"data.json 업데이트 완료! (최근 기준일: {updated_time_str})")

if __name__ == "__main__":
    main()
