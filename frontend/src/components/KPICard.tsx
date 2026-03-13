import type { LucideIcon } from "lucide-react";

type KPICardProps = {
  title: string;
  value: string | number;
  icon: LucideIcon;
  subtitle?: string;
  accent?: boolean;
};

export function KPICard({ title, value, icon: Icon, subtitle, accent = false }: KPICardProps) {
  return (
    <article className={`kpi-card${accent ? " kpi-card-accent" : ""}`}>
      <div className="kpi-card-top">
        <div className="kpi-icon-wrap">
          <Icon className="kpi-icon" />
        </div>
      </div>
      <p className="kpi-title">{title}</p>
      <strong className="kpi-value">{value}</strong>
      {subtitle ? <p className="kpi-subtitle">{subtitle}</p> : null}
    </article>
  );
}
