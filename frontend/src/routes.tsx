import { createBrowserRouter } from "react-router-dom";

import { Layout } from "./components/Layout";
import { InsightsPage } from "./pages/InsightsPage";
import { MapExplorerPage } from "./pages/MapExplorerPage";
import { NotFoundPage } from "./pages/NotFoundPage";
import { OverviewPage } from "./pages/OverviewPage";

export const router = createBrowserRouter([
  {
    path: "/",
    Component: Layout,
    children: [
      { index: true, Component: OverviewPage },
      { path: "map", Component: MapExplorerPage },
      { path: "insights", Component: InsightsPage },
      { path: "*", Component: NotFoundPage }
    ]
  }
]);
