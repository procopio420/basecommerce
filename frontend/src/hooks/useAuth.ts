import { useState, useEffect } from "react";
import api from "../services/api";

interface User {
  id: string;
  nome: string;
  email: string;
  tenant_id: string;
}

interface LoginData {
  email: string;
  password: string;
  tenant_id?: string;
}

export function useAuth() {
  const [isAuthenticated, setIsAuthenticated] = useState<boolean>(false);
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (token) {
      setIsAuthenticated(true);
      // Aqui você poderia buscar dados do usuário
    }
    setLoading(false);
  }, []);

  const login = async (data: LoginData) => {
    try {
      const response = await api.post("/auth/login", data);
      const { access_token } = response.data;
      localStorage.setItem("token", access_token);
      setIsAuthenticated(true);
      return { success: true };
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || "Erro ao fazer login",
      };
    }
  };

  const logout = () => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    setUser(null);
  };

  return {
    isAuthenticated,
    user,
    loading,
    login,
    logout,
  };
}
