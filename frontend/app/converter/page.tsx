import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { TextConverter } from "@/components/text-converter"

export default function ConverterPage() {
  return (
    <div className="min-h-screen">
      <Navigation />
      <main className="py-12">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h1 className="font-space-grotesk font-bold text-3xl lg:text-4xl text-foreground mb-4">
              Text to Resume Converter
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Transform your unstructured text into a professional resume format with AI-powered formatting and
              optimization.
            </p>
          </div>
          <TextConverter />
        </div>
      </main>
      <Footer />
    </div>
  )
}
