import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import Navbar from "@/components/Navbar"
import Footer from "@/components/Footer"
import Link from "next/link"

const templates = [
  {
    id: "modern",
    name: "Modern Professional",
    description: "Clean, contemporary design perfect for tech and creative roles",
    image: "/modern-resume-template.png",
  },
  {
    id: "creative",
    name: "Creative Designer",
    description: "Artistic layout with gradient backgrounds for creative professionals",
    image: "/creative-resume-template.png",
  },
  {
    id: "professional",
    name: "Corporate Professional",
    description: "Traditional business style ideal for corporate environments",
    image: "/professional-resume-template.png",
  },
  {
    id: "minimal",
    name: "Minimal Clean",
    description: "Simple and elegant design that focuses on content",
    image: "/minimal-resume-template.png",
  },
]

export default function TemplatesPage() {
  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="container mx-auto px-4 py-12">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Choose Your Perfect Template</h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Select from our professionally designed resume templates. Each template is fully customizable and
            ATS-friendly.
          </p>
        </div>

        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-8">
          {templates.map((template) => (
            <Card key={template.id} className="overflow-hidden hover:shadow-lg transition-shadow">
              <div className="aspect-[3/4] bg-gray-100">
                <img
                  src={template.image || "/placeholder.svg"}
                  alt={template.name}
                  className="w-full h-full object-cover"
                />
              </div>
              <CardHeader>
                <CardTitle className="text-lg">{template.name}</CardTitle>
                <CardDescription>{template.description}</CardDescription>
              </CardHeader>
              <CardContent>
                <Link href={`/editor?template=${template.id}`}>
                  <Button className="w-full">Use This Template</Button>
                </Link>
              </CardContent>
            </Card>
          ))}
        </div>
      </div>

      <Footer />
    </div>
  )
}
