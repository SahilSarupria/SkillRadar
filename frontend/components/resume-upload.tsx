"use client"

import type React from "react"
import { useEffect } from "react"
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
  const [resumeId, setResumeId] = useState<string | null>(null)
  const [parsedResume, setParsedResume] = useState<any | null>(null)
  const { toast } = useToast()
  const [selectedJobRole, setSelectedJobRole] = useState<string | null>(null)
const [jobRoles, setJobRoles] = useState<any[]>([])
const [defaultGoal, setDefaultGoal] = useState<any | null>(null)
useEffect(() => {
  async function fetchJobRoles() {
    try {
      const res = await fetch("http://localhost:8000/api/skills/job-roles/", {
        credentials: "include",
      });
      if (!res.ok) throw new Error(`HTTP error! Status: ${res.status}`);

      const data = await res.json();
      setJobRoles(data.results || []);  // 👈 IMPORTANT
    } catch (err) {
      console.error("Error fetching job roles:", err);
      setJobRoles([]); // fallback
    }
  }

  fetchJobRoles();
}, []);




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
      title: "File ready",
      description: `${selectedFile.name} is ready for analysis.`,
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

  async function handleAnalyze() {
    if (!file) return

    setIsAnalyzing(true)
    setAnalysisResult(null)
    setParsedResume(null)
    setResumeId(null)

    try {
      // 1) Upload file to backend which parses it
      const fd = new FormData()
      fd.append("file", file)
      const uploadRes = await fetch("http://localhost:8000/api/resumes/upload-resume/", {
        method: "POST",
        body: fd,
        credentials: "include",
      })
      if (!uploadRes.ok) {
        const err = await uploadRes.text()
        throw new Error(`Upload failed: ${uploadRes.status} ${err}`)
      }
      const uploadJson = await uploadRes.json()
      const parsed = uploadJson.parsed || null
      const rid = uploadJson.resume_id || null
      setParsedResume(parsed)
      setResumeId(rid)

      // 2) Calculate score - use a default sample Goal for now
      // 2) Get goal for selected job role




      const scoreRes = await fetch("http://localhost:8000/api/resumes/calculate-score/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ resume_data: parsed, goal: defaultGoal }),
      })
      if (!scoreRes.ok) {
        const err = await scoreRes.text()
        throw new Error(`Scoring failed: ${scoreRes.status} ${err}`)
      }
      const scoreJson = await scoreRes.json()

      // 3) Build UI-friendly analysisResult from parsed + score response
      const overallScore = scoreJson.score ?? 0
      const breakdown = scoreJson.breakdown ?? {}
      const matchedSkills: string[] = (scoreJson.matched_skills || []).map((s: string) => String(s))

      // derive some section scores heuristically
      const contactScore = parsed && parsed.personal_info && (parsed.personal_info.email || parsed.personal_info.phone) ? 95 : 40
      const summaryLen = parsed && parsed.professional_summary ? String(parsed.professional_summary).trim().length : 0
      const summaryScore = summaryLen > 200 ? 80 : summaryLen > 80 ? 70 : 50
      const experienceScore = Math.round(breakdown.experience_match_percent ?? 0)
      const skillsScore = Math.round(breakdown.skill_match_percent ?? 0)
      const educationScore = parsed && parsed.education && parsed.education.length ? 90 : 50
      const atsScore = (contactScore > 80 && skillsScore > 50 && experienceScore > 40) ? 85 : 55

      // status helper
      const statusFor = (s: number) => (s >= 80 ? "good" : s >= 60 ? "warning" : "error") as "good" | "warning" | "error"

      // compute skill gaps relative to defaultGoal
      const reqSet = new Set((defaultGoal.required_skills || []).map((s: string) => s.toLowerCase()))
      const matchedSet = new Set(matchedSkills.map((s) => s.toLowerCase()))
      const gaps = Array.from(reqSet).filter((s) => !matchedSet.has(s))

      const sections = [
        { name: "Contact Information", score: contactScore, feedback: contactScore >= 80 ? "Complete and professional contact details" : "Add email and phone in a clear header", status: statusFor(contactScore) },
        { name: "Professional Summary", score: summaryScore, feedback: summaryScore >= 75 ? "Good summary" : "Make your summary impact-first and include achievements", status: statusFor(summaryScore) },
        { name: "Work Experience", score: experienceScore, feedback: experienceScore >= 70 ? "Strong experience" : "Add measurable achievements and dates", status: statusFor(experienceScore) },
        { name: "Skills Section", score: skillsScore, feedback: skillsScore >= 70 ? "Relevant skills present" : "Add missing technical skills required for the target role", status: statusFor(skillsScore) },
        { name: "Education", score: educationScore, feedback: educationScore >= 80 ? "Education section looks good" : "Add degree/timeframe details", status: statusFor(educationScore) },
        { name: "ATS Compatibility", score: atsScore, feedback: atsScore >= 75 ? "Likely ATS friendly" : "Simplify formatting and add keywords for ATS", status: statusFor(atsScore) },
      ]

      const recommendations: string[] = []
      if (gaps.length) recommendations.push(`Add or emphasize these required skills: ${gaps.join(", ")}`)
      if (skillsScore < 70) recommendations.push("Expand the technical skills section with concrete tools and frameworks.")
      if (experienceScore < 70) recommendations.push("Add quantifiable achievements (metrics, percentages) to experience bullets.")
      if (atsScore < 70) recommendations.push("Use plain text headings and avoid complex tables to improve ATS parsing.")

      setAnalysisResult({
        overallScore,
        sections,
        recommendations,
        skillGaps: gaps,
      })

      toast({
        title: "Analysis complete",
        description: "Resume parsed and scored by the backend.",
      })
    } catch (error: any) {
      console.error(error)
      toast({
        title: "Analysis error",
        description: String(error?.message || error),
        variant: "destructive",
      })
    } finally {
      setIsAnalyzing(false)
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
                <div className="space-y-4">
  {/* Job Role Select */}
<label className="text-sm font-medium">Target Job Role</label>
<select
  className="border rounded-md p-2 w-full"
  value={selectedJobRole || ""}
  onChange={async (e) => {
    const id = e.target.value;
    setSelectedJobRole(id);
    setDefaultGoal(null); // reset while loading

    try {
      const res = await fetch(`http://localhost:8000/api/skills/job-roles/get-goal/${id}/`, { credentials: "include" });
      if (!res.ok) throw new Error("Failed to fetch goal details");
      const data = await res.json();
      setDefaultGoal(data);  // 👈 set full job role
    } catch (err) {
      console.error(err);
      toast({ title: "Error", description: "Failed to load job role details.", variant: "destructive" });
    }
  }}
>

  <option value="" disabled>Select job role</option>
  {jobRoles.length > 0 ? (
    jobRoles.map((job) => (
      <option key={job.id} value={job.id}>
        {job.title} - {job.industry} ({job.level})
      </option>
    ))
  ) : (
    <option disabled>Loading...</option>
  )}
</select>

</div>

                <div className="flex items-center space-x-4">
                  <Button onClick={handleAnalyze} disabled={isAnalyzing || !selectedJobRole }>
                    {isAnalyzing ? (
    <>
        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2" />
        Analyzing...
    </>
) : (
    // Removed the "ynta error" text
    !selectedJobRole ? "Select Job Role First" : "Analyze Resume"
)}
                    
                  </Button>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setFile(null)
                      setAnalysisResult(null)
                      setParsedResume(null)
                      setResumeId(null)
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
                {analysisResult.skillGaps.length ? (
                  analysisResult.skillGaps.map((skill, index) => (
                    <Badge key={index} variant="outline" className="text-sm">
                      {skill}
                    </Badge>
                  ))
                ) : (
                  <div className="text-sm text-muted-foreground">No major gaps detected for the selected goal.</div>
                )}
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
