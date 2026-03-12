import type { ReactNode } from "react";

import { act, render, screen, waitFor } from "@testing-library/react";
import { vi } from "vitest";

import App from "./App";

let latestLayerProps: Record<string, unknown> | null = null;

vi.mock("@deck.gl/react", () => ({
  default: ({ children }: { children: ReactNode }) => <div data-testid="deckgl">{children}</div>
}));

vi.mock("@deck.gl/layers", () => ({
  ColumnLayer: class {
    props: Record<string, unknown>;

    constructor(props: Record<string, unknown>) {
      latestLayerProps = props;
      this.props = props;
    }
  }
}));

vi.mock("react-map-gl/mapbox", () => ({
  Map: () => <div data-testid="mapbox-map" />
}));

describe("App", () => {
  beforeEach(() => {
    latestLayerProps = null;
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({
          as_of_date: "2026-03-12",
          count: 1,
          items: [
            {
              id: 1,
              name: "AHC SKIN GAME T SHOT 팝업",
              address: "서울 성동구 연무장11길 13",
              start_date: "2026-03-01",
              end_date: "2026-03-31",
              latitude: 37.5432,
              longitude: 127.0568,
              source_url: "https://example.com/ahc",
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

  it("renders active popup data and shows a tooltip when a column is clicked", async () => {
    render(<App />);

    await waitFor(() => {
      expect(screen.getByText("운영 중 팝업")).toBeInTheDocument();
      expect(screen.getByText("AHC SKIN GAME T SHOT 팝업")).toBeInTheDocument();
    });

    expect(latestLayerProps).not.toBeNull();

    await act(async () => {
      (latestLayerProps?.onClick as (info: Record<string, unknown>) => void)({
        object: {
          id: 1,
          name: "AHC SKIN GAME T SHOT 팝업",
          address: "서울 성동구 연무장11길 13",
          start_date: "2026-03-01",
          end_date: "2026-03-31",
          latitude: 37.5432,
          longitude: 127.0568,
          source_url: "https://example.com/ahc",
          popularity: 100
        },
        x: 48,
        y: 64
      });
    });

    expect(screen.getAllByText("AHC SKIN GAME T SHOT 팝업").length).toBeGreaterThan(0);
    expect(screen.getAllByText("2026-03-01 - 2026-03-31").length).toBeGreaterThan(0);
  });
});
