import { authLogin, authMe } from "@/lib/api";
import type { User } from "@/types";

export interface LoginResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export const authService = {
  login: authLogin,
  me: authMe,
  logout(): void {
    if (typeof window !== "undefined") {
      localStorage.removeItem("nextgic_token");
    }
  },
};
