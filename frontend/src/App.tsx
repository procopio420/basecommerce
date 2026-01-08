import { Routes, Route, Navigate } from "react-router-dom";
import { useAuth } from "./hooks/useAuth";
import Login from "./pages/Login";
import Dashboard from "./pages/Dashboard";
import Cotacoes from "./pages/Cotacoes";
import CotacaoDetail from "./pages/CotacaoDetail";
import NovaCotacao from "./pages/NovaCotacao";
import Pedidos from "./pages/Pedidos";
import Clientes from "./pages/Clientes";
import Produtos from "./pages/Produtos";
import Layout from "./components/Layout";

function App() {
  const { isAuthenticated } = useAuth();

  return (
    <Routes>
      <Route path="/login" element={!isAuthenticated ? <Login /> : <Navigate to="/" />} />
      <Route path="/" element={isAuthenticated ? <Layout /> : <Navigate to="/login" />}>
        <Route index element={<Dashboard />} />
        <Route path="cotacoes" element={<Cotacoes />} />
        <Route path="cotacoes/nova" element={<NovaCotacao />} />
        <Route path="cotacoes/:id" element={<CotacaoDetail />} />
        <Route path="pedidos" element={<Pedidos />} />
        <Route path="clientes" element={<Clientes />} />
        <Route path="produtos" element={<Produtos />} />
      </Route>
    </Routes>
  );
}

export default App;
