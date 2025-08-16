import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { SignupForm } from "@/components/auth/signup-form"

export default function SignupPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-md mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-8">
            <h1 className="font-space-grotesk font-bold text-3xl text-foreground mb-2">Create Your Account</h1>
            <p className="text-muted-foreground">
              Join thousands of professionals advancing their careers with AI-powered insights.
            </p>
          </div>
          <SignupForm />
        </div>
      </main>
      <Footer />
    </div>
  )
}
