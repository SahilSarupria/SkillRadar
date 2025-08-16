"use client"

import type React from "react"
import { useState, useRef, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { Badge } from "@/components/ui/badge"
import { Separator } from "@/components/ui/separator"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Input } from "@/components/ui/input"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  Wand2,
  Download,
  Copy,
  CheckCircle,
  Upload,
  Trash2,
  Plus,
  Edit3,
  RotateCcw,
  RotateCw,
  Grid3X3,
  AlignLeft,
  AlignCenter,
  AlignRight,
  FileText,
  User,
  Briefcase,
  GraduationCap,
  Award,
  Code,
  Phone,
  Globe,
  ChevronLeft,
  ChevronRight,
  Maximize2,
} from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface ResumeSection {
  id: string
  type:
    | "header"
    | "contact"
    | "summary"
    | "experience"
    | "education"
    | "skills"
    | "projects"
    | "certifications"
    | "custom"
  title: string
  content: string
  position: { x: number; y: number }
  size: { width: number; height: number }
  style: {
    fontSize: string
    fontWeight: string
    color: string
    backgroundColor: string
    padding: string
    borderRadius: string
    textAlign: "left" | "center" | "right"
    borderWidth: string
    borderColor: string
  }
  page: number
}

interface DragState {
  isDragging: boolean
  dragOffset: { x: number; y: number }
  isResizing: boolean
  resizeHandle: string | null
}

const CANVAS_WIDTH = 794 // A4 width in pixels at 96 DPI
const CANVAS_HEIGHT = 1123 // A4 height in pixels at 96 DPI
const GRID_SIZE = 10
const MIN_SECTION_WIDTH = 100
const MIN_SECTION_HEIGHT = 40

export function TextConverter() {
  const [inputText, setInputText] = useState("")
  const [convertedResume, setConvertedResume] = useState("")
  const [isConverting, setIsConverting] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showBuilder, setShowBuilder] = useState(false)
  const [resumeSections, setResumeSections] = useState<ResumeSection[]>([])
  const [selectedSection, setSelectedSection] = useState<string | null>(null)
  const [dragState, setDragState] = useState<DragState>({
    isDragging: false,
    dragOffset: { x: 0, y: 0 },
    isResizing: false,
    resizeHandle: null,
  })
  const [currentPage, setCurrentPage] = useState(1)
  const [totalPages, setTotalPages] = useState(1)
  const [showGrid, setShowGrid] = useState(true)
  const [snapToGrid, setSnapToGrid] = useState(true)
  const [history, setHistory] = useState<ResumeSection[][]>([])
  const [historyIndex, setHistoryIndex] = useState(-1)
  const canvasRef = useRef<HTMLDivElement>(null)
  const { toast } = useToast()

  const componentTemplates = {
    header: {
      title: "Header",
      icon: User,
      content: "JOHN DOE\nSoftware Engineer",
      style: { fontSize: "24px", fontWeight: "bold", textAlign: "center" as const },
    },
    contact: {
      title: "Contact Info",
      icon: Phone,
      content: "📧 john.doe@email.com\n📱 (555) 123-4567\n📍 San Francisco, CA\n🌐 linkedin.com/in/johndoe",
      style: { fontSize: "12px", fontWeight: "normal", textAlign: "left" as const },
    },
    summary: {
      title: "Professional Summary",
      icon: FileText,
      content:
        "Experienced software engineer with 5+ years of expertise in full-stack development, specializing in React, Node.js, and cloud technologies.",
      style: { fontSize: "14px", fontWeight: "normal", textAlign: "left" as const },
    },
    experience: {
      title: "Work Experience",
      icon: Briefcase,
      content:
        "Senior Software Engineer | TechCorp Inc. | 2021 - Present\n• Led development of customer-facing web applications\n• Implemented microservices architecture\n• Mentored junior developers",
      style: { fontSize: "14px", fontWeight: "normal", textAlign: "left" as const },
    },
    education: {
      title: "Education",
      icon: GraduationCap,
      content: "Bachelor of Science in Computer Science\nUniversity of California, Berkeley | 2019\nGPA: 3.8/4.0",
      style: { fontSize: "14px", fontWeight: "normal", textAlign: "left" as const },
    },
    skills: {
      title: "Technical Skills",
      icon: Code,
      content:
        "• Programming: JavaScript, TypeScript, Python, Java\n• Frontend: React, Next.js, Vue.js, HTML5, CSS3\n• Backend: Node.js, Express.js, Django, REST APIs\n• Cloud: AWS, Docker, Kubernetes",
      style: { fontSize: "14px", fontWeight: "normal", textAlign: "left" as const },
    },
    projects: {
      title: "Projects",
      icon: Globe,
      content:
        "E-Commerce Platform | 2023\n• Built full-stack application with React and Node.js\n• Integrated payment processing and inventory management\n• Deployed on AWS with CI/CD pipeline",
      style: { fontSize: "14px", fontWeight: "normal", textAlign: "left" as const },
    },
    certifications: {
      title: "Certifications",
      icon: Award,
      content:
        "• AWS Certified Solutions Architect - Associate (2023)\n• Google Cloud Professional Developer (2022)\n• Certified Kubernetes Administrator (2022)",
      style: { fontSize: "14px", fontWeight: "normal", textAlign: "left" as const },
    },
  }

  const checkCollision = useCallback(
    (newSection: ResumeSection, excludeId?: string): boolean => {
      return resumeSections.some((section) => {
        if (section.id === excludeId || section.page !== newSection.page) return false

        const rect1 = {
          left: newSection.position.x,
          right: newSection.position.x + newSection.size.width,
          top: newSection.position.y,
          bottom: newSection.position.y + newSection.size.height,
        }

        const rect2 = {
          left: section.position.x,
          right: section.position.x + section.size.width,
          top: section.position.y,
          bottom: section.position.y + section.size.height,
        }

        return !(
          rect1.right <= rect2.left ||
          rect1.left >= rect2.right ||
          rect1.bottom <= rect2.top ||
          rect1.top >= rect2.bottom
        )
      })
    },
    [resumeSections],
  )

  const snapToGridFn = useCallback(
    (value: number): number => {
      if (!snapToGrid) return value
      return Math.round(value / GRID_SIZE) * GRID_SIZE
    },
    [snapToGrid],
  )

  const constrainToBounds = useCallback(
    (section: ResumeSection): ResumeSection => {
      const maxX = CANVAS_WIDTH - section.size.width
      const maxY = CANVAS_HEIGHT - section.size.height

      return {
        ...section,
        position: {
          x: Math.max(0, Math.min(maxX, snapToGridFn(section.position.x))),
          y: Math.max(0, Math.min(maxY, snapToGridFn(section.position.y))),
        },
        size: {
          width: Math.max(MIN_SECTION_WIDTH, Math.min(CANVAS_WIDTH, section.size.width)),
          height: Math.max(MIN_SECTION_HEIGHT, Math.min(CANVAS_HEIGHT, section.size.height)),
        },
      }
    },
    [snapToGridFn],
  )

  const saveToHistory = useCallback(() => {
    const newHistory = history.slice(0, historyIndex + 1)
    newHistory.push([...resumeSections])
    setHistory(newHistory)
    setHistoryIndex(newHistory.length - 1)
  }, [history, historyIndex, resumeSections])

  const undo = useCallback(() => {
    if (historyIndex > 0) {
      setHistoryIndex(historyIndex - 1)
      setResumeSections(history[historyIndex - 1])
    }
  }, [history, historyIndex])

  const redo = useCallback(() => {
    if (historyIndex < history.length - 1) {
      setHistoryIndex(historyIndex + 1)
      setResumeSections(history[historyIndex + 1])
    }
  }, [history, historyIndex])

  const handleConvert = async () => {
    if (!inputText.trim()) {
      toast({
        title: "Please enter some text",
        description: "Add your career information to convert into a resume format.",
        variant: "destructive",
      })
      return
    }

    setIsConverting(true)
    await new Promise((resolve) => setTimeout(resolve, 2000))

    const mockResume = `JOHN DOE
Software Engineer
Email: john.doe@email.com | Phone: (555) 123-4567
LinkedIn: linkedin.com/in/johndoe | Location: San Francisco, CA

PROFESSIONAL SUMMARY
Experienced software engineer with 5+ years of expertise in full-stack development, specializing in React, Node.js, and cloud technologies. Proven track record of delivering scalable applications and leading cross-functional teams to achieve business objectives.

TECHNICAL SKILLS
• Programming Languages: JavaScript, TypeScript, Python, Java
• Frontend: React, Next.js, Vue.js, HTML5, CSS3, Tailwind CSS
• Backend: Node.js, Express.js, Django, REST APIs, GraphQL
• Databases: PostgreSQL, MongoDB, Redis
• Cloud & DevOps: AWS, Docker, Kubernetes, CI/CD

PROFESSIONAL EXPERIENCE

Senior Software Engineer | TechCorp Inc. | 2021 - Present
• Led development of customer-facing web applications serving 100K+ users
• Implemented microservices architecture reducing system latency by 40%
• Mentored junior developers and established coding best practices
• Collaborated with product teams to deliver features ahead of schedule

Software Engineer | StartupXYZ | 2019 - 2021
• Built responsive web applications using React and Node.js
• Developed RESTful APIs and integrated third-party services
• Optimized database queries improving application performance by 30%
• Participated in agile development processes and code reviews

EDUCATION
Bachelor of Science in Computer Science
University of California, Berkeley | 2019

CERTIFICATIONS
• AWS Certified Solutions Architect
• Google Cloud Professional Developer`

    setConvertedResume(mockResume)

    const sections: ResumeSection[] = [
      {
        id: "header",
        type: "header",
        title: "Header",
        content: "JOHN DOE\nSoftware Engineer",
        position: { x: 50, y: 50 },
        size: { width: 694, height: 80 },
        style: {
          fontSize: "24px",
          fontWeight: "bold",
          color: "#1f2937",
          backgroundColor: "#f8fafc",
          padding: "20px",
          borderRadius: "8px",
          textAlign: "center",
          borderWidth: "0px",
          borderColor: "#e5e7eb",
        },
        page: 1,
      },
      {
        id: "contact",
        type: "contact",
        title: "Contact Info",
        content: "📧 john.doe@email.com\n📱 (555) 123-4567\n📍 San Francisco, CA\n🌐 linkedin.com/in/johndoe",
        position: { x: 50, y: 150 },
        size: { width: 300, height: 100 },
        style: {
          fontSize: "12px",
          fontWeight: "normal",
          color: "#374151",
          backgroundColor: "#ffffff",
          padding: "16px",
          borderRadius: "6px",
          textAlign: "left",
          borderWidth: "1px",
          borderColor: "#e5e7eb",
        },
        page: 1,
      },
      {
        id: "summary",
        type: "summary",
        title: "Professional Summary",
        content:
          "Experienced software engineer with 5+ years of expertise in full-stack development, specializing in React, Node.js, and cloud technologies.",
        position: { x: 370, y: 150 },
        size: { width: 374, height: 100 },
        style: {
          fontSize: "14px",
          fontWeight: "normal",
          color: "#374151",
          backgroundColor: "#ffffff",
          padding: "16px",
          borderRadius: "6px",
          textAlign: "left",
          borderWidth: "1px",
          borderColor: "#e5e7eb",
        },
        page: 1,
      },
      {
        id: "skills",
        type: "skills",
        title: "Technical Skills",
        content:
          "• Programming: JavaScript, TypeScript, Python, Java\n• Frontend: React, Next.js, Vue.js, HTML5, CSS3\n• Backend: Node.js, Express.js, Django, REST APIs\n• Cloud: AWS, Docker, Kubernetes",
        position: { x: 50, y: 270 },
        size: { width: 694, height: 120 },
        style: {
          fontSize: "14px",
          fontWeight: "normal",
          color: "#374151",
          backgroundColor: "#ffffff",
          padding: "16px",
          borderRadius: "6px",
          textAlign: "left",
          borderWidth: "1px",
          borderColor: "#e5e7eb",
        },
        page: 1,
      },
      {
        id: "experience",
        type: "experience",
        title: "Work Experience",
        content:
          "Senior Software Engineer | TechCorp Inc. | 2021 - Present\n• Led development of customer-facing web applications\n• Implemented microservices architecture\n• Mentored junior developers",
        position: { x: 50, y: 410 },
        size: { width: 694, height: 150 },
        style: {
          fontSize: "14px",
          fontWeight: "normal",
          color: "#374151",
          backgroundColor: "#ffffff",
          padding: "16px",
          borderRadius: "6px",
          textAlign: "left",
          borderWidth: "1px",
          borderColor: "#e5e7eb",
        },
        page: 1,
      },
    ]

    setResumeSections(sections)
    setTotalPages(1)
    setCurrentPage(1)
    setHistory([sections])
    setHistoryIndex(0)
    setIsConverting(false)
    setShowBuilder(true)

    toast({
      title: "Resume converted successfully!",
      description: "Now customize your resume with the advanced visual builder.",
    })
  }

  const handleSectionUpdate = useCallback(
    (sectionId: string, updates: Partial<ResumeSection>) => {
      setResumeSections((sections) => {
        const updatedSections = sections.map((section) => {
          if (section.id === sectionId) {
            const updatedSection = { ...section, ...updates }

            // Apply constraints and collision detection for position/size changes
            if (updates.position || updates.size) {
              const constrainedSection = constrainToBounds(updatedSection)

              // Check for collisions if not dragging
              if (!dragState.isDragging && checkCollision(constrainedSection, sectionId)) {
                return section // Revert if collision detected
              }

              return constrainedSection
            }

            return updatedSection
          }
          return section
        })

        // Save to history for non-style changes
        if (updates.position || updates.size || updates.content) {
          setTimeout(() => saveToHistory(), 100)
        }

        return updatedSections
      })
    },
    [constrainToBounds, checkCollision, dragState.isDragging, saveToHistory],
  )

  const handleAddSection = useCallback(
    (type: keyof typeof componentTemplates) => {
      const template = componentTemplates[type]
      const newSection: ResumeSection = {
        id: `${type}-${Date.now()}`,
        type,
        title: template.title,
        content: template.content,
        position: { x: 50, y: 50 + resumeSections.filter((s) => s.page === currentPage).length * 120 },
        size: { width: 400, height: 100 },
        style: {
          fontSize: template.style.fontSize,
          fontWeight: template.style.fontWeight,
          color: "#374151",
          backgroundColor: "#ffffff",
          padding: "16px",
          borderRadius: "6px",
          textAlign: template.style.textAlign,
          borderWidth: "1px",
          borderColor: "#e5e7eb",
        },
        page: currentPage,
      }

      const constrainedSection = constrainToBounds(newSection)

      // Find non-colliding position
      let attempts = 0
      while (checkCollision(constrainedSection) && attempts < 20) {
        constrainedSection.position.y += 30
        attempts++
      }

      setResumeSections((prev) => [...prev, constrainedSection])
      saveToHistory()
    },
    [currentPage, resumeSections, constrainToBounds, checkCollision, saveToHistory],
  )

  const handleCopy = async () => {
    await navigator.clipboard.writeText(convertedResume)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
    toast({
      title: "Copied to clipboard",
      description: "Resume content has been copied to your clipboard.",
    })
  }

  const handleDownload = () => {
    const blob = new Blob([convertedResume], { type: "text/plain" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "converted-resume.txt"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Resume downloaded",
      description: "Your converted resume has been saved as a text file.",
    })
  }

  const handleSectionClick = (sectionId: string) => {
    setSelectedSection(sectionId)
  }

  const handleDeleteSection = (sectionId: string) => {
    setResumeSections((sections) => sections.filter((s) => s.id !== sectionId))
    setSelectedSection(null)
    saveToHistory()
  }

  const exportTemplate = () => {
    const template = {
      sections: resumeSections,
      pages: totalPages,
      metadata: {
        name: "Custom Resume Template",
        created: new Date().toISOString(),
        version: "2.0",
      },
    }
    const blob = new Blob([JSON.stringify(template, null, 2)], { type: "application/json" })
    const url = URL.createObjectURL(blob)
    const a = document.createElement("a")
    a.href = url
    a.download = "resume-template.json"
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)

    toast({
      title: "Template exported",
      description: "Your multi-page resume template has been saved.",
    })
  }

  const importTemplate = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0]
    if (!file) return

    const reader = new FileReader()
    reader.onload = (e) => {
      try {
        const template = JSON.parse(e.target?.result as string)
        setResumeSections(template.sections)
        setTotalPages(template.pages || 1)
        setCurrentPage(1)
        setHistory([template.sections])
        setHistoryIndex(0)
        toast({
          title: "Template imported",
          description: "Your resume template has been loaded.",
        })
      } catch (error) {
        toast({
          title: "Import failed",
          description: "Invalid template file format.",
          variant: "destructive",
        })
      }
    }
    reader.readAsText(file)
  }

  const addPage = () => {
    setTotalPages((prev) => prev + 1)
    setCurrentPage(totalPages + 1)
  }

  const deletePage = () => {
    if (totalPages > 1) {
      setResumeSections((sections) => sections.filter((s) => s.page !== currentPage))
      setTotalPages((prev) => prev - 1)
      setCurrentPage(Math.min(currentPage, totalPages - 1))
      saveToHistory()
    }
  }

  const handleMouseDown = useCallback(
    (e: React.MouseEvent, sectionId: string, action: "drag" | "resize", handle?: string) => {
      e.preventDefault()
      e.stopPropagation()

      const section = resumeSections.find((s) => s.id === sectionId)
      if (!section) return

      const rect = canvasRef.current?.getBoundingClientRect()
      if (!rect) return

      const startX = e.clientX - rect.left
      const startY = e.clientY - rect.top

      setDragState({
        isDragging: action === "drag",
        isResizing: action === "resize",
        resizeHandle: handle || null,
        dragOffset: {
          x: startX - section.position.x,
          y: startY - section.position.y,
        },
      })

      setSelectedSection(sectionId)
    },
    [resumeSections],
  )

  const handleMouseMove = useCallback(
    (e: React.MouseEvent) => {
      if (!selectedSection || (!dragState.isDragging && !dragState.isResizing)) return

      const rect = canvasRef.current?.getBoundingClientRect()
      if (!rect) return

      const currentX = e.clientX - rect.left
      const currentY = e.clientY - rect.top

      const section = resumeSections.find((s) => s.id === selectedSection)
      if (!section) return

      if (dragState.isDragging) {
        const newX = currentX - dragState.dragOffset.x
        const newY = currentY - dragState.dragOffset.y

        handleSectionUpdate(selectedSection, {
          position: { x: newX, y: newY },
        })
      } else if (dragState.isResizing && dragState.resizeHandle) {
        const handle = dragState.resizeHandle
        let newWidth = section.size.width
        let newHeight = section.size.height
        let newX = section.position.x
        let newY = section.position.y

        if (handle.includes("right")) {
          newWidth = Math.max(MIN_SECTION_WIDTH, currentX - section.position.x)
        }
        if (handle.includes("bottom")) {
          newHeight = Math.max(MIN_SECTION_HEIGHT, currentY - section.position.y)
        }
        if (handle.includes("left")) {
          const deltaX = currentX - section.position.x
          newWidth = Math.max(MIN_SECTION_WIDTH, section.size.width - deltaX)
          newX = currentX
        }
        if (handle.includes("top")) {
          const deltaY = currentY - section.position.y
          newHeight = Math.max(MIN_SECTION_HEIGHT, section.size.height - deltaY)
          newY = currentY
        }

        handleSectionUpdate(selectedSection, {
          position: { x: newX, y: newY },
          size: { width: newWidth, height: newHeight },
        })
      }
    },
    [selectedSection, dragState, resumeSections, handleSectionUpdate],
  )

  const handleMouseUp = useCallback(() => {
    setDragState({
      isDragging: false,
      isResizing: false,
      resizeHandle: null,
      dragOffset: { x: 0, y: 0 },
    })
  }, [])

  if (showBuilder) {
    const currentPageSections = resumeSections.filter((s) => s.page === currentPage)

    return (
      <div className="space-y-6">
        {/* Enhanced Builder Header */}
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-space-grotesk font-bold">Advanced Resume Builder</h2>
            <p className="text-muted-foreground">Professional drag-and-drop resume editor with multi-page support</p>
          </div>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm" onClick={undo} disabled={historyIndex <= 0}>
              <RotateCcw className="h-4 w-4" />
            </Button>
            <Button variant="outline" size="sm" onClick={redo} disabled={historyIndex >= history.length - 1}>
              <RotateCw className="h-4 w-4" />
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button variant="outline" size="sm" onClick={() => setShowGrid(!showGrid)}>
              <Grid3X3 className="h-4 w-4 mr-2" />
              Grid
            </Button>
            <Button variant="outline" size="sm" onClick={() => setSnapToGrid(!snapToGrid)}>
              <Maximize2 className="h-4 w-4 mr-2" />
              Snap
            </Button>
            <Separator orientation="vertical" className="h-6" />
            <Button variant="outline" size="sm" onClick={() => setShowBuilder(false)}>
              <Edit3 className="h-4 w-4 mr-2" />
              Edit Text
            </Button>
            <Button variant="outline" size="sm" onClick={exportTemplate}>
              <Download className="h-4 w-4 mr-2" />
              Export
            </Button>
            <label>
              <Button variant="outline" size="sm" asChild>
                <span>
                  <Upload className="h-4 w-4 mr-2" />
                  Import
                </span>
              </Button>
              <input type="file" accept=".json" onChange={importTemplate} className="hidden" />
            </label>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-5 gap-6">
          {/* Enhanced Sidebar */}
          <div className="lg:col-span-1 space-y-4">
            {/* Component Library */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Components</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="grid grid-cols-2 gap-2">
                  {Object.entries(componentTemplates).map(([type, template]) => {
                    const Icon = template.icon
                    return (
                      <Button
                        key={type}
                        variant="outline"
                        size="sm"
                        onClick={() => handleAddSection(type as keyof typeof componentTemplates)}
                        className="h-auto p-2 flex flex-col items-center space-y-1"
                      >
                        <Icon className="h-4 w-4" />
                        <span className="text-xs">{template.title}</span>
                      </Button>
                    )
                  })}
                </div>
              </CardContent>
            </Card>

            {/* Page Management */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Pages</CardTitle>
              </CardHeader>
              <CardContent className="space-y-2">
                <div className="flex items-center justify-between">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                    disabled={currentPage === 1}
                  >
                    <ChevronLeft className="h-4 w-4" />
                  </Button>
                  <span className="text-sm font-medium">
                    Page {currentPage} of {totalPages}
                  </span>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                    disabled={currentPage === totalPages}
                  >
                    <ChevronRight className="h-4 w-4" />
                  </Button>
                </div>
                <div className="flex space-x-2">
                  <Button variant="outline" size="sm" onClick={addPage} className="flex-1 bg-transparent">
                    <Plus className="h-4 w-4 mr-1" />
                    Add
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={deletePage}
                    disabled={totalPages === 1}
                    className="flex-1 bg-transparent"
                  >
                    <Trash2 className="h-4 w-4 mr-1" />
                    Delete
                  </Button>
                </div>
              </CardContent>
            </Card>

            {/* Section List */}
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Current Page Sections</CardTitle>
              </CardHeader>
              <CardContent className="space-y-1">
                {currentPageSections.map((section) => (
                  <div
                    key={section.id}
                    className={`p-2 rounded cursor-pointer text-sm transition-colors ${
                      selectedSection === section.id ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                    }`}
                    onClick={() => handleSectionClick(section.id)}
                  >
                    <div className="flex items-center justify-between">
                      <span className="truncate">{section.title}</span>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => {
                          e.stopPropagation()
                          handleDeleteSection(section.id)
                        }}
                        className="h-6 w-6 p-0 hover:bg-destructive hover:text-destructive-foreground"
                      >
                        <Trash2 className="h-3 w-3" />
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>

            {/* Enhanced Style Panel */}
            {selectedSection && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-sm">Style Options</CardTitle>
                </CardHeader>
                <CardContent>
                  <Tabs defaultValue="typography" className="w-full">
                    <TabsList className="grid w-full grid-cols-3">
                      <TabsTrigger value="typography">Text</TabsTrigger>
                      <TabsTrigger value="layout">Layout</TabsTrigger>
                      <TabsTrigger value="appearance">Style</TabsTrigger>
                    </TabsList>

                    <TabsContent value="typography" className="space-y-4">
                      <div className="space-y-2">
                        <Label>Font Size</Label>
                        <Select
                          value={resumeSections.find((s) => s.id === selectedSection)?.style.fontSize}
                          onValueChange={(value) =>
                            handleSectionUpdate(selectedSection, {
                              style: {
                                ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                fontSize: value,
                              },
                            })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="10px">Extra Small</SelectItem>
                            <SelectItem value="12px">Small</SelectItem>
                            <SelectItem value="14px">Medium</SelectItem>
                            <SelectItem value="16px">Large</SelectItem>
                            <SelectItem value="18px">Extra Large</SelectItem>
                            <SelectItem value="24px">Heading</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Font Weight</Label>
                        <Select
                          value={resumeSections.find((s) => s.id === selectedSection)?.style.fontWeight}
                          onValueChange={(value) =>
                            handleSectionUpdate(selectedSection, {
                              style: {
                                ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                fontWeight: value,
                              },
                            })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="normal">Normal</SelectItem>
                            <SelectItem value="bold">Bold</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>

                      <div className="space-y-2">
                        <Label>Text Alignment</Label>
                        <div className="flex space-x-1">
                          {(["left", "center", "right"] as const).map((align) => (
                            <Button
                              key={align}
                              variant={
                                resumeSections.find((s) => s.id === selectedSection)?.style.textAlign === align
                                  ? "default"
                                  : "outline"
                              }
                              size="sm"
                              onClick={() =>
                                handleSectionUpdate(selectedSection, {
                                  style: {
                                    ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                    textAlign: align,
                                  },
                                })
                              }
                            >
                              {align === "left" && <AlignLeft className="h-4 w-4" />}
                              {align === "center" && <AlignCenter className="h-4 w-4" />}
                              {align === "right" && <AlignRight className="h-4 w-4" />}
                            </Button>
                          ))}
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="layout" className="space-y-4">
                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-2">
                          <Label>Width</Label>
                          <Input
                            type="number"
                            value={resumeSections.find((s) => s.id === selectedSection)?.size.width || 0}
                            onChange={(e) =>
                              handleSectionUpdate(selectedSection, {
                                size: {
                                  ...resumeSections.find((s) => s.id === selectedSection)!.size,
                                  width: Number.parseInt(e.target.value) || MIN_SECTION_WIDTH,
                                },
                              })
                            }
                            min={MIN_SECTION_WIDTH}
                            max={CANVAS_WIDTH}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Height</Label>
                          <Input
                            type="number"
                            value={resumeSections.find((s) => s.id === selectedSection)?.size.height || 0}
                            onChange={(e) =>
                              handleSectionUpdate(selectedSection, {
                                size: {
                                  ...resumeSections.find((s) => s.id === selectedSection)!.size,
                                  height: Number.parseInt(e.target.value) || MIN_SECTION_HEIGHT,
                                },
                              })
                            }
                            min={MIN_SECTION_HEIGHT}
                            max={CANVAS_HEIGHT}
                          />
                        </div>
                      </div>

                      <div className="grid grid-cols-2 gap-2">
                        <div className="space-y-2">
                          <Label>X Position</Label>
                          <Input
                            type="number"
                            value={resumeSections.find((s) => s.id === selectedSection)?.position.x || 0}
                            onChange={(e) =>
                              handleSectionUpdate(selectedSection, {
                                position: {
                                  ...resumeSections.find((s) => s.id === selectedSection)!.position,
                                  x: Number.parseInt(e.target.value) || 0,
                                },
                              })
                            }
                            min={0}
                            max={CANVAS_WIDTH}
                          />
                        </div>
                        <div className="space-y-2">
                          <Label>Y Position</Label>
                          <Input
                            type="number"
                            value={resumeSections.find((s) => s.id === selectedSection)?.position.y || 0}
                            onChange={(e) =>
                              handleSectionUpdate(selectedSection, {
                                position: {
                                  ...resumeSections.find((s) => s.id === selectedSection)!.position,
                                  y: Number.parseInt(e.target.value) || 0,
                                },
                              })
                            }
                            min={0}
                            max={CANVAS_HEIGHT}
                          />
                        </div>
                      </div>
                    </TabsContent>

                    <TabsContent value="appearance" className="space-y-4">
                      <div className="space-y-2">
                        <Label>Text Color</Label>
                        <Input
                          type="color"
                          value={resumeSections.find((s) => s.id === selectedSection)?.style.color}
                          onChange={(e) =>
                            handleSectionUpdate(selectedSection, {
                              style: {
                                ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                color: e.target.value,
                              },
                            })
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Background Color</Label>
                        <Input
                          type="color"
                          value={resumeSections.find((s) => s.id === selectedSection)?.style.backgroundColor}
                          onChange={(e) =>
                            handleSectionUpdate(selectedSection, {
                              style: {
                                ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                backgroundColor: e.target.value,
                              },
                            })
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Border Color</Label>
                        <Input
                          type="color"
                          value={resumeSections.find((s) => s.id === selectedSection)?.style.borderColor}
                          onChange={(e) =>
                            handleSectionUpdate(selectedSection, {
                              style: {
                                ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                borderColor: e.target.value,
                              },
                            })
                          }
                        />
                      </div>

                      <div className="space-y-2">
                        <Label>Border Width</Label>
                        <Select
                          value={resumeSections.find((s) => s.id === selectedSection)?.style.borderWidth}
                          onValueChange={(value) =>
                            handleSectionUpdate(selectedSection, {
                              style: {
                                ...resumeSections.find((s) => s.id === selectedSection)!.style,
                                borderWidth: value,
                              },
                            })
                          }
                        >
                          <SelectTrigger>
                            <SelectValue />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="0px">None</SelectItem>
                            <SelectItem value="1px">Thin</SelectItem>
                            <SelectItem value="2px">Medium</SelectItem>
                            <SelectItem value="3px">Thick</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                    </TabsContent>
                  </Tabs>
                </CardContent>
              </Card>
            )}
          </div>

          {/* Enhanced Canvas */}
          <div className="lg:col-span-4">
            <Card className="h-[900px]">
              <CardContent className="p-0 h-full">
                <div
                  ref={canvasRef}
                  className="relative w-full h-full bg-white overflow-auto"
                  style={{
                    backgroundImage: showGrid
                      ? `
                      linear-gradient(to right, #f0f0f0 1px, transparent 1px),
                      linear-gradient(to bottom, #f0f0f0 1px, transparent 1px)
                    `
                      : "none",
                    backgroundSize: showGrid ? `${GRID_SIZE}px ${GRID_SIZE}px` : "auto",
                  }}
                  onMouseMove={handleMouseMove}
                  onMouseUp={handleMouseUp}
                  onMouseLeave={handleMouseUp}
                >
                  {/* Canvas boundary indicator */}
                  <div
                    className="absolute border-2 border-dashed border-gray-300 pointer-events-none"
                    style={{
                      width: CANVAS_WIDTH,
                      height: CANVAS_HEIGHT,
                      left: 20,
                      top: 20,
                    }}
                  />

                  {/* Page indicator */}
                  <div className="absolute top-2 left-2 bg-black/80 text-white px-2 py-1 rounded text-xs font-medium">
                    Page {currentPage} of {totalPages}
                  </div>

                  {currentPageSections.map((section) => (
                    <div
                      key={section.id}
                      className={`absolute cursor-move border-2 transition-all select-none ${
                        selectedSection === section.id
                          ? "border-primary shadow-lg z-10"
                          : "border-transparent hover:border-muted-foreground/30"
                      }`}
                      style={{
                        left: section.position.x + 20,
                        top: section.position.y + 20,
                        width: section.size.width,
                        height: section.size.height,
                        ...section.style,
                        textAlign: section.style.textAlign,
                        border: `${section.style.borderWidth} solid ${section.style.borderColor}`,
                        userSelect: "none",
                      }}
                      onClick={() => handleSectionClick(section.id)}
                      onMouseDown={(e) => handleMouseDown(e, section.id, "drag")}
                    >
                      <div className="w-full h-full overflow-hidden pointer-events-none">
                        <div className="text-xs font-medium text-primary mb-1 opacity-60">{section.title}</div>
                        <div
                          className="text-sm whitespace-pre-wrap overflow-hidden"
                          style={{
                            fontSize: section.style.fontSize,
                            fontWeight: section.style.fontWeight,
                            color: section.style.color,
                          }}
                        >
                          {section.content}
                        </div>
                      </div>

                      {/* Resize handles */}
                      {selectedSection === section.id && (
                        <>
                          {/* Corner handles */}
                          <div
                            className="absolute -top-1 -left-1 w-3 h-3 bg-primary border border-white cursor-nw-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "top-left")}
                          />
                          <div
                            className="absolute -top-1 -right-1 w-3 h-3 bg-primary border border-white cursor-ne-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "top-right")}
                          />
                          <div
                            className="absolute -bottom-1 -left-1 w-3 h-3 bg-primary border border-white cursor-sw-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "bottom-left")}
                          />
                          <div
                            className="absolute -bottom-1 -right-1 w-3 h-3 bg-primary border border-white cursor-se-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "bottom-right")}
                          />

                          {/* Edge handles */}
                          <div
                            className="absolute -top-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-primary border border-white cursor-n-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "top")}
                          />
                          <div
                            className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 w-3 h-3 bg-primary border border-white cursor-s-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "bottom")}
                          />
                          <div
                            className="absolute -left-1 top-1/2 transform -translate-y-1/2 w-3 h-3 bg-primary border border-white cursor-w-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "left")}
                          />
                          <div
                            className="absolute -right-1 top-1/2 transform -translate-y-1/2 w-3 h-3 bg-primary border border-white cursor-e-resize"
                            onMouseDown={(e) => handleMouseDown(e, section.id, "resize", "right")}
                          />
                        </>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-8">
      {/* Input Section */}
      <Card>
        <CardHeader>
          <CardTitle className="font-space-grotesk flex items-center space-x-2">
            <Wand2 className="h-5 w-5 text-primary" />
            <span>Enter Your Career Information</span>
          </CardTitle>
          <CardDescription>
            Paste your career details, work experience, skills, or any text you'd like to convert into a professional
            resume format with advanced visual customization.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Textarea
            placeholder="Example: I am a software engineer with 5 years of experience. I worked at TechCorp where I built web applications using React and Node.js. I have skills in JavaScript, Python, AWS, and databases. I graduated from UC Berkeley with a Computer Science degree..."
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="min-h-[200px] resize-none"
          />
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Badge variant="secondary">{inputText.length} characters</Badge>
              {inputText.length > 100 && (
                <Badge variant="outline" className="text-primary border-primary">
                  <CheckCircle className="h-3 w-3 mr-1" />
                  Good length
                </Badge>
              )}
            </div>
            <Button onClick={handleConvert} disabled={isConverting || !inputText.trim()}>
              {isConverting ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2" />
                  Converting...
                </>
              ) : (
                <>
                  <Wand2 className="h-4 w-4 mr-2" />
                  Convert & Build Visually
                </>
              )}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Output Section */}
      {convertedResume && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="font-space-grotesk">Your Professional Resume</CardTitle>
                <CardDescription>
                  AI-generated resume format ready for visual customization with our advanced builder.
                </CardDescription>
              </div>
              <div className="flex items-center space-x-2">
                <Button variant="outline" size="sm" onClick={handleCopy}>
                  {copied ? (
                    <>
                      <CheckCircle className="h-4 w-4 mr-2 text-primary" />
                      Copied
                    </>
                  ) : (
                    <>
                      <Copy className="h-4 w-4 mr-2" />
                      Copy
                    </>
                  )}
                </Button>
                <Button variant="outline" size="sm" onClick={handleDownload}>
                  <Download className="h-4 w-4 mr-2" />
                  Download
                </Button>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="bg-muted/30 rounded-lg p-6 font-mono text-sm whitespace-pre-wrap border">
              {convertedResume}
            </div>
            <Separator className="my-4" />
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>Resume generated with AI formatting</span>
              <Badge variant="secondary">Ready for visual customization</Badge>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Enhanced Tips Section */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="font-space-grotesk text-lg">💡 Pro Tips for Better Results</CardTitle>
        </CardHeader>
        <CardContent>
          <ul className="space-y-2 text-sm text-muted-foreground">
            <li>Include specific job titles, company names, and years of experience</li>
            <li>Mention technical skills, programming languages, and tools you've used</li>
            <li>Add quantifiable achievements (e.g., "increased sales by 30%")</li>
            <li>Include education details, certifications, and relevant projects</li>
            <li>The more detailed your input, the better the formatted output and visual builder experience</li>
            <li>Use the visual builder to create multi-page resumes with professional layouts</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}
