import { Button } from "@/components/ui/button"
import { ArrowRight, Upload, BarChart3, Target, BookOpen } from "lucide-react"
import Link from "next/link"

export function HeroSection() {
  return (
    <section className="relative py-20 lg:py-32 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center">
          <h1 className="font-space-grotesk font-bold text-4xl sm:text-5xl lg:text-6xl text-foreground mb-6">
            Transform Your Career with <span className="text-primary">AI-Powered</span> Resume Analysis
          </h1>
          <p className="text-xl text-muted-foreground mb-8 max-w-3xl mx-auto leading-relaxed">
            Get instant insights into your resume, identify skill gaps, and receive personalized learning
            recommendations to accelerate your career growth.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16">
            <Button size="lg" className="text-lg px-8" asChild>
              <Link href="/analyzer">
                Analyze My Resume
                <ArrowRight className="ml-2 h-5 w-5" />
              </Link>
            </Button>
            <Button size="lg" variant="outline" className="text-lg px-8 bg-transparent" asChild>
              <Link href="/converter">Try Text Converter</Link>
            </Button>
          </div>

          {/* Feature Cards */}
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 mt-16">
            <div className="bg-card rounded-lg p-6 text-center border border-border">
              <div className="bg-primary/10 rounded-lg p-3 w-fit mx-auto mb-4">
                <Upload className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-space-grotesk font-semibold text-lg mb-2">Smart Upload</h3>
              <p className="text-muted-foreground text-sm">
                Upload your resume or convert text to professional format instantly
              </p>
            </div>
            <div className="bg-card rounded-lg p-6 text-center border border-border">
              <div className="bg-primary/10 rounded-lg p-3 w-fit mx-auto mb-4">
                <BarChart3 className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-space-grotesk font-semibold text-lg mb-2">AI Analysis</h3>
              <p className="text-muted-foreground text-sm">
                Get detailed insights on content, formatting, and optimization opportunities
              </p>
            </div>
            <div className="bg-card rounded-lg p-6 text-center border border-border">
              <div className="bg-primary/10 rounded-lg p-3 w-fit mx-auto mb-4">
                <Target className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-space-grotesk font-semibold text-lg mb-2">Skill Gaps</h3>
              <p className="text-muted-foreground text-sm">
                Identify missing skills for your target roles and career goals
              </p>
            </div>
            <div className="bg-card rounded-lg p-6 text-center border border-border">
              <div className="bg-primary/10 rounded-lg p-3 w-fit mx-auto mb-4">
                <BookOpen className="h-6 w-6 text-primary" />
              </div>
              <h3 className="font-space-grotesk font-semibold text-lg mb-2">Learn & Grow</h3>
              <p className="text-muted-foreground text-sm">
                Get personalized course recommendations from top platforms
              </p>
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
