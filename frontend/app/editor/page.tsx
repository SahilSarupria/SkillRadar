"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import Navbar from "@/components/Navbar"
import ResumeForm from "./components/ResumeForm"
import ResumePreview from "./components/ResumePreview"
import TemplateSelector from "./components/TemplateSelector"
import ColorPicker from "./components/ColorPicker"
import FontPicker from "./components/FontPicker"
import { Button } from "@/components/ui/button"
import { Download, Save } from "lucide-react"

export interface ResumeData {
  personalInfo: {
    name: string
    email: string
    phone: string
    location: string
    linkedin: string
    website: string
  }
  summary: string
  skills: string[]
  experience: Array<{
    id: string
    company: string
    position: string
    startDate: string
    endDate: string
    description: string
  }>
  education: Array<{
    id: string
    school: string
    degree: string
    field: string
    graduationDate: string
    gpa?: string
  }>
  projects: Array<{
    id: string
    name: string
    description: string
    technologies: string[]
    link?: string
  }>
}

export interface ResumeTheme {
  template: string
  primaryColor: string
  fontFamily: string
}

export default function EditorPage() {
  const [resumeData, setResumeData] = useState<ResumeData>({
    personalInfo: {
      name: "",
      email: "",
      phone: "",
      location: "",
      linkedin: "",
      website: "",
    },
    summary: "",
    skills: [],
    experience: [],
    education: [],
    projects: [],
  })

  const [theme, setTheme] = useState<ResumeTheme>({
    template: "modern",
    primaryColor: "#3b82f6",
    fontFamily: "Inter",
  })

  const handleExportPDF = () => {
    // TODO: Implement PDF export
    console.log("Exporting PDF...")
  }

  const handleSave = () => {
    // TODO: Implement save functionality
    console.log("Saving resume...")
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />

      <div className="container mx-auto px-4 py-6">
        {/* Header Actions */}
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-900">Resume Editor</h1>
          <div className="flex gap-3">
            <Button variant="outline" onClick={handleSave}>
              <Save className="mr-2 h-4 w-4" />
              Save
            </Button>
            <Button onClick={handleExportPDF}>
              <Download className="mr-2 h-4 w-4" />
              Export PDF
            </Button>
          </div>
        </div>

        {/* Customization Panel */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mb-6">
          <TemplateSelector
            selectedTemplate={theme.template}
            onTemplateChange={(template) => setTheme({ ...theme, template })}
          />
          <ColorPicker
            selectedColor={theme.primaryColor}
            onColorChange={(color) => setTheme({ ...theme, primaryColor: color })}
          />
          <FontPicker
            selectedFont={theme.fontFamily}
            onFontChange={(font) => setTheme({ ...theme, fontFamily: font })}
          />
        </div>

        {/* Main Editor Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Form Panel */}
          <div className="space-y-6">
            <ResumeForm data={resumeData} onChange={setResumeData} />
          </div>

          {/* Preview Panel */}
          <div className="lg:sticky lg:top-6">
            <Card className="p-6">
              <ResumePreview data={resumeData} theme={theme} />
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
