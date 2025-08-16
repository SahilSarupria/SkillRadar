"use client"

import { useState } from "react"
import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Menu, X, Brain, FileText, BarChart3, BookOpen, User, Settings, Wand2 } from "lucide-react"

export function Navigation() {
  const [isMenuOpen, setIsMenuOpen] = useState(false)

  return (
    <nav className="bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60 sticky top-0 z-50 border-b border-border">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          {/* Logo */}
          <Link href="/" className="flex items-center space-x-2">
            <div className="bg-primary rounded-lg p-2">
              <Brain className="h-6 w-6 text-primary-foreground" />
            </div>
            <span className="font-space-grotesk font-bold text-xl text-foreground">ResumeAI</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hidden md:flex items-center space-x-8">
            <Link
              href="/analyzer"
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
            >
              <FileText className="h-4 w-4" />
              <span>Resume Analyzer</span>
            </Link>
            <Link
              href="/converter"
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
            >
              <Wand2 className="h-4 w-4" />
              <span>AI Builder</span>
            </Link>
            <Link
              href="/skills"
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
            >
              <BarChart3 className="h-4 w-4" />
              <span>Skill Analysis</span>
            </Link>
            <Link
              href="/learning"
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
            >
              <BookOpen className="h-4 w-4" />
              <span>Learning</span>
            </Link>
            <Link
              href="/dashboard"
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
            >
              <User className="h-4 w-4" />
              <span>Dashboard</span>
            </Link>
            <Link
              href="/settings"
              className="text-muted-foreground hover:text-foreground transition-colors flex items-center space-x-1"
            >
              <Settings className="h-4 w-4" />
              <span>Settings</span>
            </Link>
          </div>

          {/* Desktop CTA */}
          <div className="hidden md:flex items-center space-x-4">
            <Button variant="ghost" asChild>
              <Link href="/login">Sign In</Link>
            </Button>
            <Button asChild>
              <Link href="/signup">Get Started</Link>
            </Button>
          </div>

          {/* Mobile menu button */}
          <button
            onClick={() => setIsMenuOpen(!isMenuOpen)}
            className="md:hidden p-2 rounded-md text-muted-foreground hover:text-foreground hover:bg-accent"
          >
            {isMenuOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>

        {/* Mobile Navigation */}
        {isMenuOpen && (
          <div className="md:hidden py-4 space-y-4">
            <Link href="/analyzer" className="block text-muted-foreground hover:text-foreground transition-colors">
              Resume Analyzer
            </Link>
            <Link href="/converter" className="block text-muted-foreground hover:text-foreground transition-colors">
              AI Builder
            </Link>
            <Link href="/skills" className="block text-muted-foreground hover:text-foreground transition-colors">
              Skill Analysis
            </Link>
            <Link href="/learning" className="block text-muted-foreground hover:text-foreground transition-colors">
              Learning
            </Link>
            <Link href="/dashboard" className="block text-muted-foreground hover:text-foreground transition-colors">
              Dashboard
            </Link>
            <Link href="/settings" className="block text-muted-foreground hover:text-foreground transition-colors">
              Settings
            </Link>
            <div className="pt-4 space-y-2">
              <Button variant="ghost" className="w-full" asChild>
                <Link href="/login">Sign In</Link>
              </Button>
              <Button className="w-full" asChild>
                <Link href="/signup">Get Started</Link>
              </Button>
            </div>
          </div>
        )}
      </div>
    </nav>
  )
}
