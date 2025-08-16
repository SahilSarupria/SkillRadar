import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import Navbar from "@/components/Navbar"
import Footer from "@/components/Footer"
import { FileText, Palette, Download, Sparkles } from "lucide-react"

export default function HomePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <Navbar />

      {/* Hero Section */}
      <section className="container mx-auto px-4 py-20">
        <div className="text-center max-w-4xl mx-auto">
          <h1 className="text-5xl font-bold text-gray-900 mb-6">
            Build Your Perfect Resume with <span className="text-blue-600">AI Power</span>
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Create professional, ATS-friendly resumes in minutes. Choose from beautiful templates, customize with ease,
            and let AI optimize your content.
          </p>
          <div className="flex gap-4 justify-center">
            <Link href="/editor">
              <Button size="lg" className="px-8 py-3">
                <Sparkles className="mr-2 h-5 w-5" />
                Start Building
              </Button>
            </Link>
            <Link href="/templates">
              <Button variant="outline" size="lg" className="px-8 py-3 bg-transparent">
                View Templates
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="container mx-auto px-4 py-16">
        <div className="grid md:grid-cols-3 gap-8">
          <Card>
            <CardHeader>
              <FileText className="h-10 w-10 text-blue-600 mb-2" />
              <CardTitle>Professional Templates</CardTitle>
              <CardDescription>Choose from dozens of professionally designed templates</CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Palette className="h-10 w-10 text-blue-600 mb-2" />
              <CardTitle>Easy Customization</CardTitle>
              <CardDescription>Customize colors, fonts, and layouts with our intuitive editor</CardDescription>
            </CardHeader>
          </Card>

          <Card>
            <CardHeader>
              <Download className="h-10 w-10 text-blue-600 mb-2" />
              <CardTitle>Export & Share</CardTitle>
              <CardDescription>Download as PDF or share your resume link instantly</CardDescription>
            </CardHeader>
          </Card>
        </div>
      </section>

      <Footer />
    </div>
  )
}
