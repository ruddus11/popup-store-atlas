# Popup Store Atlas

광역 팝업스토어 수집, PostGIS 적재, FastAPI 조회, Deck.gl 시각화를 한 저장소에서 다루는 프로젝트다.

## 구성

- `crawler/`: 시드 URL 기반 팝업스토어 크롤러
- `backend/`: CSV 적재기와 FastAPI API 서버
- `infra/`: PostgreSQL/PostGIS 초기화 스크립트
- `frontend/`: React + Deck.gl + Mapbox 프런트엔드
- `data/interim/`: 크롤링 결과 CSV, 거부 목록, 지오코딩 실패 목록

## 빠른 시작

1. `cp .env.example .env`
2. Python 의존성 설치: `make install-python`
3. DB 초기화: `make init-db`
4. 크롤링 실행: `make crawl`
5. CSV 적재: `make load-csv`
6. API 실행: `make run-api`
7. 프런트 의존성 설치: `make frontend-install`
8. 프런트 실행: `make frontend-dev`

## 환경 변수

- `DATABASE_URL`: 기본값 `postgresql:///popup_db`
- `KAKAO_REST_API_KEY`: Kakao Local REST API 키
- `VITE_API_BASE_URL`: 프런트가 호출할 FastAPI base URL
- `VITE_MAPBOX_ACCESS_TOKEN`: Mapbox 토큰

## 테스트

- Python: `make test`
- Frontend: `npm --prefix frontend test`

## Render 배포

백엔드는 Render Web Service, 데이터베이스는 Render Postgres 기준으로 바로 배포할 수 있게 `render.yaml` 을 포함한다.

1. 이 디렉터리를 GitHub 저장소로 푸시한다.
2. Render 대시보드에서 `Blueprint` 또는 `Web Service + Postgres` 생성 시 루트의 `render.yaml` 을 사용한다.
3. 생성되는 Web Service 이름은 `popup-store-api`, DB 이름은 `popup-store-db` 다.
4. 무료 플랜에서는 `pre-deploy command` 를 지원하지 않으므로, 서비스와 DB가 생성된 뒤 로컬에서 `python -m backend.init_db` 를 한 번 실행해 `postgis` 확장과 `popup_stores` 테이블을 초기화한다.
5. 배포 완료 후 백엔드 URL은 `https://...onrender.com` 형태가 된다.
6. 이 URL을 Vercel 환경변수 `VITE_API_BASE_URL` 로 넣고 프런트를 다시 배포한다.

Render용 참고 경로:

- 헬스 체크: `/health`
- 활성 팝업 API: `/api/popups/active`
