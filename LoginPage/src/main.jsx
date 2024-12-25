import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import "./index.css";
import App from "./App.jsx";
import { AuthProvider } from "./StoreContext/AuthContext.jsx";
import { BrowserRouter } from "react-router-dom";
import { GlobalProvider } from "../user.jsx";

createRoot(document.getElementById("root")).render(
  <GlobalProvider>
  <BrowserRouter>
    <StrictMode>
      <AuthProvider>
        <App />
      </AuthProvider>
    </StrictMode>
  </BrowserRouter>
  </GlobalProvider>
);
