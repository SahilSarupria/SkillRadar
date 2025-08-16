// API utilities for communicating with Django backend
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api"

export interface APIResponse<T> {
  data: T
  message?: string
  error?: string
}

export async function apiRequest<T>(endpoint: string, options: RequestInit = {}): Promise<APIResponse<T>> {
  try {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      headers: {
        "Content-Type": "application/json",
        ...options.headers,
      },
      ...options,
    })

    const data = await response.json()

    if (!response.ok) {
      throw new Error(data.message || "API request failed")
    }

    return { data }
  } catch (error) {
    console.error("API Error:", error)
    return {
      data: null as T,
      error: error instanceof Error ? error.message : "Unknown error",
    }
  }
}

// Resume-specific API functions
export async function saveResume(resumeData: any) {
  return apiRequest("/resumes/", {
    method: "POST",
    body: JSON.stringify(resumeData),
  })
}

export async function getResume(id: string) {
  return apiRequest(`/resumes/${id}/`)
}

export async function updateResume(id: string, resumeData: any) {
  return apiRequest(`/resumes/${id}/`, {
    method: "PUT",
    body: JSON.stringify(resumeData),
  })
}

export async function generateAIContent(prompt: string, section: string) {
  return apiRequest("/ai/generate/", {
    method: "POST",
    body: JSON.stringify({ prompt, section }),
  })
}
