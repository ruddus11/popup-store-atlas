import { Download, Store } from "lucide-react";
import { useState } from "react";
import { Bar, BarChart, CartesianGrid, Cell, Pie, PieChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";

import { EmptyState } from "../components/EmptyState";
import { PopupDetailModal } from "../components/PopupDetailModal";
import { StatusBadge } from "../components/StatusBadge";
import { getCategoryDistribution, getMonthlyTrend, getRegionCounts, PopupItem, usePopupData } from "../popup-data";

const PIE_COLORS = ["#0f766e", "#b5793d", "#223049", "#8b7961", "#d2c2ae"];

type SortField = "name" | "region" | "startDate" | "endDate";

export function InsightsPage() {
  const { catalog, loading } = usePopupData();
  const [selectedId, setSelectedId] = useState<number | null>(null);
  const [sortField, setSortField] = useState<SortField>("startDate");
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("desc");
  const selectedPopup = catalog.find((popup) => popup.id === selectedId) ?? null;

  const regionData = getRegionCounts(catalog);
  const categoryData = getCategoryDistribution(catalog);
  const trendData = getMonthlyTrend(catalog);

  const sortedPopups = [...catalog].sort((left, right) => comparePopups(left, right, sortField, sortDirection));

  return (
    <div className="page page-insights">
      <header className="page-header compact with-action">
        <div>
          <p className="section-kicker">Insights</p>
          <h2>차트와 표로 읽는 전체 카탈로그</h2>
          <p className="page-lead">Figma 시안의 분석 화면 구성을 현재 데이터 구조에 맞춰 현실적으로 옮겼다.</p>
        </div>
        <button type="button" className="secondary-button" disabled>
          <Download size={16} />
          <span>내보내기 준비 중</span>
        </button>
      </header>

      <section className="insights-grid">
        <article className="panel-card chart-card">
          <div className="panel-head">
            <div>
              <p className="section-kicker">By Region</p>
              <h3>지역별 분포</h3>
            </div>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={regionData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e2d8" />
                <XAxis type="number" stroke="#7f7566" />
                <YAxis type="category" dataKey="region" stroke="#7f7566" />
                <Tooltip />
                <Bar dataKey="count" fill="#0f766e" radius={[0, 10, 10, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel-card chart-card">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Category Split</p>
              <h3>카테고리 분포</h3>
            </div>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <PieChart>
                <Pie data={categoryData} dataKey="value" nameKey="name" outerRadius={96} innerRadius={52}>
                  {categoryData.map((entry, index) => (
                    <Cell key={`${entry.name}-${index}`} fill={PIE_COLORS[index % PIE_COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </article>

        <article className="panel-card chart-card span-two">
          <div className="panel-head">
            <div>
              <p className="section-kicker">Monthly Signal</p>
              <h3>월별 운영 추이</h3>
            </div>
          </div>
          <div className="chart-wrap">
            <ResponsiveContainer width="100%" height={280}>
              <BarChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e8e2d8" />
                <XAxis dataKey="month" stroke="#7f7566" />
                <YAxis stroke="#7f7566" />
                <Tooltip />
                <Bar dataKey="active" fill="#0f766e" radius={[10, 10, 0, 0]} />
                <Bar dataKey="new" fill="#b5793d" radius={[10, 10, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </article>
      </section>

      <section className="panel-card table-card">
        <div className="panel-head">
          <div>
            <p className="section-kicker">Catalog Table</p>
            <h3>전체 팝업 목록</h3>
          </div>
          <span className="pill-muted">{catalog.length} rows</span>
        </div>

        {loading ? <div className="loading-block">데이터 테이블을 준비하는 중...</div> : null}

        {!loading && catalog.length === 0 ? (
          <EmptyState
            icon={Store}
            title="표시할 카탈로그가 없다"
            description="크롤링 데이터가 비어 있거나 아직 적재되지 않았다."
          />
        ) : null}

        <div className="table-scroll">
          <table className="insights-table">
            <thead>
              <tr>
                <th>
                  <button type="button" onClick={() => toggleSort("name", sortField, sortDirection, setSortField, setSortDirection)}>
                    팝업명
                  </button>
                </th>
                <th>
                  <button type="button" onClick={() => toggleSort("region", sortField, sortDirection, setSortField, setSortDirection)}>
                    지역
                  </button>
                </th>
                <th>카테고리</th>
                <th>
                  <button type="button" onClick={() => toggleSort("startDate", sortField, sortDirection, setSortField, setSortDirection)}>
                    시작일
                  </button>
                </th>
                <th>
                  <button type="button" onClick={() => toggleSort("endDate", sortField, sortDirection, setSortField, setSortDirection)}>
                    종료일
                  </button>
                </th>
                <th>상태</th>
              </tr>
            </thead>
            <tbody>
              {sortedPopups.map((popup) => (
                <tr key={popup.id} onClick={() => setSelectedId(popup.id)}>
                  <td>
                    <div className="table-title-cell">
                      <strong>{popup.name}</strong>
                      <span>{popup.subRegion}</span>
                    </div>
                  </td>
                  <td>{popup.region}</td>
                  <td>{popup.category}</td>
                  <td>{popup.startDate}</td>
                  <td>{popup.endDate}</td>
                  <td>
                    <StatusBadge status={popup.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <PopupDetailModal popup={selectedPopup} onClose={() => setSelectedId(null)} />
    </div>
  );
}

function comparePopups(
  left: PopupItem,
  right: PopupItem,
  field: SortField,
  direction: "asc" | "desc"
) {
  const modifier = direction === "asc" ? 1 : -1;

  if (field === "name" || field === "region") {
    return left[field].localeCompare(right[field]) * modifier;
  }

  return (new Date(left[field]).getTime() - new Date(right[field]).getTime()) * modifier;
}

function toggleSort(
  field: SortField,
  currentField: SortField,
  currentDirection: "asc" | "desc",
  setSortField: (field: SortField) => void,
  setSortDirection: (direction: "asc" | "desc") => void
) {
  if (currentField === field) {
    setSortDirection(currentDirection === "asc" ? "desc" : "asc");
    return;
  }

  setSortField(field);
  setSortDirection("asc");
}
