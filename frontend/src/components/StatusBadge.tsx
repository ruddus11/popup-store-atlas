import type { PopupStatus } from "../popup-data";

type StatusBadgeProps = {
  status: PopupStatus;
};

const STATUS_MAP: Record<PopupStatus, { label: string; className: string }> = {
  active: { label: "운영 중", className: "status-active" },
  "ending-soon": { label: "종료 임박", className: "status-ending" },
  ended: { label: "종료됨", className: "status-ended" },
  upcoming: { label: "오픈 예정", className: "status-upcoming" }
};

export function StatusBadge({ status }: StatusBadgeProps) {
  const config = STATUS_MAP[status];
  return <span className={`status-badge ${config.className}`}>{config.label}</span>;
}
