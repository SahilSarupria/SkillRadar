import Link from "next/link"
import { Button } from "@/components/ui/button"
import { FileText } from "lucide-react"

export default function Navbar() {
  return (
    <nav className="border-b bg-white/95 backdrop-blur supports-[backdrop-filter]:bg-white/60">
      <div className="container mx-auto px-4 h-16 flex items-center justify-between">
        <Link href="/" className="flex items-center space-x-2">
          <FileText className="h-6 w-6 text-blue-600" />
          <span className="font-bold text-xl">ResumeAI</span>
        </Link>

        <div className="hidden md:flex items-center space-x-6">
          <Link href="/templates" className="text-gray-600 hover:text-gray-900">
            Templates
          </Link>
          <Link href="/editor" className="text-gray-600 hover:text-gray-900">
            Editor
          </Link>
        </div>

        <div className="flex items-center space-x-4">
          <Link href="/editor">
            <Button>Get Started</Button>
          </Link>
        </div>
      </div>
    </nav>
  )
}
