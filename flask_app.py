# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import re
from konlpy.tag import Okt
import xgboost as xgb
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# 입력한 URL에서 명사 추출
def extract_nouns_from_url(url):
    if not url.startswith('http'):
        url = 'http://' + url

    req = requests.get(url)
    soup = BeautifulSoup(req.text, 'html.parser')
    text = soup.get_text()

    # 정규표현식을 사용하여 특수문자 제거
    cleaned_text = re.sub('[^ㄱ-ㅣ가-힣0-9\n\{\}\[\]\/?.,;:|\)*~`!^\-_+<>@\#$%&\\\=\(\'\"\s]', ' ', text)

    # 단어 추출 (명사 추출을 위해 KoNLPy의 Okt 형태소 분석기 사용)
    okt = Okt()
    nouns = Okt().nouns(cleaned_text)
    return nouns


# 입력한 URL에서 명사 추출 후 불법사이트 여부 판단
def check_website_safety(url, feature_words, threshold):
    nouns = extract_nouns_from_url(url)
    count = sum(noun in feature_words for noun in nouns)

    if count >= threshold:
        return "이 사이트는 불법사이트로 의심됩니다."
    else:
        return "이 사이트는 안전한 사이트입니다."

# Feature 단어 로드
feature_words = ['리그', '분석', '커뮤니티', '비시', '폴리스', '사이트', '도메인', '사다리', '한자리', '욕구', '연습', '슬롯', '농구', '스코어', '체코', '보증금', '메라', '코드', '프리미어', '곰탕', '막대', '폴더', '아메리카', '놀이터', '티비', '쪽지', '필독', '슈퍼마리오', '라인업', '저희', '봇', '비너스', '기수', '로투스', '스리', '키노', '보타', '리저', '노리', '페셔널', '럭비', '이부', '퀄리티', '파워볼', '비지니스', '리뷰']

# 학습된 XGBoost 모델 로드
model = xgb.Booster()
model.load_model('xmodel.model')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/classify', methods=['POST'])
def classify():
    url = request.json['text']
    nouns = extract_nouns_from_url(url)
    result = check_website_safety(url, feature_words, 10)  # threshold 값은 임의로 설정
    
    return jsonify({'label': result, 'nouns': nouns})


if __name__ == '__main__':
    app.run(debug=True)
