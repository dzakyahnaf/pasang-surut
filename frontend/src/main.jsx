import { StrictMode } from "react";
import { createRoot } from "react-dom/client";

import "./styles/dasar.css";
import "./styles/tata-letak.css";
import App from "./App.jsx";

createRoot(document.getElementById("akar")).render(
  <StrictMode>
    <App />
  </StrictMode>
);
