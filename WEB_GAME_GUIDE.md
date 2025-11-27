# 웹 게임 실행 가이드

## 빠른 시작

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

또는 Python 3를 사용하는 경우:
```bash
pip3 install -r requirements.txt
```

### 2. 서버 실행
```bash
python3 app.py
```

또는 실행 스크립트 사용:
```bash
./run_web.sh
```

### 3. 브라우저에서 접속
서버가 시작되면 브라우저에서 다음 주소로 접속하세요:
```
http://localhost:5000
```

## 게임 플레이 방법

1. **단어 선택**: 화면 중앙의 세 가지 섹션에서 각각 하나씩 선택
   - **Modifiers** (보라색): Huge, Fast, Vampiric, Burning, Heavy, Electric
   - **Cores** (빨간색): Fire, Water, Sword, Stone, Lightning
   - **Shapes** (파란색): Ball, Rain, Wall, Ray, Explosion

2. **주문 미리보기**: 세 단어를 모두 선택하면 주문 정보가 자동으로 표시됩니다
   - 데미지, 마나 비용, 타겟 타입, 상태 효과 등

3. **주문 시전**: "CAST SPELL" 버튼을 클릭하여 주문 시전

4. **전투**: 적의 HP를 0으로 만들면 승리!

## 기능

- ✅ 실시간 HP/Mana 바 업데이트
- ✅ 주문 미리보기 기능
- ✅ 전투 로그 자동 스크롤
- ✅ 상태 효과 표시
- ✅ 반응형 디자인 (모바일 지원)
- ✅ 다크 테마 UI

## 추천 주문 조합

- **Fast + Fire + Ball**: 빠른 화염 공격
- **Vampiric + Sword + Rain**: 전체 공격 + 생명력 흡수
- **Heavy + Water + Wall**: 방어력 증가
- **Electric + Water + Ball**: 전기 충격 효과

## 문제 해결

### 포트가 이미 사용 중인 경우
`app.py` 파일의 마지막 줄을 수정하여 다른 포트를 사용하세요:
```python
app.run(debug=True, host='0.0.0.0', port=5001)  # 포트 번호 변경
```

### 모듈을 찾을 수 없는 경우
```bash
pip3 install Flask flask-cors
```

### 브라우저에서 접속이 안 되는 경우
- 서버가 정상적으로 실행되었는지 확인
- 방화벽 설정 확인
- `localhost` 대신 `127.0.0.1` 사용 시도

## 배포 (선택사항)

### Heroku 배포
1. Heroku 계정 생성
2. Heroku CLI 설치
3. `Procfile` 생성:
   ```
   web: python app.py
   ```
4. 배포:
   ```bash
   heroku create
   git push heroku main
   ```

### 다른 클라우드 서비스
- AWS Elastic Beanstalk
- Google Cloud Run
- DigitalOcean App Platform
- Railway

모든 서비스에서 `requirements.txt`와 `app.py`를 사용할 수 있습니다.
