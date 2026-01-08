import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../services/api";
import "./Dashboard.css";

interface DashboardData {
  cotacoes_hoje: number;
  pedidos_hoje: number;
  pedidos_semana: number;
  cotacoes_recentes: Array<{
    id: string;
    numero: string;
    cliente_id: string;
    status: string;
    created_at: string;
  }>;
}

export default function Dashboard() {
  const { data, isLoading } = useQuery<DashboardData>({
    queryKey: ["dashboard"],
    queryFn: async () => {
      const response = await api.get("/dashboard/");
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="dashboard">
      <div className="dashboard-header">
        <h2>Dashboard</h2>
        <Link to="/cotacoes/nova" className="btn-primary">
          + Nova Cotação
        </Link>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-label">Cotações Hoje</div>
          <div className="stat-value">{data?.cotacoes_hoje || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pedidos Hoje</div>
          <div className="stat-value">{data?.pedidos_hoje || 0}</div>
        </div>
        <div className="stat-card">
          <div className="stat-label">Pedidos Semana</div>
          <div className="stat-value">{data?.pedidos_semana || 0}</div>
        </div>
      </div>

      <div className="dashboard-section">
        <h3>Cotações Recentes</h3>
        {data?.cotacoes_recentes && data.cotacoes_recentes.length > 0 ? (
          <div className="cotacoes-list">
            {data.cotacoes_recentes.map((cotacao) => (
              <Link key={cotacao.id} to={`/cotacoes/${cotacao.id}`} className="cotacao-item">
                <div className="cotacao-numero">{cotacao.numero}</div>
                <div className={`cotacao-status status-${cotacao.status}`}>{cotacao.status}</div>
              </Link>
            ))}
          </div>
        ) : (
          <p className="empty-state">Nenhuma cotação recente</p>
        )}
        <Link to="/cotacoes" className="view-all-link">
          Ver todas as cotações →
        </Link>
      </div>
    </div>
  );
}
