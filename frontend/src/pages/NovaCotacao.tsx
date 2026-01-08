import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useMutation, useQuery } from "@tanstack/react-query";
import api from "../services/api";
import "./NovaCotacao.css";

interface Cliente {
  id: string;
  nome: string;
  documento: string;
}

interface Produto {
  id: string;
  nome: string;
  codigo?: string;
  preco_base: number;
  unidade: string;
}

export default function NovaCotacao() {
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [clienteId, setClienteId] = useState("");
  const [searchCliente, setSearchCliente] = useState("");
  const [searchProduto, setSearchProduto] = useState("");
  const [itens, setItens] = useState<
    Array<{
      produto_id: string;
      produto_nome: string;
      quantidade: number;
      preco_unitario: number;
      desconto_percentual: number;
    }>
  >([]);
  const [descontoGeral, setDescontoGeral] = useState(0);
  const [observacoes, setObservacoes] = useState("");

  const { data: clientes } = useQuery<Cliente[]>({
    queryKey: ["clientes", searchCliente],
    queryFn: async () => {
      const response = await api.get("/clientes/", {
        params: { search: searchCliente || undefined },
      });
      return response.data;
    },
    enabled: step === 1,
  });

  const { data: produtos } = useQuery<Produto[]>({
    queryKey: ["produtos", searchProduto],
    queryFn: async () => {
      const response = await api.get("/produtos/", {
        params: { search: searchProduto || undefined, ativo: true },
      });
      return response.data;
    },
    enabled: step === 2,
  });

  const createMutation = useMutation({
    mutationFn: async (data: any) => {
      const response = await api.post("/cotacoes/", data);
      return response.data;
    },
    onSuccess: (cotacao) => {
      navigate(`/cotacoes/${cotacao.id}`);
    },
  });

  const adicionarItem = (produto: Produto) => {
    const itemExistente = itens.find((item) => item.produto_id === produto.id);
    if (itemExistente) {
      setItens(
        itens.map((item) =>
          item.produto_id === produto.id ? { ...item, quantidade: item.quantidade + 1 } : item
        )
      );
    } else {
      setItens([
        ...itens,
        {
          produto_id: produto.id,
          produto_nome: produto.nome,
          quantidade: 1,
          preco_unitario: Number(produto.preco_base),
          desconto_percentual: 0,
        },
      ]);
    }
    setSearchProduto("");
  };

  const removerItem = (produtoId: string) => {
    setItens(itens.filter((item) => item.produto_id !== produtoId));
  };

  const atualizarItem = (produtoId: string, field: string, value: any) => {
    setItens(
      itens.map((item) => (item.produto_id === produtoId ? { ...item, [field]: value } : item))
    );
  };

  const calcularTotal = () => {
    const subtotal = itens.reduce((sum, item) => {
      const valorItem = item.quantidade * item.preco_unitario;
      const descontoItem = valorItem * (item.desconto_percentual / 100);
      return sum + valorItem - descontoItem;
    }, 0);
    const descontoGeralValor = subtotal * (descontoGeral / 100);
    return subtotal - descontoGeralValor;
  };

  const handleFinalizar = () => {
    if (!clienteId || itens.length === 0) {
      alert("Selecione um cliente e adicione pelo menos um item");
      return;
    }

    createMutation.mutate({
      cliente_id: clienteId,
      desconto_percentual: descontoGeral,
      observacoes,
      validade_dias: 7,
      itens: itens.map((item) => ({
        produto_id: item.produto_id,
        quantidade: item.quantidade,
        preco_unitario: item.preco_unitario,
        desconto_percentual: item.desconto_percentual,
      })),
    });
  };

  return (
    <div className="nova-cotacao">
      <h2>Nova Cotação - Passo {step} de 3</h2>

      {step === 1 && (
        <div className="step-content">
          <div className="form-group">
            <label>Buscar Cliente</label>
            <input
              type="text"
              value={searchCliente}
              onChange={(e) => setSearchCliente(e.target.value)}
              placeholder="Nome, documento ou email..."
            />
          </div>
          <div className="clientes-list">
            {clientes &&
              clientes.map((cliente) => (
                <div
                  key={cliente.id}
                  className={`cliente-item ${clienteId === cliente.id ? "selected" : ""}`}
                  onClick={() => setClienteId(cliente.id)}
                >
                  <div>
                    <strong>{cliente.nome}</strong>
                    <span>{cliente.documento}</span>
                  </div>
                  {clienteId === cliente.id && <span>✓</span>}
                </div>
              ))}
          </div>
          <div className="step-actions">
            <button onClick={() => navigate("/cotacoes")}>Cancelar</button>
            <button
              onClick={() => clienteId && setStep(2)}
              disabled={!clienteId}
              className="btn-primary"
            >
              Próximo →
            </button>
          </div>
        </div>
      )}

      {step === 2 && (
        <div className="step-content">
          <div className="form-group">
            <label>Buscar Produto</label>
            <input
              type="text"
              value={searchProduto}
              onChange={(e) => setSearchProduto(e.target.value)}
              placeholder="Nome ou código..."
            />
          </div>
          <div className="produtos-list">
            {produtos &&
              produtos.map((produto) => (
                <div
                  key={produto.id}
                  className="produto-item"
                  onClick={() => adicionarItem(produto)}
                >
                  <div>
                    <strong>{produto.nome}</strong>
                    <span>{produto.codigo || "Sem código"}</span>
                  </div>
                  <div>
                    <span>R$ {Number(produto.preco_base).toFixed(2)}</span>
                    <button>+</button>
                  </div>
                </div>
              ))}
          </div>
          <div className="itens-cotacao">
            <h3>Itens da Cotação</h3>
            {itens.length === 0 ? (
              <p className="empty">Nenhum item adicionado</p>
            ) : (
              <table>
                <thead>
                  <tr>
                    <th>Produto</th>
                    <th>Qtd</th>
                    <th>Preço Unit.</th>
                    <th>Desc%</th>
                    <th>Total</th>
                    <th></th>
                  </tr>
                </thead>
                <tbody>
                  {itens.map((item) => {
                    const valorItem = item.quantidade * item.preco_unitario;
                    const descontoItem = valorItem * (item.desconto_percentual / 100);
                    const totalItem = valorItem - descontoItem;
                    return (
                      <tr key={item.produto_id}>
                        <td>{item.produto_nome}</td>
                        <td>
                          <input
                            type="number"
                            min="0.001"
                            step="0.001"
                            value={item.quantidade}
                            onChange={(e) =>
                              atualizarItem(
                                item.produto_id,
                                "quantidade",
                                parseFloat(e.target.value) || 0
                              )
                            }
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            min="0"
                            step="0.01"
                            value={item.preco_unitario}
                            onChange={(e) =>
                              atualizarItem(
                                item.produto_id,
                                "preco_unitario",
                                parseFloat(e.target.value) || 0
                              )
                            }
                          />
                        </td>
                        <td>
                          <input
                            type="number"
                            min="0"
                            max="100"
                            value={item.desconto_percentual}
                            onChange={(e) =>
                              atualizarItem(
                                item.produto_id,
                                "desconto_percentual",
                                parseFloat(e.target.value) || 0
                              )
                            }
                          />
                        </td>
                        <td>R$ {totalItem.toFixed(2)}</td>
                        <td>
                          <button onClick={() => removerItem(item.produto_id)}>Remover</button>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            )}
          </div>
          <div className="step-actions">
            <button onClick={() => setStep(1)}>← Voltar</button>
            <button
              onClick={() => setStep(3)}
              disabled={itens.length === 0}
              className="btn-primary"
            >
              Finalizar →
            </button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="step-content">
          <div className="resumo">
            <h3>Resumo da Cotação</h3>
            <p>
              <strong>Cliente:</strong> {clientes?.find((c) => c.id === clienteId)?.nome}
            </p>
            <p>
              <strong>Itens:</strong> {itens.length} produtos
            </p>
            <div className="form-group">
              <label>Desconto Geral (%)</label>
              <input
                type="number"
                min="0"
                max="100"
                value={descontoGeral}
                onChange={(e) => setDescontoGeral(parseFloat(e.target.value) || 0)}
              />
            </div>
            <div className="form-group">
              <label>Observações</label>
              <textarea
                value={observacoes}
                onChange={(e) => setObservacoes(e.target.value)}
                rows={4}
              />
            </div>
            <div className="total-final">
              <strong>TOTAL: R$ {calcularTotal().toFixed(2)}</strong>
            </div>
          </div>
          <div className="step-actions">
            <button onClick={() => setStep(2)}>← Voltar</button>
            <button
              onClick={handleFinalizar}
              disabled={createMutation.isPending}
              className="btn-primary"
            >
              {createMutation.isPending ? "Salvando..." : "Salvar Cotação"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
