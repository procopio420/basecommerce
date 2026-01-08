import { Outlet, Link, useLocation } from "react-router-dom";
import { useAuth } from "../hooks/useAuth";
import "./Layout.css";

export default function Layout() {
  const { logout } = useAuth();
  const location = useLocation();

  const isActive = (path: string) =>
    location.pathname === path || location.pathname.startsWith(path + "/");

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Construção SaaS</h2>
        </div>
        <nav className="sidebar-nav">
          <Link
            to="/"
            className={
              isActive("/") &&
              !location.pathname.includes("cotacoes") &&
              !location.pathname.includes("pedidos")
                ? "active"
                : ""
            }
          >
            Dashboard
          </Link>
          <Link to="/cotacoes" className={isActive("/cotacoes") ? "active" : ""}>
            Cotações
          </Link>
          <Link to="/pedidos" className={isActive("/pedidos") ? "active" : ""}>
            Pedidos
          </Link>
          <Link to="/clientes" className={isActive("/clientes") ? "active" : ""}>
            Clientes
          </Link>
          <Link to="/produtos" className={isActive("/produtos") ? "active" : ""}>
            Produtos
          </Link>
        </nav>
        <div className="sidebar-footer">
          <button onClick={logout} className="logout-btn">
            Sair
          </button>
        </div>
      </aside>
      <main className="main-content">
        <header className="main-header">
          <h1>Gestão de Cotações e Pedidos</h1>
        </header>
        <div className="content">
          <Outlet />
        </div>
      </main>
    </div>
  );
}
