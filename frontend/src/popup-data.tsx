import { createContext, useContext, useEffect, useState, type ReactNode } from "react";

import { FALLBACK_AS_OF_DATE, FALLBACK_CATALOG } from "./fallback-catalog";

const API_BASE_URL = import.meta.env.DEV
  ? (import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000")
  : "";
const REQUEST_TIMEOUT_MS = 12000;

export type PopupStatus = "active" | "ending-soon" | "ended" | "upcoming";

type RawPopupItem = {
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
  items: RawPopupItem[];
};

export type PopupItem = {
  id: number;
  name: string;
  address: string;
  startDate: string;
  endDate: string;
  lat: number;
  lng: number;
  sourceUrl: string;
  popularity: number;
  region: string;
  subRegion: string;
  category: string;
  status: PopupStatus;
  daysRemaining: number;
};

type PopupDataContextValue = {
  asOfDate: string;
  catalog: PopupItem[];
  livePopups: PopupItem[];
  endingSoon: PopupItem[];
  loading: boolean;
  error: string;
  isFallback: boolean;
};

const PopupDataContext = createContext<PopupDataContextValue | null>(null);

const CATEGORY_RULES: Array<[RegExp, string]> = [
  [/(커피|카페|베이커리|티|푸드|f&b)/i, "F&B"],
  [/(뷰티|skin|cosmetic|ahc|beauty)/i, "뷰티"],
  [/(패밀리|캐릭터|toy|굿즈|프렌즈)/i, "캐릭터"],
  [/(커피|팝업존|롯데월드몰|더현대|현대백화점)/i, "라이프스타일"],
  [/(fashion|ralph|marni|jordan|나이키|무신사|젠틀몬스터)/i, "패션"]
];

const ALLOWED_SOURCE_DOMAINS = ["ehyundai.com", "marieclairekorea.com", "tistory.com"];

function inferRegion(address: string) {
  if (address.startsWith("서울")) return "서울";
  if (address.startsWith("경기") || address.startsWith("인천")) return "경기";
  if (address.startsWith("대전") || address.startsWith("충청") || address.startsWith("세종")) {
    return "충청";
  }
  return "기타";
}

function inferSubRegion(address: string) {
  const parts = address.split(/\s+/).filter(Boolean);
  return parts[1] ?? parts[0] ?? "상세 지역";
}

function inferCategory(name: string) {
  for (const [pattern, label] of CATEGORY_RULES) {
    if (pattern.test(name)) {
      return label;
    }
  }
  return "팝업";
}

function toStatus(startDate: string, endDate: string, asOfDate: string): PopupStatus {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const today = new Date(asOfDate);
  const diffDays = Math.ceil((end.getTime() - today.getTime()) / (1000 * 60 * 60 * 24));

  if (start.getTime() > today.getTime()) {
    return "upcoming";
  }
  if (end.getTime() < today.getTime()) {
    return "ended";
  }
  if (diffDays <= 7) {
    return "ending-soon";
  }
  return "active";
}

function transformItem(item: RawPopupItem, asOfDate: string): PopupItem {
  return {
    id: item.id,
    name: item.name,
    address: item.address,
    startDate: item.start_date,
    endDate: item.end_date,
    lat: item.latitude,
    lng: item.longitude,
    sourceUrl: item.source_url,
    popularity: item.popularity,
    region: inferRegion(item.address),
    subRegion: inferSubRegion(item.address),
    category: inferCategory(item.name),
    status: toStatus(item.start_date, item.end_date, asOfDate),
    daysRemaining: Math.ceil(
      (new Date(item.end_date).getTime() - new Date(asOfDate).getTime()) / (1000 * 60 * 60 * 24)
    )
  };
}

function createStateFromPayload(payload: ApiResponse, error = "", isFallback = false): PopupDataContextValue {
  const catalog = payload.items.map((item) => transformItem(item, payload.as_of_date));
  const livePopups = catalog.filter(
    (popup) => popup.status === "active" || popup.status === "ending-soon"
  );
  const endingSoon = catalog.filter((popup) => popup.status === "ending-soon");

  return {
    asOfDate: payload.as_of_date,
    catalog,
    livePopups,
    endingSoon,
    loading: false,
    error,
    isFallback
  };
}

function createFallbackState(error: string): PopupDataContextValue {
  return createStateFromPayload(
    {
      as_of_date: FALLBACK_AS_OF_DATE,
      count: FALLBACK_CATALOG.length,
      items: [...FALLBACK_CATALOG]
    },
    error,
    true
  );
}

export function isSafeSourceUrl(url: string) {
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

export function getRegionCounts(popups: PopupItem[]) {
  return ["서울", "경기", "충청"].map((region) => ({
    region,
    count: popups.filter((popup) => popup.region === region && popup.status !== "ended").length
  }));
}

export function getCategoryDistribution(popups: PopupItem[]) {
  return popups
    .filter((popup) => popup.status !== "ended")
    .reduce<Array<{ name: string; value: number }>>((acc, popup) => {
      const existing = acc.find((item) => item.name === popup.category);
      if (existing) {
        existing.value += 1;
      } else {
        acc.push({ name: popup.category, value: 1 });
      }
      return acc;
    }, []);
}

export function getMonthlyTrend(popups: PopupItem[]) {
  const bucket = new Map<string, { month: string; active: number; new: number }>();

  for (const popup of popups) {
    const startMonth = `${new Date(popup.startDate).getFullYear()}-${String(
      new Date(popup.startDate).getMonth() + 1
    ).padStart(2, "0")}`;
    const endMonth = `${new Date(popup.endDate).getFullYear()}-${String(
      new Date(popup.endDate).getMonth() + 1
    ).padStart(2, "0")}`;

    if (!bucket.has(startMonth)) {
      bucket.set(startMonth, { month: startMonth, active: 0, new: 0 });
    }
    bucket.get(startMonth)!.new += 1;

    if (!bucket.has(endMonth)) {
      bucket.set(endMonth, { month: endMonth, active: 0, new: 0 });
    }
    if (popup.status !== "ended") {
      bucket.get(endMonth)!.active += 1;
    }
  }

  return [...bucket.values()]
    .sort((a, b) => a.month.localeCompare(b.month))
    .slice(-6)
    .map((item) => ({
      month: `${item.month.slice(5)}월`,
      active: item.active,
      new: item.new
    }));
}

export function PopupDataProvider({ children }: { children: ReactNode }) {
  const [state, setState] = useState<PopupDataContextValue>({
    asOfDate: "",
    catalog: [],
    livePopups: [],
    endingSoon: [],
    loading: true,
    error: "",
    isFallback: false
  });

  useEffect(() => {
    const controller = new AbortController();
    const timeoutId = window.setTimeout(() => controller.abort("timeout"), REQUEST_TIMEOUT_MS);

    const loadCatalog = async () => {
      setState((current) => ({ ...current, loading: true, error: "", isFallback: false }));

      try {
        const response = await fetch(`${API_BASE_URL}/api/popups/catalog`, {
          signal: controller.signal
        });
        if (!response.ok) {
          throw new Error(`API request failed with ${response.status}`);
        }

        const payload = (await response.json()) as ApiResponse;
        setState(createStateFromPayload(payload));
      } catch (error) {
        if (controller.signal.aborted) {
          setState(
            createFallbackState("실시간 API 응답이 지연되어 저장된 카탈로그를 먼저 표시한다.")
          );
          return;
        }
        const message = error instanceof Error ? error.message : "Unknown error";
        setState(createFallbackState(`실시간 API 연결에 실패해 저장된 카탈로그를 표시한다. (${message})`));
      } finally {
        window.clearTimeout(timeoutId);
      }
    };

    void loadCatalog();
    return () => {
      window.clearTimeout(timeoutId);
      controller.abort();
    };
  }, []);

  return <PopupDataContext.Provider value={state}>{children}</PopupDataContext.Provider>;
}

export function usePopupData() {
  const value = useContext(PopupDataContext);
  if (!value) {
    throw new Error("usePopupData must be used inside PopupDataProvider");
  }
  return value;
}
