import { useState } from "react";
import { useQuery } from "@tanstack/react-query";
import api from "../services/api";
import "./Clientes.css";

interface Cliente {
  id: string;
  nome: string;
  documento: string;
  email?: string;
  telefone?: string;
}

export default function Clientes() {
  const [search, setSearch] = useState("");

  const { data, isLoading } = useQuery<Cliente[]>({
    queryKey: ["clientes", search],
    queryFn: async () => {
      const response = await api.get("/clientes/", {
        params: { search: search || undefined },
      });
      return response.data;
    },
  });

  if (isLoading) {
    return <div className="loading">Carregando...</div>;
  }

  return (
    <div className="clientes-page">
      <div className="page-header">
        <h2>Clientes</h2>
        <button className="btn-primary">+ Novo Cliente</button>
      </div>

      <div className="search-bar">
        <input
          type="text"
          placeholder="Buscar por nome, documento ou email..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
      </div>

      <div className="clientes-grid">
        {data && data.length > 0 ? (
          data.map((cliente) => (
            <div key={cliente.id} className="cliente-card">
              <h3>{cliente.nome}</h3>
              <p>
                <strong>Documento:</strong> {cliente.documento}
              </p>
              {cliente.email && (
                <p>
                  <strong>Email:</strong> {cliente.email}
                </p>
              )}
              {cliente.telefone && (
                <p>
                  <strong>Telefone:</strong> {cliente.telefone}
                </p>
              )}
            </div>
          ))
        ) : (
          <p className="empty-state">Nenhum cliente encontrado</p>
        )}
      </div>
    </div>
  );
}
