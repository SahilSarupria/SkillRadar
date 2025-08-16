import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { LearningPlatforms } from "@/components/learning-platforms"

export default function LearningPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="font-space-grotesk font-bold text-3xl lg:text-4xl text-foreground mb-4">
              Learning Recommendations
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Discover personalized courses and learning paths from top platforms to close your skill gaps and advance
              your career.
            </p>
          </div>
          <LearningPlatforms />
        </div>
      </main>
      <Footer />
    </div>
  )
}
