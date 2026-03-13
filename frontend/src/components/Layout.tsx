import { BarChart3, LayoutDashboard, Map, Menu, X } from "lucide-react";
import { useState } from "react";
import { NavLink, Outlet } from "react-router-dom";

import { usePopupData } from "../popup-data";

const NAV_ITEMS = [
  { to: "/", label: "Overview", icon: LayoutDashboard, end: true },
  { to: "/map", label: "Map", icon: Map },
  { to: "/insights", label: "Insights", icon: BarChart3 }
];

export function Layout() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const { asOfDate } = usePopupData();

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <p className="brand-kicker">Popup Intelligence</p>
          <h1>Popup Store Atlas</h1>
          <p className="brand-copy">팝업스토어 데이터를 탐색과 인사이트 기준으로 다시 본다.</p>
        </div>

        <nav className="sidebar-nav">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `nav-link${isActive ? " nav-link-active" : ""}`
              }
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        <div className="sidebar-footnote">
          <span className="sidebar-footnote-label">Catalog As Of</span>
          <strong>{asOfDate || "-"}</strong>
        </div>
      </aside>

      <header className="mobile-bar">
        <div>
          <p className="brand-kicker">Popup Intelligence</p>
          <strong>Popup Store Atlas</strong>
        </div>
        <button
          type="button"
          className="menu-toggle"
          onClick={() => setMobileMenuOpen((open) => !open)}
          aria-label="메뉴 토글"
        >
          {mobileMenuOpen ? <X /> : <Menu />}
        </button>
      </header>

      {mobileMenuOpen ? (
        <nav className="mobile-nav-panel">
          {NAV_ITEMS.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              end={item.end}
              className={({ isActive }) =>
                `nav-link${isActive ? " nav-link-active" : ""}`
              }
              onClick={() => setMobileMenuOpen(false)}
            >
              <item.icon className="nav-icon" />
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>
      ) : null}

      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
