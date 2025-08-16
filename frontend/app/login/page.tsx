import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { LoginForm } from "@/components/auth/login-form"

export default function LoginPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="font-space-grotesk font-bold text-3xl text-foreground mb-2">Welcome Back</h1>
            <p className="text-muted-foreground">Sign in to your ResumeAI account to continue your career journey.</p>
          </div>
          <LoginForm />
        </div>
      </main>
      <Footer />
    </div>
  )
}
