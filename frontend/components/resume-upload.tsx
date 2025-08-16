"use client"

import type React from "react"

import { useState, useCallback } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Separator } from "@/components/ui/separator"
import { Upload, FileText, CheckCircle, AlertCircle, BarChart3, Target, BookOpen } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

interface AnalysisResult {
  overallScore: number
  sections: {
    name: string
    score: number
    feedback: string
    status: "good" | "warning" | "error"
  }[]
  recommendations: string[]
  skillGaps: string[]
}

export function ResumeUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [dragActive, setDragActive] = useState(false)
  const { toast } = useToast()

  const handleDrag = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }, [])

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    const files = e.dataTransfer.files
    if (files && files[0]) {
      handleFileSelect(files[0])
    }
  }, [])

  const handleFileSelect = (selectedFile: File) => {
    const allowedTypes = [
      "application/pdf",
      "application/msword",
      "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
      "text/plain",
    ]

    if (!allowedTypes.includes(selectedFile.type)) {
      toast({
        title: "Invalid file type",
        description: "Please upload a PDF, DOC, DOCX, or TXT file.",
        variant: "destructive",
      })
      return
    }

    if (selectedFile.size > 5 * 1024 * 1024) {
      // 5MB limit
      toast({
        title: "File too large",
        description: "Please upload a file smaller than 5MB.",
        variant: "destructive",
      })
      return
    }

    setFile(selectedFile)
    toast({
      title: "File uploaded successfully",
      description: `${selectedFile.name} is ready for analysis.`,
    })
  }

  const handleAnalyze = async () => {
    if (!file) return

    setIsAnalyzing(true)

    // Simulate AI analysis
    await new Promise((resolve) => setTimeout(resolve, 3000))

    // Mock analysis result
    const mockResult: AnalysisResult = {
      overallScore: 78,
      sections: [
        {
          name: "Contact Information",
          score: 95,
          feedback: "Complete and professional contact details",
          status: "good",
        },
        {
          name: "Professional Summary",
          score: 72,
          feedback: "Good summary but could be more specific about achievements",
          status: "warning",
        },
        {
          name: "Work Experience",
          score: 85,
          feedback: "Strong experience section with quantifiable results",
          status: "good",
        },
        {
          name: "Skills Section",
          score: 65,
          feedback: "Skills listed but lacks technical depth and certifications",
          status: "warning",
        },
        {
          name: "Education",
          score: 90,
          feedback: "Well-formatted education section",
          status: "good",
        },
        {
          name: "ATS Compatibility",
          score: 60,
          feedback: "Some formatting issues may cause ATS parsing problems",
          status: "error",
        },
      ],
      recommendations: [
        "Add more specific technical skills and certifications",
        "Include quantifiable achievements in your summary",
        "Optimize formatting for better ATS compatibility",
        "Add relevant keywords for your target industry",
        "Consider adding a projects or certifications section",
      ],
      skillGaps: [
        "Cloud Computing (AWS, Azure)",
        "Data Analysis & Visualization",
        "Project Management Certification",
        "Advanced JavaScript Frameworks",
        "DevOps & CI/CD Tools",
      ],
    }

    setAnalysisResult(mockResult)
    setIsAnalyzing(false)

    toast({
      title: "Analysis complete!",
      description: "Your resume has been analyzed. Check the results below.",
    })
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getStatusIcon = (status: "good" | "warning" | "error") => {
    switch (status) {
      case "good":
        return <CheckCircle className="h-4 w-4 text-green-600" />
      case "warning":
        return <AlertCircle className="h-4 w-4 text-yellow-600" />
      case "error":
        return <AlertCircle className="h-4 w-4 text-red-600" />
    }
  }

  return (
    <div className="space-y-8">
      {/* Upload Section */}
      <Card>
        <CardHeader>
          <CardTitle className="font-space-grotesk flex items-center space-x-2">
            <Upload className="h-5 w-5 text-primary" />
            <span>Upload Your Resume</span>
          </CardTitle>
          <CardDescription>
            Upload your resume in PDF, DOC, DOCX, or TXT format for comprehensive AI analysis.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div
            className={`border-2 border-dashed rounded-lg p-8 text-center transition-colors ${
              dragActive ? "border-primary bg-primary/5" : "border-border hover:border-primary/50"
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            {file ? (
              <div className="space-y-4">
                <div className="flex items-center justify-center space-x-2">
                  <FileText className="h-8 w-8 text-primary" />
                  <div className="text-left">
                    <p className="font-medium">{file.name}</p>
                    <p className="text-sm text-muted-foreground">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                  </div>
                </div>
                <div className="flex items-center space-x-4">
                  <Button onClick={handleAnalyze} disabled={isAnalyzing}>
                    {isAnalyzing ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2" />
                        Analyzing...
                      </>
                    ) : (
                      <>
                        <BarChart3 className="h-4 w-4 mr-2" />
                        Analyze Resume
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setFile(null)
                      setAnalysisResult(null)
                    }}
                  >
                    Remove File
                  </Button>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <Upload className="h-12 w-12 text-muted-foreground mx-auto" />
                <div>
                  <p className="text-lg font-medium">Drop your resume here</p>
                  <p className="text-muted-foreground">or click to browse files</p>
                </div>
                <input
                  type="file"
                  accept=".pdf,.doc,.docx,.txt"
                  onChange={(e) => e.target.files?.[0] && handleFileSelect(e.target.files[0])}
                  className="hidden"
                  id="file-upload"
                />
                <Button asChild variant="outline">
                  <label htmlFor="file-upload" className="cursor-pointer">
                    Choose File
                  </label>
                </Button>
                <div className="flex items-center justify-center space-x-4 text-sm text-muted-foreground">
                  <Badge variant="secondary">PDF</Badge>
                  <Badge variant="secondary">DOC</Badge>
                  <Badge variant="secondary">DOCX</Badge>
                  <Badge variant="secondary">TXT</Badge>
                  <span>Max 5MB</span>
                </div>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <div className="space-y-6">
          {/* Overall Score */}
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk flex items-center justify-between">
                <span>Overall Resume Score</span>
                <span className={`text-3xl font-bold ${getScoreColor(analysisResult.overallScore)}`}>
                  {analysisResult.overallScore}/100
                </span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <Progress value={analysisResult.overallScore} className="h-3" />
              <p className="text-sm text-muted-foreground mt-2">
                {analysisResult.overallScore >= 80
                  ? "Excellent! Your resume is well-optimized."
                  : analysisResult.overallScore >= 60
                    ? "Good foundation with room for improvement."
                    : "Significant improvements needed for better results."}
              </p>
            </CardContent>
          </Card>

          {/* Section Analysis */}
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Section Analysis</CardTitle>
              <CardDescription>Detailed breakdown of each resume section with specific feedback.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {analysisResult.sections.map((section, index) => (
                  <div key={index} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-3">
                      {getStatusIcon(section.status)}
                      <div>
                        <p className="font-medium">{section.name}</p>
                        <p className="text-sm text-muted-foreground">{section.feedback}</p>
                      </div>
                    </div>
                    <div className="text-right">
                      <span className={`text-lg font-semibold ${getScoreColor(section.score)}`}>{section.score}%</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>

          {/* Recommendations */}
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk flex items-center space-x-2">
                <Target className="h-5 w-5 text-primary" />
                <span>Improvement Recommendations</span>
              </CardTitle>
            </CardHeader>
            <CardContent>
              <ul className="space-y-3">
                {analysisResult.recommendations.map((rec, index) => (
                  <li key={index} className="flex items-start space-x-2">
                    <CheckCircle className="h-4 w-4 text-primary mt-0.5 flex-shrink-0" />
                    <span className="text-sm">{rec}</span>
                  </li>
                ))}
              </ul>
            </CardContent>
          </Card>

          {/* Skill Gaps */}
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk flex items-center space-x-2">
                <BookOpen className="h-5 w-5 text-primary" />
                <span>Identified Skill Gaps</span>
              </CardTitle>
              <CardDescription>Skills that could enhance your profile for better job opportunities.</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="flex flex-wrap gap-2">
                {analysisResult.skillGaps.map((skill, index) => (
                  <Badge key={index} variant="outline" className="text-sm">
                    {skill}
                  </Badge>
                ))}
              </div>
              <Separator className="my-4" />
              <Button className="w-full" asChild>
                <a href="/skills">
                  <BookOpen className="h-4 w-4 mr-2" />
                  Get Learning Recommendations
                </a>
              </Button>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  )
}
