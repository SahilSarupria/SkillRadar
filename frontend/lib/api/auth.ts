const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export async function forgotPassword(email: string) {
  const res = await fetch(
    `${API_BASE}/api/auth/password-reset/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email }),
    }
  )
  if (!res.ok) {
    throw new Error("Failed to send reset email")
  }
  return res.json()
}

export async function login(email: string, password: string) {
  const res = await fetch(
    `${API_BASE}/api/auth/login/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email, password }),
    }
  )
  if (!res.ok) {
    throw new Error("Failed to log in")
  }
  return res.json()
}

// Add extra fields if your backend requires them (e.g., username, re_password)
export async function register(
  email: string,
  password: string,
  password_confirm: string,
  first_name: string,
  last_name: string
) {
  const body = { email, password, password_confirm, first_name, last_name }
  const res = await fetch(
    `${API_BASE}/api/auth/register/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    }
  )
  if (!res.ok) {
    throw new Error("Failed to register")
  }
  return res.json()
}

// Reset password confirm: expects uid, token, new_password, re_new_password
export async function resetPasswordConfirm(
  uid: string,
  token: string,
  new_password: string,
  re_new_password: string
) {
  const res = await fetch(
    `${API_BASE}/api/auth/password-reset-confirm/${uid}/${token}/`,
    {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ new_password, re_new_password }),
    }
  )
  if (!res.ok) {
    throw new Error("Failed to reset password")
  }
  return res.json()
}