import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { ResumeUpload } from "@/components/resume-upload"

export default function AnalyzerPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="font-space-grotesk font-bold text-3xl lg:text-4xl text-foreground mb-4">Resume Analyzer</h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Upload your resume and get instant AI-powered analysis with actionable insights to improve your career
              prospects.
            </p>
          </div>
          <ResumeUpload />
        </div>
      </main>
      <Footer />
    </div>
  )
}
