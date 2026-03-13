import { Compass } from "lucide-react";
import { Link } from "react-router-dom";

export function NotFoundPage() {
  return (
    <div className="page page-not-found">
      <div className="not-found-card">
        <Compass className="not-found-icon" />
        <h2>페이지를 찾지 못했다</h2>
        <p>대시보드 구조는 Overview, Map, Insights 기준으로 정리되어 있다.</p>
        <Link className="primary-link-button" to="/">
          Overview로 돌아가기
        </Link>
      </div>
    </div>
  );
}
