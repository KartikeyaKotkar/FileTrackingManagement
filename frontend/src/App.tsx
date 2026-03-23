import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login from "./pages/login";
import Dashboard from "./pages/dashboard";
import DocumentDetail from "./pages/document-detail";
import "./App.css";

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/documents" element={<Dashboard />} />
        <Route path="/settings" element={<Dashboard />} />
        <Route path="/departments-view" element={<Dashboard />} />
        <Route path="/users-view" element={<Dashboard />} />
        <Route path="/documents/:id" element={<DocumentDetail />} />
        <Route path="*" element={<Navigate to="/dashboard" replace />} />
      </Routes>
    </BrowserRouter>
  );
}

export default App;
