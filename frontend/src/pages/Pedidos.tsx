import { useQuery } from "@tanstack/react-query";
import { Link } from "react-router-dom";
import api from "../services/api";
import "./Pedidos.css";

interface Pedido {
  id: string;
  numero: string;
  cliente_id: string;
  status: string;
  created_at: string;
}

export default function Pedidos() {
  const { data, isLoading } = useQuery<Pedido[]>({
    queryKey: ["pedidos"],
    queryFn: async () => {
      const response = await api.get("/pedidos/");
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="pedidos-page">
      <div className="page-header">
        <h2>Pedidos</h2>
      </div>

      <div className="pedidos-table">
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
              data.map((pedido) => (
                <tr key={pedido.id}>
                  <td>{pedido.numero}</td>
                  <td>{pedido.cliente_id}</td>
                  <td>
                    <span className={`status-badge status-${pedido.status}`}>{pedido.status}</span>
                  </td>
                  <td>{new Date(pedido.created_at).toLocaleDateString("pt-BR")}</td>
                  <td>
                    <Link to={`/pedidos/${pedido.id}`} className="btn-link">
                      Ver
                    </Link>
                  </td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={5} className="empty-state">
                  Nenhum pedido encontrado
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
