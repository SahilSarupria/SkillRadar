"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  PieChart,
  Pie,
  Cell,
  LineChart,
  Line,
} from "recharts"
import {
  TrendingUp,
  FileText,
  Target,
  BookOpen,
  Award,
  AlertTriangle,
  CheckCircle,
  Download,
  Share,
} from "lucide-react"

// Mock data for the dashboard
const mockAnalysisData = {
  overallScore: 78,
  previousScore: 65,
  sectionsData: [
    { section: "Contact Info", score: 95, maxScore: 100 },
    { section: "Summary", score: 72, maxScore: 100 },
    { section: "Experience", score: 85, maxScore: 100 },
    { section: "Skills", score: 65, maxScore: 100 },
    { section: "Education", score: 90, maxScore: 100 },
    { section: "ATS Score", score: 60, maxScore: 100 },
  ],
  skillsRadar: [
    { skill: "Technical Skills", current: 75, market: 85 },
    { skill: "Leadership", current: 60, market: 70 },
    { skill: "Communication", current: 80, market: 75 },
    { skill: "Problem Solving", current: 85, market: 80 },
    { skill: "Project Management", current: 55, market: 75 },
    { skill: "Industry Knowledge", current: 70, market: 80 },
  ],
  atsCompatibility: [
    { name: "Compatible", value: 60, color: "#059669" },
    { name: "Needs Improvement", value: 25, color: "#f59e0b" },
    { name: "Issues Found", value: 15, color: "#ef4444" },
  ],
  improvementTrend: [
    { month: "Jan", score: 45 },
    { month: "Feb", score: 52 },
    { month: "Mar", score: 58 },
    { month: "Apr", score: 65 },
    { month: "May", score: 72 },
    { month: "Jun", score: 78 },
  ],
  keyInsights: [
    {
      type: "success",
      title: "Strong Experience Section",
      description: "Your work experience demonstrates clear career progression with quantifiable achievements.",
      impact: "High",
    },
    {
      type: "warning",
      title: "Skills Section Needs Enhancement",
      description: "Consider adding more technical skills and certifications relevant to your target roles.",
      impact: "Medium",
    },
    {
      type: "error",
      title: "ATS Compatibility Issues",
      description: "Some formatting elements may prevent proper parsing by applicant tracking systems.",
      impact: "High",
    },
    {
      type: "info",
      title: "Missing Keywords",
      description: "Include more industry-specific keywords to improve visibility in searches.",
      impact: "Medium",
    },
  ],
  recommendations: [
    "Add cloud computing certifications (AWS, Azure, GCP)",
    "Include more quantifiable achievements in your summary",
    "Optimize formatting for better ATS compatibility",
    "Add relevant industry keywords throughout your resume",
    "Consider adding a projects or portfolio section",
  ],
}

export function AnalysisDashboard() {
  const [activeTab, setActiveTab] = useState("overview")

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  const getInsightIcon = (type: string) => {
    switch (type) {
      case "success":
        return <CheckCircle className="h-5 w-5 text-green-600" />
      case "warning":
        return <AlertTriangle className="h-5 w-5 text-yellow-600" />
      case "error":
        return <AlertTriangle className="h-5 w-5 text-red-600" />
      default:
        return <FileText className="h-5 w-5 text-blue-600" />
    }
  }

  return (
    <div className="space-y-6">
      {/* Header Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Overall Score</p>
                <p className={`text-3xl font-bold ${getScoreColor(mockAnalysisData.overallScore)}`}>
                  {mockAnalysisData.overallScore}
                </p>
              </div>
              <div className="flex items-center space-x-1 text-green-600">
                <TrendingUp className="h-4 w-4" />
                <span className="text-sm font-medium">
                  +{mockAnalysisData.overallScore - mockAnalysisData.previousScore}
                </span>
              </div>
            </div>
            <Progress value={mockAnalysisData.overallScore} className="mt-3" />
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">ATS Compatible</p>
                <p className="text-3xl font-bold text-yellow-600">60%</p>
              </div>
              <Target className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">Needs optimization</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Skill Gaps</p>
                <p className="text-3xl font-bold text-red-600">5</p>
              </div>
              <BookOpen className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">Areas to improve</p>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Market Readiness</p>
                <p className="text-3xl font-bold text-green-600">Good</p>
              </div>
              <Award className="h-8 w-8 text-muted-foreground" />
            </div>
            <p className="text-xs text-muted-foreground mt-2">Above average</p>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <div className="flex items-center justify-between">
          <TabsList className="grid w-full max-w-md grid-cols-4">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="sections">Sections</TabsTrigger>
            <TabsTrigger value="skills">Skills</TabsTrigger>
            <TabsTrigger value="trends">Trends</TabsTrigger>
          </TabsList>
          <div className="flex items-center space-x-2">
            <Button variant="outline" size="sm">
              <Download className="h-4 w-4 mr-2" />
              Export Report
            </Button>
            <Button variant="outline" size="sm">
              <Share className="h-4 w-4 mr-2" />
              Share
            </Button>
          </div>
        </div>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Section Scores */}
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Section Performance</CardTitle>
                <CardDescription>Detailed breakdown of each resume section</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={mockAnalysisData.sectionsData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="section" tick={{ fontSize: 12 }} />
                    <YAxis />
                    <Tooltip />
                    <Bar dataKey="score" fill="#059669" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            {/* ATS Compatibility */}
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">ATS Compatibility</CardTitle>
                <CardDescription>How well your resume works with applicant tracking systems</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={mockAnalysisData.atsCompatibility}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={120}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {mockAnalysisData.atsCompatibility.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
                <div className="flex justify-center space-x-4 mt-4">
                  {mockAnalysisData.atsCompatibility.map((item, index) => (
                    <div key={index} className="flex items-center space-x-2">
                      <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                      <span className="text-sm">{item.name}</span>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </div>

          {/* Key Insights */}
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Key Insights</CardTitle>
              <CardDescription>Important findings from your resume analysis</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {mockAnalysisData.keyInsights.map((insight, index) => (
                  <div key={index} className="flex items-start space-x-3 p-4 border rounded-lg">
                    {getInsightIcon(insight.type)}
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-1">
                        <h4 className="font-medium">{insight.title}</h4>
                        <Badge
                          variant={
                            insight.impact === "High"
                              ? "destructive"
                              : insight.impact === "Medium"
                                ? "default"
                                : "secondary"
                          }
                        >
                          {insight.impact}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">{insight.description}</p>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="sections" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Section-by-Section Analysis</CardTitle>
              <CardDescription>Detailed feedback for each part of your resume</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {mockAnalysisData.sectionsData.map((section, index) => (
                  <div key={index} className="border rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="font-space-grotesk font-semibold text-lg">{section.section}</h3>
                      <div className="flex items-center space-x-2">
                        <span className={`text-2xl font-bold ${getScoreColor(section.score)}`}>{section.score}%</span>
                        <Progress value={section.score} className="w-24" />
                      </div>
                    </div>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div>
                        <h4 className="font-medium mb-2">Strengths</h4>
                        <ul className="space-y-1 text-muted-foreground">
                          <li>• Clear and professional formatting</li>
                          <li>• Relevant information included</li>
                          <li>• Good use of action verbs</li>
                        </ul>
                      </div>
                      <div>
                        <h4 className="font-medium mb-2">Improvements</h4>
                        <ul className="space-y-1 text-muted-foreground">
                          <li>• Add more quantifiable results</li>
                          <li>• Include relevant keywords</li>
                          <li>• Optimize for ATS systems</li>
                        </ul>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skills" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Skills vs Market Demand</CardTitle>
                <CardDescription>How your skills compare to market requirements</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={400}>
                  <RadarChart data={mockAnalysisData.skillsRadar}>
                    <PolarGrid />
                    <PolarAngleAxis dataKey="skill" tick={{ fontSize: 12 }} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} />
                    <Radar name="Your Skills" dataKey="current" stroke="#059669" fill="#059669" fillOpacity={0.3} />
                    <Radar name="Market Demand" dataKey="market" stroke="#10b981" fill="#10b981" fillOpacity={0.1} />
                    <Tooltip />
                  </RadarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Skill Gap Analysis</CardTitle>
                <CardDescription>Areas where you can improve to meet market demands</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockAnalysisData.skillsRadar.map((skill, index) => {
                    const gap = skill.market - skill.current
                    return (
                      <div key={index} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{skill.skill}</span>
                          <span
                            className={`text-sm ${gap > 10 ? "text-red-600" : gap > 5 ? "text-yellow-600" : "text-green-600"}`}
                          >
                            {gap > 0 ? `+${gap} needed` : "Above market"}
                          </span>
                        </div>
                        <div className="flex space-x-2">
                          <Progress value={skill.current} className="flex-1" />
                          <Progress value={skill.market} className="flex-1 opacity-50" />
                        </div>
                      </div>
                    )
                  })}
                </div>
                <div className="mt-6 p-4 bg-muted/30 rounded-lg">
                  <h4 className="font-medium mb-2">Priority Skills to Develop</h4>
                  <div className="flex flex-wrap gap-2">
                    <Badge variant="outline">Cloud Computing</Badge>
                    <Badge variant="outline">Project Management</Badge>
                    <Badge variant="outline">Leadership</Badge>
                  </div>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>

        <TabsContent value="trends" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Score Improvement Trend</CardTitle>
              <CardDescription>Track your resume optimization progress over time</CardDescription>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={mockAnalysisData.improvementTrend}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="month" />
                  <YAxis />
                  <Tooltip />
                  <Line type="monotone" dataKey="score" stroke="#059669" strokeWidth={3} dot={{ fill: "#059669" }} />
                </LineChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          <div className="grid md:grid-cols-2 gap-6">
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Recent Improvements</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm">Added technical certifications (+8 points)</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm">Improved ATS compatibility (+5 points)</span>
                  </div>
                  <div className="flex items-center space-x-3">
                    <TrendingUp className="h-4 w-4 text-green-600" />
                    <span className="text-sm">Enhanced summary section (+3 points)</span>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Next Steps</CardTitle>
              </CardHeader>
              <CardContent>
                <div className="space-y-3">
                  {mockAnalysisData.recommendations.slice(0, 3).map((rec, index) => (
                    <div key={index} className="flex items-start space-x-3">
                      <div className="bg-primary/10 rounded-full p-1 mt-0.5">
                        <div className="w-2 h-2 bg-primary rounded-full" />
                      </div>
                      <span className="text-sm">{rec}</span>
                    </div>
                  ))}
                </div>
                <Button className="w-full mt-4" asChild>
                  <a href="/skills">View All Recommendations</a>
                </Button>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
