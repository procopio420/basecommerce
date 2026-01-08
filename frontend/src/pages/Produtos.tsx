import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import "./Produtos.css";

interface Produto {
  id: string;
  nome: string;
  codigo?: string;
  preco_base: number;
  unidade: string;
}

export default function Produtos() {
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery<Produto[]>({
    queryKey: ["produtos", search],
    queryFn: async () => {
      const response = await api.get("/produtos/", {
        params: { search: search || undefined, ativo: true },
      });
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="produtos-page">
      <div className="page-header">
        <h2>Produtos</h2>
        <button className="btn-primary">+ Novo Produto</button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Buscar por nome ou código..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="produtos-table">
        <table>
          <thead>
            <tr>
              <th>Código</th>
              <th>Nome</th>
              <th>Unidade</th>
              <th>Preço Base</th>
            </tr>
          </thead>
          <tbody>
            {data && data.length > 0 ? (
              data.map((produto) => (
                <tr key={produto.id}>
                  <td>{produto.codigo || "-"}</td>
                  <td>{produto.nome}</td>
                  <td>{produto.unidade}</td>
                  <td>R$ {Number(produto.preco_base).toFixed(2)}</td>
                </tr>
              ))
            ) : (
              <tr>
                <td colSpan={4} className="empty-state">
                  Nenhum produto encontrado
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
