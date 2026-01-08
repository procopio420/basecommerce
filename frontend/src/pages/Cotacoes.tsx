import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../services/api";
import "./Cotacoes.css";

interface Cotacao {
  id: string;
  numero: string;
  cliente_id: string;
  status: string;
  created_at: string;
}

export default function Cotacoes() {
  const { data, isLoading, refetch } = useQuery<Cotacao[]>({
    queryKey: ["cotacoes"],
    queryFn: async () => {
      const response = await api.get("/cotacoes/");
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="cotacoes-page">
      <div className="page-header">
        <h2>Cotações</h2>
        <Link to="/cotacoes/nova" className="btn-primary">
          + Nova Cotação
        </Link>
      </div>

      <div className="cotacoes-table">
        <table>
          <thead>
            <tr>
              <th>Número</th>
              <th>Cliente</th>
              <th>Status</th>
              <th>Data</th>
              <th>Ações</th>
            </tr>
          </thead>
          <tbody>
            {data && data.length > 0 ? (
              data.map((cotacao) => (
                <tr key={cotacao.id}>
                  <td>{cotacao.numero}</td>
                  <td>{cotacao.cliente_id}</td>
                  <td>
                    <span className={`status-badge status-${cotacao.status}`}>
                      {cotacao.status}
                    </span>
                  </td>
                  <td>{new Date(cotacao.created_at).toLocaleDateString("pt-BR")}</td>
                  <td>
                    <Link to={`/cotacoes/${cotacao.id}`} className="btn-link">
                      Ver
                    </Link>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="empty-state">
                  Nenhuma cotação encontrada
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
