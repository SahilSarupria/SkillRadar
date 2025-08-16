import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { UserDashboard } from "@/components/user-dashboard"

export default function DashboardPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-8">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="font-space-grotesk font-bold text-3xl lg:text-4xl text-foreground mb-2">Your Dashboard</h1>
            <p className="text-lg text-muted-foreground">
              Track your progress, view your history, and manage your career development journey.
            </p>
          </div>
          <UserDashboard />
        </div>
      </main>
      <Footer />
    </div>
  )
}
