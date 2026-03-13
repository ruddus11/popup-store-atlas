import { RouterProvider } from "react-router-dom";

import { PopupDataProvider } from "./popup-data";
import { router } from "./routes";

export default function App() {
  return (
    <PopupDataProvider>
      <RouterProvider router={router} />
    </PopupDataProvider>
  );
}
