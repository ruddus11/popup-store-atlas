import type { ReactNode } from "react";

import { render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";

vi.mock("@deck.gl/react", () => ({
  default: ({ children }: { children: ReactNode }) => <div data-testid="deckgl">{children}</div>
}));

vi.mock("@deck.gl/layers", () => ({
  ColumnLayer: class {
    constructor(public props: Record<string, unknown>) {}
  }
}));

vi.mock("react-map-gl/mapbox", () => ({
  Map: () => <div data-testid="mapbox-map" />
}));

describe("App", () => {
  beforeEach(() => {
    window.history.replaceState({}, "", "/");
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          as_of_date: "2026-03-12",
          count: 2,
          items: [
            {
              id: 1,
              name: "AHC SKIN GAME T SHOT 팝업",
              address: "서울 성동구 연무장11길 13",
              start_date: "2026-03-01",
              end_date: "2026-03-31",
              latitude: 37.5432,
              longitude: 127.0568,
              source_url: "https://www.marieclairekorea.com/newnew/2026/03/ahc-popup/",
              popularity: 100
            },
            {
              id: 2,
              name: "실바니안 패밀리 40주년 팝업스토어",
              address: "서울 용산구 한강대로23길 55 더 센터 6층",
              start_date: "2025-02-21",
              end_date: "2025-03-06",
              latitude: 37.529,
              longitude: 126.965,
              source_url: "https://www.marieclairekorea.com/newnew/2025/02/march-pop-up/",
              popularity: 100
            }
          ]
        })
      })
    );
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("renders overview metrics and navigation from the Figma-inspired layout", async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("한눈에 보는 팝업 운영 보드")).toBeInTheDocument();
      expect(screen.getByText("현재 운영 중")).toBeInTheDocument();
      expect(screen.getByText("운영 중 팝업 Top List")).toBeInTheDocument();
      expect(screen.getAllByText("AHC SKIN GAME T SHOT 팝업").length).toBeGreaterThan(0);
    });

    expect(screen.getByRole("link", { name: "Overview" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Map" })).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Insights" })).toBeInTheDocument();
  });
});
