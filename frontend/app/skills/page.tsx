import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { SkillGapAnalyzer } from "@/components/skill-gap-analyzer"
import { SkillsTimeline } from "@/components/skills-timeline"

export default function SkillsPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="font-space-grotesk font-bold text-3xl lg:text-4xl text-foreground mb-4">
              Skills Analysis & Timeline
            </h1>
            <p className="text-xl text-muted-foreground max-w-3xl mx-auto">
              Track your skill development journey, identify gaps, and discover career path opportunities with our
              comprehensive skills analysis tools.
            </p>
          </div>

          <div className="mb-12">
            <SkillsTimeline />
          </div>

          <SkillGapAnalyzer />
        </div>
      </main>
      <Footer />
    </div>
  )
}
