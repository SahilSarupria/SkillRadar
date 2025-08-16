import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { UserSettings } from "@/components/auth/user-settings"

export default function SettingsPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="mb-8">
            <h1 className="font-space-grotesk font-bold text-3xl text-foreground mb-2">Account Settings</h1>
            <p className="text-muted-foreground">Manage your account preferences and security settings.</p>
          </div>
          <UserSettings />
        </div>
      </main>
      <Footer />
    </div>
  )
}
