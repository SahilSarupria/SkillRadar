"use client"

import { createContext, useContext, useEffect, useState } from "react"

interface AuthContextType {
  isAuthenticated: boolean
  user: any
  login: (token: string, user: any) => void
  logout: () => void
  loading: boolean
}

const AuthContext = createContext<AuthContextType>({
  isAuthenticated: false,
  user: null,
  login: () => {},
  logout: () => {},
  loading: true,
})

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false)
  const [user, setUser] = useState<any>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("access") : null
    if (token) {
      setIsAuthenticated(true)
      // Optionally fetch user profile here and setUser
    }
    setLoading(false)
  }, [])

  const login = (token: string, user: any) => {
    localStorage.setItem("access", token)
    setIsAuthenticated(true)
    setUser(user)
  }

  const logout = () => {
    localStorage.removeItem("access")
    setIsAuthenticated(false)
    setUser(null)
    window.location.href = "/"
  }

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, loading }}>
      {!loading && children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}