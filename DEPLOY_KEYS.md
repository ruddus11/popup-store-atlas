# 배포/연결용 키 위치 메모

이 프로젝트에서 자주 찾는 값은 아래 4개다.

- `DATABASE_URL`
- `KAKAO_REST_API_KEY`
- `VITE_MAPBOX_ACCESS_TOKEN`
- `VITE_API_BASE_URL`

## 1. Render DB URL (`DATABASE_URL`)

로컬 터미널에서 DB 적재할 때는 **반드시 External Database URL** 을 쓴다.

경로:

1. Render Dashboard 접속
2. 프로젝트/Blueprint에서 `popup-store-db` 클릭
3. 오른쪽 위 `Connect` 클릭
4. `External Database URL` 복사

주의:

- 로컬 터미널에서 적재할 때는 `Internal Database URL` 말고 `External Database URL` 을 사용
- 값은 보통 `postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require` 형태

예시:

```bash
export DATABASE_URL="postgresql://USER:PASSWORD@HOST:PORT/DBNAME?sslmode=require"
```

## 2. Kakao REST API 키 (`KAKAO_REST_API_KEY`)

경로:

1. Kakao Developers 접속
2. 앱 선택
3. `[앱] > [플랫폼 키]`
4. `REST API 키` 값 복사

추가 확인:

- 카카오맵/로컬 API를 쓰려면 `[카카오맵] > [사용 설정] > [상태]` 가 `ON` 이어야 함
- 신규 앱은 이 설정이 없으면 지오코딩 호출 시 `OPEN_MAP_AND_LOCAL service` 에러가 날 수 있음

예시:

```bash
export KAKAO_REST_API_KEY="여기에_실제_REST_API_키"
```

## 3. Mapbox 토큰 (`VITE_MAPBOX_ACCESS_TOKEN`)

프런트에서 쓰는 값이라 **`pk.` 로 시작하는 public token** 을 사용한다.

경로:

1. Mapbox Console 접속
2. `Access tokens` 페이지 이동
3. `Default public token` 또는 새 public token 선택
4. `pk.` 로 시작하는 값 복사

권장:

- 배포용 토큰에는 URL restriction 추가
- 허용 도메인 예시:
  - `https://popup-store-atlas.vercel.app`
  - `http://localhost:5173`

## 4. Vercel 프런트 API 주소 (`VITE_API_BASE_URL`)

이 값은 키가 아니라 **백엔드 공개 주소**다.

현재 값:

```text
https://popup-store-api.onrender.com
```

확인 경로:

1. Render Dashboard
2. `popup-store-api` 클릭
3. 서비스 URL 확인

Vercel에서 확인/수정 경로:

1. Vercel Dashboard
2. 프로젝트 `popup-store-atlas`
3. `Settings`
4. `Environment Variables`
5. `VITE_API_BASE_URL` 확인 또는 수정

## 5. 지금 프로젝트에서 다시 적재할 때 쓰는 명령

```bash
cd /Users/gyeong-yeon/Downloads/project04
source .venv/bin/activate
export DATABASE_URL="Render의 External Database URL"
export KAKAO_REST_API_KEY="Kakao REST API 키"
python -m backend.load_csv --csv data/interim/popup_stores.csv
```

## 6. 값이 제대로 들어갔는지 빠르게 확인

```bash
echo "$DATABASE_URL"
echo ${KAKAO_REST_API_KEY:+set}
```

정상 예시:

- `echo "$DATABASE_URL"` -> `postgresql://...`
- `echo ${KAKAO_REST_API_KEY:+set}` -> `set`

비정상 예시:

- `Render External Database URL`
- 빈 문자열

## 7. 실수 방지 메모

- 안내 문구를 그대로 넣지 말고 **실제 값**을 복붙할 것
- `DATABASE_URL="Render External Database URL"` 처럼 쓰면 안 됨
- 값에 특수문자가 많으므로 `export KEY=\"...\"` 형태로 따옴표를 유지할 것
- 프런트에서 쓰는 Mapbox 토큰은 `pk.` 로 시작해야 함
- Kakao 지오코딩은 `REST API 키` 를 사용해야 함

## 참고 링크

- Render Postgres 연결: https://render.com/docs/postgresql-creating-connecting
- Kakao 앱/플랫폼 키: https://developers.kakao.com/docs/latest/ko/app-setting/app
- Kakao 지도 시작하기: https://developers.kakao.com/docs/latest/ko/kakaomap
- Mapbox access tokens: https://docs.mapbox.com/help/dive-deeper/access-tokens/
- Vercel environment variables: https://vercel.com/docs/environment-variables
