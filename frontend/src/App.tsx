import type { PickingInfo } from "@deck.gl/core";
import { ColumnLayer } from "@deck.gl/layers";
import DeckGL from "@deck.gl/react";
import { useEffect, useState } from "react";
import { Map } from "react-map-gl/mapbox";

type PopupItem = {
  id: number;
  name: string;
  address: string;
  start_date: string;
  end_date: string;
  latitude: number;
  longitude: number;
  source_url: string;
  popularity: number;
};

type ApiResponse = {
  as_of_date: string;
  count: number;
  items: PopupItem[];
};

type TooltipState = {
  x: number;
  y: number;
  popup: PopupItem;
};

const INITIAL_VIEW_STATE = {
  longitude: 127.35,
  latitude: 36.85,
  zoom: 6.3,
  pitch: 50,
  bearing: 8
};

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";
const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ?? "";
const ALLOWED_SOURCE_DOMAINS = ["marieclairekorea.com", "tistory.com"];

function formatPeriod(popup: PopupItem) {
  return `${popup.start_date} - ${popup.end_date}`;
}

function buildTooltip(info: PickingInfo<PopupItem>): TooltipState | null {
  if (!info.object) {
    return null;
  }

  return {
    x: info.x ?? 0,
    y: info.y ?? 0,
    popup: info.object
  };
}

function isSafeSourceUrl(url: string) {
  try {
    const parsed = new URL(url);
    if (parsed.protocol !== "https:") {
      return false;
    }
    return ALLOWED_SOURCE_DOMAINS.some(
      (domain) => parsed.hostname === domain || parsed.hostname.endsWith(`.${domain}`)
    );
  } catch {
    return false;
  }
}

export default function App() {
  const [response, setResponse] = useState<ApiResponse>({
    as_of_date: "",
    count: 0,
    items: []
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [hovered, setHovered] = useState<TooltipState | null>(null);
  const [selected, setSelected] = useState<TooltipState | null>(null);

  useEffect(() => {
    const controller = new AbortController();

    const loadPopups = async () => {
      setLoading(true);
      setError("");

      try {
        const res = await fetch(`${API_BASE_URL}/api/popups/active`, {
          signal: controller.signal
        });
        if (!res.ok) {
          throw new Error(`API request failed with ${res.status}`);
        }
        const payload = (await res.json()) as ApiResponse;
        setResponse(payload);
      } catch (err) {
        if (controller.signal.aborted) {
          return;
        }
        setError(err instanceof Error ? err.message : "Unknown error");
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    };

    void loadPopups();
    return () => controller.abort();
  }, []);

  const layer = new ColumnLayer<PopupItem>({
    id: "popup-columns",
    data: response.items,
    pickable: true,
    extruded: true,
    radius: 7000,
    elevationScale: 32,
    diskResolution: 24,
    autoHighlight: true,
    getPosition: (item) => [item.longitude, item.latitude],
    getElevation: (item) => item.popularity,
    getFillColor: [11, 122, 114, 220],
    getLineColor: [253, 245, 230, 180],
    lineWidthMinPixels: 1,
    onHover: (info) => {
      if (!selected) {
        setHovered(buildTooltip(info));
      }
    },
    onClick: (info) => {
      setSelected(buildTooltip(info));
      if (!info.object) {
        setHovered(null);
      }
    }
  });

  const visibleTooltip = selected ?? hovered;
  const visibleSourceUrl =
    visibleTooltip && isSafeSourceUrl(visibleTooltip.popup.source_url)
      ? visibleTooltip.popup.source_url
      : null;

  return (
    <div className="page-shell">
      <div className="background-glow background-glow-left" />
      <div className="background-glow background-glow-right" />

      <header className="hero">
        <div>
          <p className="eyebrow">Popup Store Atlas</p>
          <h1>서울부터 충청권까지, 운영 중인 팝업을 입체적으로 본다.</h1>
          <p className="hero-copy">
            FastAPI가 내려주는 운영 중 팝업만 골라 Mapbox 위에 ColumnLayer로 올렸다.
            위치, 기간, 원문 링크를 한 화면에서 확인할 수 있다.
          </p>
        </div>

        <div className="hero-stats">
          <div className="stat-card">
            <span className="stat-label">As Of</span>
            <strong>{response.as_of_date || "-"}</strong>
          </div>
          <div className="stat-card">
            <span className="stat-label">Active Popups</span>
            <strong>{response.count}</strong>
          </div>
          <div className="stat-card stat-card-accent">
            <span className="stat-label">Elevation Rule</span>
            <strong>Popularity 100</strong>
          </div>
        </div>
      </header>

      <main className="dashboard">
        <section className="map-card">
          <div className="map-card-header">
            <div>
              <p className="section-kicker">3D Map</p>
              <h2>광역 팝업 지형도</h2>
            </div>
            {!MAPBOX_TOKEN ? (
              <span className="token-warning">Mapbox 토큰이 없어서 지도 타일은 숨김 처리됨</span>
            ) : null}
          </div>

          <div className="map-stage">
            {MAPBOX_TOKEN ? (
              <DeckGL
                controller
                initialViewState={INITIAL_VIEW_STATE}
                layers={[layer]}
                style={{ position: "absolute", inset: "0" }}
              >
                <Map
                  mapboxAccessToken={MAPBOX_TOKEN}
                  mapStyle="mapbox://styles/mapbox/light-v11"
                  reuseMaps
                />
              </DeckGL>
            ) : (
              <div className="map-fallback">
                <strong>Mapbox token required</strong>
                <p>
                  `VITE_MAPBOX_ACCESS_TOKEN` 을 넣으면 서울, 경기, 충청권 지도를
                  바로 렌더링한다.
                </p>
              </div>
            )}

            {visibleTooltip ? (
              <div
                className="tooltip-card"
                style={{ left: visibleTooltip.x + 16, top: visibleTooltip.y + 16 }}
              >
                <p className="tooltip-title">{visibleTooltip.popup.name}</p>
                <p>{visibleTooltip.popup.address}</p>
                <p>{formatPeriod(visibleTooltip.popup)}</p>
                {visibleSourceUrl ? (
                  <a href={visibleSourceUrl} target="_blank" rel="noopener noreferrer">
                    원문 보기
                  </a>
                ) : (
                  <p>검증된 원문 링크가 없어 표시하지 않는다.</p>
                )}
                {selected ? (
                  <button
                    className="tooltip-close"
                    type="button"
                    onClick={() => setSelected(null)}
                    aria-label="선택 해제"
                  >
                    닫기
                  </button>
                ) : null}
              </div>
            ) : null}
          </div>
        </section>

        <aside className="side-panel">
          <section className="panel-card">
            <p className="section-kicker">Status</p>
            <h2>데이터 상태</h2>
            {loading ? <p className="status-pill">데이터를 불러오는 중</p> : null}
            {error ? <p className="status-pill status-error">{error}</p> : null}
            {!loading && !error && response.count === 0 ? (
              <p className="status-pill status-empty">운영 중 팝업이 없다.</p>
            ) : null}
          </section>

          <section className="panel-card">
            <p className="section-kicker">Live List</p>
            <h2>운영 중 팝업</h2>
            <div className="popup-list">
              {response.items.map((popup) => (
                <button
                  key={popup.id}
                  type="button"
                  className="popup-list-item"
                  onClick={() =>
                    setSelected({
                      x: 28,
                      y: 28,
                      popup
                    })
                  }
                >
                  <span className="popup-list-name">{popup.name}</span>
                  <span className="popup-list-address">{popup.address}</span>
                  <span className="popup-list-period">{formatPeriod(popup)}</span>
                </button>
              ))}
            </div>
          </section>
        </aside>
      </main>
    </div>
  );
}
