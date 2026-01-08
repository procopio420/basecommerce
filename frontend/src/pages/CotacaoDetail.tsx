import { useParams, useNavigate } from "react-router-dom";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import api from "../services/api";
import "./CotacaoDetail.css";

interface CotacaoItem {
  id: string;
  produto_id: string;
  quantidade: number;
  preco_unitario: number;
  desconto_percentual: number;
  valor_total: number;
}

interface Cotacao {
  id: string;
  numero: string;
  cliente_id: string;
  obra_id?: string;
  status: string;
  desconto_percentual: number;
  observacoes?: string;
  created_at: string;
  itens: CotacaoItem[];
}

export default function CotacaoDetail() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: cotacao, isLoading } = useQuery<Cotacao>({
    queryKey: ["cotacao", id],
    queryFn: async () => {
      const response = await api.get(`/cotacoes/${id}`);
      return response.data;
    },
  });

  const enviarMutation = useMutation({
    mutationFn: async () => {
      await api.post(`/cotacoes/${id}/enviar`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cotacao", id] });
      queryClient.invalidateQueries({ queryKey: ["cotacoes"] });
    },
  });

  const aprovarMutation = useMutation({
    mutationFn: async () => {
      await api.post(`/cotacoes/${id}/aprovar`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["cotacao", id] });
      queryClient.invalidateQueries({ queryKey: ["cotacoes"] });
    },
  });

  const converterMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post(`/pedidos/from-cotacao/${id}`);
      return response.data;
    },
    onSuccess: (pedido) => {
      queryClient.invalidateQueries({ queryKey: ["cotacao", id] });
      queryClient.invalidateQueries({ queryKey: ["cotacoes"] });
      navigate(`/pedidos/${pedido.id}`);
    },
  });

  if (isLoading) {
    return <div className="loading">Carregando...</div>;
  }

  if (!cotacao) {
    return <div className="error">Cotação não encontrada</div>;
  }

  const total = cotacao.itens.reduce((sum, item) => sum + Number(item.valor_total), 0);
  const descontoGeral = total * (Number(cotacao.desconto_percentual) / 100);
  const totalFinal = total - descontoGeral;

  return (
    <div className="cotacao-detail">
      <div className="detail-header">
        <h2>Cotação {cotacao.numero}</h2>
        <div className="actions">
          {cotacao.status === "rascunho" && (
            <button
              onClick={() => enviarMutation.mutate()}
              className="btn-secondary"
              disabled={enviarMutation.isPending}
            >
              Enviar
            </button>
          )}
          {cotacao.status === "enviada" && (
            <button
              onClick={() => aprovarMutation.mutate()}
              className="btn-secondary"
              disabled={aprovarMutation.isPending}
            >
              Marcar como Aprovada
            </button>
          )}
          {cotacao.status === "aprovada" && (
            <button
              onClick={() => converterMutation.mutate()}
              className="btn-primary"
              disabled={converterMutation.isPending}
            >
              {converterMutation.isPending ? "Convertendo..." : "Converter em Pedido"}
            </button>
          )}
        </div>
      </div>

      <div className="detail-info">
        <div className="info-card">
          <h3>Informações</h3>
          <p>
            <strong>Status:</strong>{" "}
            <span className={`status-${cotacao.status}`}>{cotacao.status}</span>
          </p>
          <p>
            <strong>Data:</strong> {new Date(cotacao.created_at).toLocaleString("pt-BR")}
          </p>
        </div>
      </div>

      <div className="itens-section">
        <h3>Itens</h3>
        <table>
          <thead>
            <tr>
              <th>Produto</th>
              <th>Qtd</th>
              <th>Preço Unit.</th>
              <th>Desc%</th>
              <th>Total</th>
            </tr>
          </thead>
          <tbody>
            {cotacao.itens.map((item) => (
              <tr key={item.id}>
                <td>{item.produto_id}</td>
                <td>{item.quantidade}</td>
                <td>R$ {Number(item.preco_unitario).toFixed(2)}</td>
                <td>{item.desconto_percentual}%</td>
                <td>R$ {Number(item.valor_total).toFixed(2)}</td>
              </tr>
            ))}
          </tbody>
        </table>

        <div className="totals">
          <div className="total-row">
            <span>Subtotal:</span>
            <span>R$ {total.toFixed(2)}</span>
          </div>
          <div className="total-row">
            <span>Desconto Geral ({cotacao.desconto_percentual}%):</span>
            <span>-R$ {descontoGeral.toFixed(2)}</span>
          </div>
          <div className="total-row total-final">
            <span>TOTAL:</span>
            <span>R$ {totalFinal.toFixed(2)}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
