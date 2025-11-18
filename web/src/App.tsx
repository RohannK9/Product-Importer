import { Navigate, Route, Routes } from "react-router-dom";
import { Layout } from "./components/Layout";
import { UploadPage } from "./pages/UploadPage";
import { ProductsPage } from "./pages/ProductsPage";
import { WebhooksPage } from "./pages/WebhooksPage";

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Navigate to="/upload" replace />} />
        <Route path="/upload" element={<UploadPage />} />
        <Route path="/products" element={<ProductsPage />} />
        <Route path="/webhooks" element={<WebhooksPage />} />
      </Routes>
    </Layout>
  );
}

export default App;
