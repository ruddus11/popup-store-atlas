import type { PickingInfo } from "@deck.gl/core";
import { ColumnLayer, TextLayer } from "@deck.gl/layers";
import DeckGL from "@deck.gl/react";
import { Filter, MapPin, Search } from "lucide-react";
import { useEffect, useState } from "react";
import { Map } from "react-map-gl/mapbox";

import { EmptyState } from "../components/EmptyState";
import { PopupDetailModal } from "../components/PopupDetailModal";
import { StatusBadge } from "../components/StatusBadge";
import { PopupItem, PopupStatus, usePopupData } from "../popup-data";

const MAPBOX_TOKEN = import.meta.env.VITE_MAPBOX_ACCESS_TOKEN ?? "";

const INITIAL_VIEW_STATE = {
  longitude: 127.35,
  latitude: 36.85,
  zoom: 6.2,
  pitch: 8,
  bearing: 0
};

const MAP_CONTROLLER = {
  dragRotate: false,
  touchRotate: false,
  keyboard: true
};

type TooltipState = {
  x: number;
  y: number;
  group: PopupVenueGroup;
};

type PopupVenueGroup = {
  id: string;
  name: string;
  lat: number;
  lng: number;
  count: number;
  status: PopupStatus;
  popups: PopupItem[];
};

const STATUS_OPTIONS: Array<{ value: PopupStatus; label: string }> = [
  { value: "active", label: "운영 중" },
  { value: "ending-soon", label: "종료 임박" },
  { value: "ended", label: "종료됨" },
  { value: "upcoming", label: "오픈 예정" }
];

function buildTooltip(info: PickingInfo<PopupVenueGroup>): TooltipState | null {
  if (!info.object) {
    return null;
  }
  return { x: info.x ?? 0, y: info.y ?? 0, group: info.object };
}

function columnColor(status: PopupStatus): [number, number, number, number] {
  if (status === "active") return [15, 118, 110, 220];
  if (status === "ending-soon") return [181, 121, 61, 220];
  if (status === "upcoming") return [41, 58, 86, 220];
  return [125, 118, 108, 150];
}

function statusElevation(status: PopupStatus, popularity: number) {
  if (status === "active") return popularity;
  if (status === "ending-soon") return popularity * 0.8;
  if (status === "upcoming") return popularity * 0.65;
  return popularity * 0.45;
}

function formatDateRange(popup: PopupItem) {
  return `${popup.startDate} - ${popup.endDate}`;
}

function groupStatus(popups: PopupItem[]): PopupStatus {
  if (popups.some((popup) => popup.status === "active")) return "active";
  if (popups.some((popup) => popup.status === "ending-soon")) return "ending-soon";
  if (popups.some((popup) => popup.status === "upcoming")) return "upcoming";
  return "ended";
}

function buildVenueGroups(popups: PopupItem[]): PopupVenueGroup[] {
  const groups = new globalThis.Map<string, PopupVenueGroup>();

  for (const popup of popups) {
    const key = `${popup.lat.toFixed(6)}:${popup.lng.toFixed(6)}`;
    const existing = groups.get(key);
    if (existing) {
      existing.popups.push(popup);
      existing.count += 1;
      existing.status = groupStatus(existing.popups);
      continue;
    }

    groups.set(key, {
      id: key,
      name: popup.subRegion,
      lat: popup.lat,
      lng: popup.lng,
      count: 1,
      status: popup.status,
      popups: [popup]
    });
  }

  return [...groups.values()].map((group) => ({
    ...group,
    popups: [...group.popups].sort((left, right) => left.endDate.localeCompare(right.endDate))
  }));
}

export function MapExplorerPage() {
  const { catalog, error, isFallback, loading } = usePopupData();
  const [selectedPopupId, setSelectedPopupId] = useState<number | null>(null);
  const [modalPopupId, setModalPopupId] = useState<number | null>(null);
  const [hovered, setHovered] = useState<TooltipState | null>(null);
  const [search, setSearch] = useState("");
  const [regions, setRegions] = useState<string[]>([]);
  const [statuses, setStatuses] = useState<PopupStatus[]>([]);

  const filteredPopups = catalog.filter((popup) => {
    const matchesRegion = regions.length === 0 || regions.includes(popup.region);
    const matchesStatus = statuses.length === 0 || statuses.includes(popup.status);
    const keyword = search.trim().toLowerCase();
    const matchesSearch =
      keyword.length === 0 ||
      popup.name.toLowerCase().includes(keyword) ||
      popup.address.toLowerCase().includes(keyword);

    return matchesRegion && matchesStatus && matchesSearch;
  });
  const venueGroups = buildVenueGroups(filteredPopups);

  const selectedPopup = catalog.find((popup) => popup.id === selectedPopupId) ?? null;
  const modalPopup = catalog.find((popup) => popup.id === modalPopupId) ?? null;
  const selectedGroup =
    selectedPopup == null
      ? null
      : venueGroups.find(
          (group) => group.popups.some((popup: PopupItem) => popup.id === selectedPopup.id)
        ) ?? null;
  const sideListPopups: PopupItem[] = selectedGroup?.popups ?? filteredPopups;

  useEffect(() => {
    if (filteredPopups.length === 0) {
      setSelectedPopupId(null);
      setModalPopupId(null);
      return;
    }

    if (!selectedPopupId || !filteredPopups.some((popup) => popup.id === selectedPopupId)) {
      setSelectedPopupId(filteredPopups[0].id);
    }
  }, [filteredPopups, selectedPopupId]);

  useEffect(() => {
    if (modalPopupId && !filteredPopups.some((popup) => popup.id === modalPopupId)) {
      setModalPopupId(null);
    }
  }, [filteredPopups, modalPopupId]);

  const layer = new ColumnLayer<PopupVenueGroup>({
    id: "popup-columns-explorer",
    data: venueGroups,
    pickable: true,
    extruded: true,
    radius: 5200,
    elevationScale: 12,
    diskResolution: 18,
    autoHighlight: true,
    getPosition: (group) => [group.lng, group.lat],
    getElevation: (group) => Math.max(100, statusElevation(group.status, 42 + group.count * 18)),
    getFillColor: (group) => columnColor(group.status),
    getLineColor: [248, 243, 238, 190],
    onHover: (info) => setHovered(buildTooltip(info)),
    onClick: (info) => {
      const tooltip = buildTooltip(info);
      setSelectedPopupId(tooltip?.group.popups[0]?.id ?? null);
    }
  });

  const labelLayer = new TextLayer<PopupVenueGroup>({
    id: "popup-count-labels",
    data: venueGroups.filter((group) => group.count > 1),
    pickable: false,
    getPosition: (group) => [group.lng, group.lat],
    getText: (group) => String(group.count),
    getColor: [32, 40, 36, 255],
    getSize: 15,
    getTextAnchor: "middle",
    getAlignmentBaseline: "center",
    getPixelOffset: [0, -10],
    fontWeight: 800,
    billboard: true
  });

  return (
    <div className="page page-map">
      <header className="page-header compact">
        <div>
          <p className="section-kicker">Map Explorer</p>
          <h2>필터와 3D 지도로 팝업 탐색</h2>
          <p className="page-lead">Figma 시안의 탐색 화면 구조를 현재 Deck.gl 지도에 맞게 연결했다.</p>
        </div>
      </header>

      {error ? <section className="alert-card">{error}</section> : null}
      {isFallback && !error ? (
        <section className="alert-card">실시간 API가 늦어 저장된 카탈로그를 먼저 보여준다.</section>
      ) : null}

      <section className="explorer-layout">
        <aside className="filter-panel">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Filters</p>
              <h3>탐색 조건</h3>
            </div>
            <Filter />
          </div>

          <label className="filter-label">검색</label>
          <div className="search-field">
            <Search size={18} />
            <input
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              placeholder="팝업명 또는 주소"
            />
          </div>

          <label className="filter-label">지역</label>
          <div className="chip-group">
            {["서울", "경기", "충청"].map((region) => (
              <button
                key={region}
                type="button"
                className={`filter-chip${regions.includes(region) ? " filter-chip-active" : ""}`}
                onClick={() =>
                  setRegions((current) =>
                    current.includes(region)
                      ? current.filter((value) => value !== region)
                      : [...current, region]
                  )
                }
              >
                {region}
              </button>
            ))}
          </div>

          <label className="filter-label">상태</label>
          <div className="chip-group">
            {STATUS_OPTIONS.map((status) => (
              <button
                key={status.value}
                type="button"
                className={`filter-chip${statuses.includes(status.value) ? " filter-chip-active" : ""}`}
                onClick={() =>
                  setStatuses((current) =>
                    current.includes(status.value)
                      ? current.filter((value) => value !== status.value)
                      : [...current, status.value]
                  )
                }
              >
                {status.label}
              </button>
            ))}
          </div>

          <div className="filter-summary">
            <strong>{filteredPopups.length}</strong>
            <span>개의 팝업이 조건과 일치한다.</span>
          </div>
        </aside>

        <div className="map-board">
          <div className="map-stage explorer-map-stage">
            {MAPBOX_TOKEN ? (
              <DeckGL
                controller={MAP_CONTROLLER}
                initialViewState={INITIAL_VIEW_STATE}
                layers={[layer, labelLayer]}
                style={{ position: "absolute", inset: "0" }}
              >
                <Map mapboxAccessToken={MAPBOX_TOKEN} mapStyle="mapbox://styles/mapbox/light-v11" reuseMaps />
              </DeckGL>
            ) : (
              <div className="map-fallback">
                <strong>Mapbox token required</strong>
                <p>`VITE_MAPBOX_ACCESS_TOKEN` 설정 후 지도 타일이 보인다.</p>
              </div>
            )}

            {selectedPopup ? (
              <div className="map-focus-card">
                <div className="map-focus-head">
                  <p className="section-kicker">On Map</p>
                  <StatusBadge status={selectedPopup.status} />
                </div>
                <strong>{selectedPopup.name}</strong>
                <p>{selectedPopup.address}</p>
                <div className="map-focus-meta">
                  <span>
                    {selectedPopup.region} · {selectedPopup.subRegion} · {selectedPopup.category}
                  </span>
                  <span>{formatDateRange(selectedPopup)}</span>
                </div>
                {selectedGroup && selectedGroup.count > 1 ? (
                  <p className="map-focus-count">이 위치에 팝업 {selectedGroup.count}개가 겹쳐 있다.</p>
                ) : null}
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setModalPopupId(selectedPopup.id)}
                >
                  상세 보기
                </button>
              </div>
            ) : null}

            {hovered ? (
              <div
                className="hover-card"
                style={{ left: hovered.x + 18, top: hovered.y + 18 }}
              >
                <p className="section-kicker">{hovered.group.name}</p>
                <strong>
                  {hovered.group.count > 1
                    ? `이 위치에 팝업 ${hovered.group.count}개`
                    : hovered.group.popups[0]?.name}
                </strong>
                <div className="hover-card-meta">
                  <StatusBadge status={hovered.group.status} />
                  {hovered.group.count === 1 ? <span>{hovered.group.popups[0]?.endDate}</span> : null}
                </div>
              </div>
            ) : null}

            <div className="map-legend">
              <p className="section-kicker">Legend</p>
              <div className="legend-row">
                <span className="legend-dot legend-active" />
                <span>운영 중</span>
              </div>
              <div className="legend-row">
                <span className="legend-dot legend-ending" />
                <span>종료 임박</span>
              </div>
              <div className="legend-row">
                <span className="legend-dot legend-ended" />
                <span>종료됨</span>
              </div>
            </div>
          </div>

          <aside className="map-side-card">
            <div className="panel-head">
              <div>
                <p className="section-kicker">Selected</p>
                <h3>선택 팝업 정보</h3>
              </div>
              <MapPin />
            </div>

            {loading ? <div className="loading-block">지도 카탈로그를 준비하는 중...</div> : null}

            {!loading && !selectedPopup ? (
              <EmptyState
                icon={MapPin}
                title="지도를 클릭해 상세를 보세요"
                description="컬럼이나 리스트를 선택하면 상세 정보와 외부 링크를 여기서 확인할 수 있다."
              />
            ) : null}

            {selectedPopup ? (
              <div className="selected-popup-stack">
                <div className="selected-popup-head">
                  <strong>{selectedPopup.name}</strong>
                  <StatusBadge status={selectedPopup.status} />
                </div>
                <p>{selectedPopup.address}</p>
                <div className="detail-grid compact-grid">
                  <div className="detail-block">
                    <p className="detail-label">기간</p>
                    <strong>
                      {selectedPopup.startDate} - {selectedPopup.endDate}
                    </strong>
                  </div>
                  <div className="detail-block">
                    <p className="detail-label">분류</p>
                    <strong>
                      {selectedPopup.region} · {selectedPopup.category}
                    </strong>
                  </div>
                </div>
                <button
                  type="button"
                  className="secondary-button"
                  onClick={() => setModalPopupId(selectedPopup.id)}
                >
                  상세 모달 열기
                </button>
              </div>
            ) : null}

            <div className="side-list">
              <p className="section-kicker">
                {selectedGroup && selectedGroup.count > 1 ? "Same Location" : "Matching Popups"}
              </p>
              {sideListPopups.slice(0, 8).map((popup: PopupItem) => (
                <button
                  key={popup.id}
                  type="button"
                  className="side-list-row"
                  onClick={() => setSelectedPopupId(popup.id)}
                >
                  <div>
                    <strong>{popup.name}</strong>
                    <p>{popup.subRegion}</p>
                  </div>
                  <StatusBadge status={popup.status} />
                </button>
              ))}

              {!loading && filteredPopups.length === 0 ? (
                <EmptyState
                  icon={Search}
                  title="조건에 맞는 팝업이 없다"
                  description="검색어 또는 상태 필터를 풀고 다시 탐색해보세요."
                />
              ) : null}
            </div>
          </aside>
        </div>
      </section>

      <PopupDetailModal popup={modalPopup} onClose={() => setModalPopupId(null)} />
    </div>
  );
}
