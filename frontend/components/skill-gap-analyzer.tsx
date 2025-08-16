"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, ResponsiveContainer, Tooltip } from "recharts"
import { Target, BookOpen, AlertTriangle, CheckCircle, Search, ExternalLink } from "lucide-react"
import { useToast } from "@/hooks/use-toast"

// Mock data for different job roles
const jobRoles = {
  "Software Engineer": {
    requiredSkills: [
      { skill: "JavaScript", importance: 95, userLevel: 80 },
      { skill: "React", importance: 90, userLevel: 75 },
      { skill: "Node.js", importance: 85, userLevel: 70 },
      { skill: "TypeScript", importance: 80, userLevel: 60 },
      { skill: "AWS", importance: 75, userLevel: 40 },
      { skill: "Docker", importance: 70, userLevel: 30 },
      { skill: "GraphQL", importance: 65, userLevel: 25 },
      { skill: "Kubernetes", importance: 60, userLevel: 20 },
    ],
    averageSalary: "$95,000",
    jobGrowth: "+22%",
    openings: "1.2M",
  },
  "Data Scientist": {
    requiredSkills: [
      { skill: "Python", importance: 95, userLevel: 70 },
      { skill: "Machine Learning", importance: 90, userLevel: 50 },
      { skill: "SQL", importance: 85, userLevel: 80 },
      { skill: "Statistics", importance: 80, userLevel: 60 },
      { skill: "TensorFlow", importance: 75, userLevel: 30 },
      { skill: "R", importance: 70, userLevel: 40 },
      { skill: "Deep Learning", importance: 65, userLevel: 25 },
      { skill: "Big Data", importance: 60, userLevel: 35 },
    ],
    averageSalary: "$118,000",
    jobGrowth: "+31%",
    openings: "450K",
  },
  "Product Manager": {
    requiredSkills: [
      { skill: "Product Strategy", importance: 95, userLevel: 65 },
      { skill: "Data Analysis", importance: 90, userLevel: 70 },
      { skill: "User Research", importance: 85, userLevel: 55 },
      { skill: "Agile/Scrum", importance: 80, userLevel: 75 },
      { skill: "A/B Testing", importance: 75, userLevel: 45 },
      { skill: "Roadmapping", importance: 70, userLevel: 60 },
      { skill: "Stakeholder Management", importance: 85, userLevel: 80 },
      { skill: "Technical Understanding", importance: 65, userLevel: 50 },
    ],
    averageSalary: "$125,000",
    jobGrowth: "+19%",
    openings: "320K",
  },
}

const skillCategories = [
  "Technical Skills",
  "Programming Languages",
  "Frameworks & Libraries",
  "Cloud & DevOps",
  "Data & Analytics",
  "Soft Skills",
  "Certifications",
]

export function SkillGapAnalyzer() {
  const [selectedRole, setSelectedRole] = useState<string>("")
  const [customRole, setCustomRole] = useState("")
  const [analysisComplete, setAnalysisComplete] = useState(false)
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [activeTab, setActiveTab] = useState("analysis")
  const { toast } = useToast()

  const handleAnalyze = async () => {
    const roleToAnalyze = selectedRole === "custom" ? customRole : selectedRole

    if (!roleToAnalyze) {
      toast({
        title: "Please select a job role",
        description: "Choose a target role to analyze your skill gaps.",
        variant: "destructive",
      })
      return
    }

    setIsAnalyzing(true)

    // Simulate analysis
    await new Promise((resolve) => setTimeout(resolve, 2000))

    setAnalysisComplete(true)
    setIsAnalyzing(false)

    toast({
      title: "Analysis complete!",
      description: "Your skill gap analysis is ready. Check the results below.",
    })
  }

  const getCurrentRoleData = () => {
    if (selectedRole === "custom") {
      // Return mock data for custom role
      return jobRoles["Software Engineer"] // Fallback to software engineer data
    }
    return jobRoles[selectedRole as keyof typeof jobRoles]
  }

  const getSkillGapColor = (gap: number) => {
    if (gap <= 10) return "#059669" // Green - small gap
    if (gap <= 30) return "#f59e0b" // Yellow - medium gap
    return "#ef4444" // Red - large gap
  }

  const getSkillGapStatus = (gap: number) => {
    if (gap <= 10) return "Strong"
    if (gap <= 30) return "Developing"
    return "Needs Focus"
  }

  const roleData = getCurrentRoleData()
  const skillGaps =
    roleData?.requiredSkills.map((skill) => ({
      ...skill,
      gap: Math.max(0, skill.importance - skill.userLevel),
    })) || []

  const prioritySkills = skillGaps
    .filter((skill) => skill.gap > 20)
    .sort((a, b) => b.gap - a.gap)
    .slice(0, 5)

  return (
    <div className="space-y-8">
      {/* Job Role Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="font-space-grotesk flex items-center space-x-2">
            <Target className="h-5 w-5 text-primary" />
            <span>Target Job Role</span>
          </CardTitle>
          <CardDescription>
            Select your target job role to analyze the skills you need to develop for career advancement.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="job-role">Choose a Role</Label>
              <Select value={selectedRole} onValueChange={setSelectedRole}>
                <SelectTrigger>
                  <SelectValue placeholder="Select a job role" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="Software Engineer">Software Engineer</SelectItem>
                  <SelectItem value="Data Scientist">Data Scientist</SelectItem>
                  <SelectItem value="Product Manager">Product Manager</SelectItem>
                  <SelectItem value="custom">Custom Role</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {selectedRole === "custom" && (
              <div className="space-y-2">
                <Label htmlFor="custom-role">Custom Role</Label>
                <Input
                  id="custom-role"
                  placeholder="Enter your target role"
                  value={customRole}
                  onChange={(e) => setCustomRole(e.target.value)}
                />
              </div>
            )}
          </div>

          {selectedRole && selectedRole !== "custom" && roleData && (
            <div className="grid md:grid-cols-3 gap-4 p-4 bg-muted/30 rounded-lg">
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Average Salary</p>
                <p className="text-lg font-semibold text-primary">{roleData.averageSalary}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Job Growth</p>
                <p className="text-lg font-semibold text-green-600">{roleData.jobGrowth}</p>
              </div>
              <div className="text-center">
                <p className="text-sm text-muted-foreground">Open Positions</p>
                <p className="text-lg font-semibold text-blue-600">{roleData.openings}</p>
              </div>
            </div>
          )}

          <Button onClick={handleAnalyze} disabled={isAnalyzing} className="w-full">
            {isAnalyzing ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-foreground mr-2" />
                Analyzing Skills...
              </>
            ) : (
              <>
                <Search className="h-4 w-4 mr-2" />
                Analyze Skill Gaps
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Analysis Results */}
      {analysisComplete && roleData && (
        <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
          <TabsList className="grid w-full max-w-md grid-cols-3">
            <TabsTrigger value="analysis">Analysis</TabsTrigger>
            <TabsTrigger value="skills">Skills</TabsTrigger>
            <TabsTrigger value="roadmap">Roadmap</TabsTrigger>
          </TabsList>

          <TabsContent value="analysis" className="space-y-6">
            {/* Overview Stats */}
            <div className="grid md:grid-cols-4 gap-4">
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-primary mb-1">
                    {skillGaps.filter((s) => s.gap <= 10).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Strong Skills</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-yellow-600 mb-1">
                    {skillGaps.filter((s) => s.gap > 10 && s.gap <= 30).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Developing</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-red-600 mb-1">
                    {skillGaps.filter((s) => s.gap > 30).length}
                  </div>
                  <div className="text-sm text-muted-foreground">Needs Focus</div>
                </CardContent>
              </Card>
              <Card>
                <CardContent className="p-4 text-center">
                  <div className="text-2xl font-bold text-foreground mb-1">
                    {Math.round(skillGaps.reduce((acc, s) => acc + s.userLevel, 0) / skillGaps.length)}%
                  </div>
                  <div className="text-sm text-muted-foreground">Overall Match</div>
                </CardContent>
              </Card>
            </div>

            {/* Skill Gap Visualization */}
            <div className="grid lg:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle className="font-space-grotesk">Skills Radar</CardTitle>
                  <CardDescription>Your current skills vs market requirements</CardDescription>
                </CardHeader>
                <CardContent>
                  <ResponsiveContainer width="100%" height={400}>
                    <RadarChart data={skillGaps.slice(0, 6)}>
                      <PolarGrid />
                      <PolarAngleAxis dataKey="skill" tick={{ fontSize: 12 }} />
                      <PolarRadiusAxis angle={90} domain={[0, 100]} />
                      <Radar name="Your Level" dataKey="userLevel" stroke="#059669" fill="#059669" fillOpacity={0.3} />
                      <Radar
                        name="Required Level"
                        dataKey="importance"
                        stroke="#10b981"
                        fill="#10b981"
                        fillOpacity={0.1}
                      />
                      <Tooltip />
                    </RadarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle className="font-space-grotesk">Priority Skills</CardTitle>
                  <CardDescription>Skills with the largest gaps that need immediate attention</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    {prioritySkills.map((skill, index) => (
                      <div key={index} className="space-y-2">
                        <div className="flex items-center justify-between">
                          <span className="font-medium">{skill.skill}</span>
                          <Badge
                            variant="outline"
                            style={{ color: getSkillGapColor(skill.gap), borderColor: getSkillGapColor(skill.gap) }}
                          >
                            {getSkillGapStatus(skill.gap)}
                          </Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <Progress value={skill.userLevel} className="flex-1" />
                          <span className="text-sm text-muted-foreground w-16">
                            {skill.userLevel}% / {skill.importance}%
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                  {prioritySkills.length === 0 && (
                    <div className="text-center py-8">
                      <CheckCircle className="h-12 w-12 text-green-600 mx-auto mb-4" />
                      <p className="text-lg font-medium">Great job!</p>
                      <p className="text-muted-foreground">You have strong skills for this role.</p>
                    </div>
                  )}
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="skills" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Detailed Skill Analysis</CardTitle>
                <CardDescription>Complete breakdown of all required skills for {selectedRole}</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {skillGaps.map((skill, index) => (
                    <div key={index} className="border rounded-lg p-4">
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center space-x-3">
                          <h3 className="font-medium">{skill.skill}</h3>
                          <Badge variant="secondary">Importance: {skill.importance}%</Badge>
                        </div>
                        <div className="flex items-center space-x-2">
                          <span className="text-sm text-muted-foreground">Gap:</span>
                          <span className="font-semibold" style={{ color: getSkillGapColor(skill.gap) }}>
                            {skill.gap} points
                          </span>
                        </div>
                      </div>
                      <div className="grid md:grid-cols-2 gap-4">
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm">Your Level</span>
                            <span className="text-sm font-medium">{skill.userLevel}%</span>
                          </div>
                          <Progress value={skill.userLevel} />
                        </div>
                        <div>
                          <div className="flex items-center justify-between mb-1">
                            <span className="text-sm">Market Requirement</span>
                            <span className="text-sm font-medium">{skill.importance}%</span>
                          </div>
                          <Progress value={skill.importance} className="opacity-50" />
                        </div>
                      </div>
                      {skill.gap > 20 && (
                        <div className="mt-3 p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded-lg">
                          <div className="flex items-center space-x-2">
                            <AlertTriangle className="h-4 w-4 text-yellow-600" />
                            <span className="text-sm font-medium text-yellow-800 dark:text-yellow-200">
                              High Priority
                            </span>
                          </div>
                          <p className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                            This skill has a significant gap and should be prioritized for learning.
                          </p>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>
          </TabsContent>

          <TabsContent value="roadmap" className="space-y-6">
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Learning Roadmap</CardTitle>
                <CardDescription>Prioritized plan to close your skill gaps and reach your career goals</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-6">
                  {/* Immediate Focus */}
                  <div>
                    <h3 className="font-space-grotesk font-semibold text-lg mb-4 flex items-center space-x-2">
                      <div className="bg-red-100 dark:bg-red-900/20 rounded-full p-1">
                        <div className="w-2 h-2 bg-red-600 rounded-full" />
                      </div>
                      <span>Immediate Focus (Next 1-3 months)</span>
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                      {prioritySkills.slice(0, 2).map((skill, index) => (
                        <div key={index} className="border rounded-lg p-4">
                          <h4 className="font-medium mb-2">{skill.skill}</h4>
                          <p className="text-sm text-muted-foreground mb-3">
                            Gap: {skill.gap} points • High impact on role success
                          </p>
                          <div className="space-y-2">
                            <Button size="sm" variant="outline" className="w-full bg-transparent">
                              <BookOpen className="h-4 w-4 mr-2" />
                              Find Courses
                            </Button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Medium Term */}
                  <div>
                    <h3 className="font-space-grotesk font-semibold text-lg mb-4 flex items-center space-x-2">
                      <div className="bg-yellow-100 dark:bg-yellow-900/20 rounded-full p-1">
                        <div className="w-2 h-2 bg-yellow-600 rounded-full" />
                      </div>
                      <span>Medium Term (3-6 months)</span>
                    </h3>
                    <div className="grid md:grid-cols-3 gap-4">
                      {skillGaps
                        .filter((s) => s.gap > 10 && s.gap <= 30)
                        .slice(0, 3)
                        .map((skill, index) => (
                          <div key={index} className="border rounded-lg p-4">
                            <h4 className="font-medium mb-2">{skill.skill}</h4>
                            <p className="text-sm text-muted-foreground mb-3">Gap: {skill.gap} points</p>
                            <Button size="sm" variant="outline" className="w-full bg-transparent">
                              <BookOpen className="h-4 w-4 mr-2" />
                              Plan Learning
                            </Button>
                          </div>
                        ))}
                    </div>
                  </div>

                  {/* Long Term */}
                  <div>
                    <h3 className="font-space-grotesk font-semibold text-lg mb-4 flex items-center space-x-2">
                      <div className="bg-green-100 dark:bg-green-900/20 rounded-full p-1">
                        <div className="w-2 h-2 bg-green-600 rounded-full" />
                      </div>
                      <span>Long Term (6+ months)</span>
                    </h3>
                    <div className="grid md:grid-cols-4 gap-4">
                      {skillGaps
                        .filter((s) => s.gap <= 10)
                        .slice(0, 4)
                        .map((skill, index) => (
                          <div key={index} className="border rounded-lg p-4">
                            <h4 className="font-medium mb-2">{skill.skill}</h4>
                            <p className="text-sm text-muted-foreground mb-3">Maintain & Advance</p>
                            <Badge variant="outline" className="text-green-600 border-green-600">
                              Strong
                            </Badge>
                          </div>
                        ))}
                    </div>
                  </div>
                </div>

                <div className="mt-8 p-6 bg-primary/5 border border-primary/20 rounded-lg">
                  <h4 className="font-space-grotesk font-semibold mb-3">Ready to Start Learning?</h4>
                  <p className="text-muted-foreground mb-4">
                    Get personalized course recommendations from top learning platforms to close your skill gaps.
                  </p>
                  <Button className="w-full">
                    <ExternalLink className="h-4 w-4 mr-2" />
                    View Learning Recommendations
                  </Button>
                </div>
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      )}
    </div>
  )
}
