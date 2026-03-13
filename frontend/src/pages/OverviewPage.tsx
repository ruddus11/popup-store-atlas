import { Calendar, Clock3, MapPinned, Store } from "lucide-react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Link } from "react-router-dom";

import { EmptyState } from "../components/EmptyState";
import { KPICard } from "../components/KPICard";
import { PopupDetailModal } from "../components/PopupDetailModal";
import { StatusBadge } from "../components/StatusBadge";
import { getMonthlyTrend, getRegionCounts, usePopupData } from "../popup-data";
import { useState } from "react";

export function OverviewPage() {
  const { asOfDate, catalog, endingSoon, error, livePopups, loading } = usePopupData();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const selectedPopup = catalog.find((popup) => popup.id === selectedId) ?? null;
  const regionData = getRegionCounts(catalog);
  const monthlyData = getMonthlyTrend(catalog);
  const topLivePopups = [...livePopups].sort((a, b) => a.daysRemaining - b.daysRemaining).slice(0, 8);

  return (
    <div className="page page-overview">
      <header className="page-header">
        <div>
          <p className="section-kicker">Overview</p>
          <h2>한눈에 보는 팝업 운영 보드</h2>
          <p className="page-lead">
            Figma 디자인 구조에 맞춰 핵심 지표, 지역 분포, 운영 추이를 첫 화면에 압축했다.
          </p>
        </div>
      </header>

      <section className="kpi-grid">
        <KPICard
          title="현재 운영 중"
          value={livePopups.length}
          icon={Store}
          subtitle="active + ending soon"
          accent
        />
        <KPICard title="종료 임박" value={endingSoon.length} icon={Clock3} subtitle="7일 이내 종료" />
        <KPICard
          title="커버 지역"
          value={new Set(catalog.map((popup) => popup.region)).size}
          icon={MapPinned}
          subtitle="서울 · 경기 · 충청"
        />
        <KPICard title="Catalog As Of" value={asOfDate || "-"} icon={Calendar} subtitle="DB 기준 날짜" />
      </section>

      {error ? <section className="alert-card">데이터를 불러오지 못했다: {error}</section> : null}

      <section className="overview-grid">
        <article className="panel-card chart-card">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Region Split</p>
              <h3>지역별 팝업 분포</h3>
            </div>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={regionData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e2d8" />
                <XAxis dataKey="region" stroke="#7f7566" />
                <YAxis stroke="#7f7566" />
                <Tooltip />
                <Bar dataKey="count" fill="#0f766e" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel-card chart-card">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Trend</p>
              <h3>월별 운영 추이</h3>
            </div>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <LineChart data={monthlyData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e2d8" />
                <XAxis dataKey="month" stroke="#7f7566" />
                <YAxis stroke="#7f7566" />
                <Tooltip />
                <Line type="monotone" dataKey="active" stroke="#0f766e" strokeWidth={3} dot={{ r: 4 }} />
                <Line type="monotone" dataKey="new" stroke="#b5793d" strokeWidth={3} dot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="overview-grid overview-grid-bottom">
        <article className="panel-card list-card">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Live List</p>
              <h3>운영 중 팝업 Top List</h3>
            </div>
            <span className="pill-muted">{livePopups.length} entries</span>
          </div>

          {loading ? <div className="loading-block">카탈로그를 불러오는 중...</div> : null}

          {!loading && topLivePopups.length === 0 ? (
            <EmptyState
              icon={Store}
              title="운영 중 팝업이 없다"
              description="현재 날짜 기준 운영 중인 팝업이 없어서 종료 임박이나 전체 인사이트 중심으로 본다."
            />
          ) : null}

          <div className="popup-list">
            {topLivePopups.map((popup) => (
              <button
                key={popup.id}
                type="button"
                className="popup-list-row"
                onClick={() => setSelectedId(popup.id)}
              >
                <div className="popup-list-copy">
                  <div className="popup-list-title-line">
                    <strong>{popup.name}</strong>
                    <StatusBadge status={popup.status} />
                  </div>
                  <p>{popup.address}</p>
                  <span>
                    {popup.region} · {popup.subRegion} · {popup.category}
                  </span>
                </div>
                <div className="popup-list-meta">
                  <span>종료</span>
                  <strong>{popup.endDate}</strong>
                </div>
              </button>
            ))}
          </div>
        </article>

        <article className="panel-card preview-card">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Map Preview</p>
              <h3>탐색 화면 미리보기</h3>
            </div>
          </div>

          <div className="mini-map-preview" aria-hidden="true">
            {catalog.slice(0, 10).map((popup, index) => (
              <span
                key={popup.id}
                className={`mini-map-dot mini-map-dot-${popup.status}`}
                style={{
                  left: `${12 + (index % 4) * 22}%`,
                  top: `${18 + Math.floor(index / 4) * 24}%`
                }}
              />
            ))}
            <div className="mini-map-center-copy">
              <strong>{catalog.length}개 팝업</strong>
              <p>지도, 필터, 상세 패널을 한 번에 본다.</p>
            </div>
          </div>

          <Link className="primary-link-button" to="/map">
            3D 지도 보기
          </Link>
        </article>
      </section>

      <PopupDetailModal popup={selectedPopup} onClose={() => setSelectedId(null)} />
    </div>
  );
}
