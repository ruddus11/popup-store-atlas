import { ExternalLink, MapPin, X } from "lucide-react";

import { PopupItem, isSafeSourceUrl } from "../popup-data";
import { StatusBadge } from "./StatusBadge";

type PopupDetailModalProps = {
  popup: PopupItem | null;
  onClose: () => void;
};

function formatDateRange(popup: PopupItem) {
  return `${popup.startDate} - ${popup.endDate}`;
}

export function PopupDetailModal({ popup, onClose }: PopupDetailModalProps) {
  if (!popup) {
    return null;
  }

  const safeSourceUrl = isSafeSourceUrl(popup.sourceUrl) ? popup.sourceUrl : null;

  return (
    <div className="modal-scrim" role="presentation" onClick={onClose}>
      <section
        className="modal-card"
        role="dialog"
        aria-modal="true"
        aria-label={`${popup.name} 상세`}
        onClick={(event) => event.stopPropagation()}
      >
        <header className="modal-head">
          <div>
            <p className="section-kicker">Popup Detail</p>
            <h3>{popup.name}</h3>
          </div>
          <button type="button" className="icon-button" onClick={onClose} aria-label="닫기">
            <X />
          </button>
        </header>

        <div className="detail-stack">
          <div className="detail-meta-line">
            <StatusBadge status={popup.status} />
            <span className="detail-chip">{popup.category}</span>
            <span className="detail-chip">{popup.region}</span>
          </div>

          <div className="detail-block">
            <p className="detail-label">주소</p>
            <strong>{popup.address}</strong>
            <span>{popup.subRegion}</span>
          </div>

          <div className="detail-grid">
            <div className="detail-block">
              <p className="detail-label">운영 기간</p>
              <strong>{formatDateRange(popup)}</strong>
            </div>
            <div className="detail-block">
              <p className="detail-label">위치 좌표</p>
              <strong>
                {popup.lat.toFixed(4)}, {popup.lng.toFixed(4)}
              </strong>
            </div>
          </div>

          <div className="detail-preview">
            <MapPin />
            <div>
              <strong>{popup.name}</strong>
              <p>지도 탐색 화면에서 컬럼과 함께 위치를 확인할 수 있다.</p>
            </div>
          </div>

          {safeSourceUrl ? (
            <a className="primary-link-button" href={safeSourceUrl} target="_blank" rel="noopener noreferrer">
              <span>원문 보기</span>
              <ExternalLink size={16} />
            </a>
          ) : (
            <p className="detail-note">검증된 원문 링크가 없어 외부 링크를 숨겼다.</p>
          )}
        </div>
      </section>
    </div>
  );
}
