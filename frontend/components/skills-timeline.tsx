"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  GitBranch,
  Star,
  TrendingUp,
  Award,
  Target,
  ChevronRight,
  Plus,
  Zap,
  Calendar,
  Trophy,
  ArrowUpRight,
} from "lucide-react"

interface Skill {
  name: string
  level: number
  acquiredDate: string
  category: string
  relatedFields: string[]
  impact: "low" | "medium" | "high"
  certifications?: string[]
}

interface CareerPath {
  id: string
  title: string
  color: string
  skills: string[]
  salary: string
  growth: string
}

const mockSkillsData: Skill[] = [
  {
    name: "HTML/CSS",
    level: 90,
    acquiredDate: "2020-01",
    category: "Frontend",
    relatedFields: ["Web Development", "UI/UX Design"],
    impact: "medium",
  },
  {
    name: "JavaScript",
    level: 85,
    acquiredDate: "2020-06",
    category: "Programming",
    relatedFields: ["Web Development", "Full Stack", "Mobile Development"],
    impact: "high",
  },
  {
    name: "React",
    level: 80,
    acquiredDate: "2021-03",
    category: "Frontend",
    relatedFields: ["Web Development", "Full Stack"],
    impact: "high",
  },
  {
    name: "Node.js",
    level: 75,
    acquiredDate: "2021-08",
    category: "Backend",
    relatedFields: ["Full Stack", "Backend Development", "API Development"],
    impact: "high",
  },
  {
    name: "Python",
    level: 70,
    acquiredDate: "2022-01",
    category: "Programming",
    relatedFields: ["Data Science", "Machine Learning", "Backend Development"],
    impact: "high",
  },
  {
    name: "SQL",
    level: 85,
    acquiredDate: "2022-04",
    category: "Database",
    relatedFields: ["Data Science", "Backend Development", "Data Analysis"],
    impact: "medium",
  },
  {
    name: "Machine Learning",
    level: 60,
    acquiredDate: "2022-10",
    category: "AI/ML",
    relatedFields: ["Data Science", "AI Engineering"],
    impact: "high",
    certifications: ["Google ML Certificate"],
  },
  {
    name: "AWS",
    level: 55,
    acquiredDate: "2023-02",
    category: "Cloud",
    relatedFields: ["DevOps", "Cloud Architecture", "Full Stack"],
    impact: "high",
  },
  {
    name: "Docker",
    level: 65,
    acquiredDate: "2023-06",
    category: "DevOps",
    relatedFields: ["DevOps", "Cloud Architecture", "Backend Development"],
    impact: "medium",
  },
]

const careerPaths: CareerPath[] = [
  {
    id: "frontend",
    title: "Frontend Developer",
    color: "#3b82f6",
    skills: ["HTML/CSS", "JavaScript", "React"],
    salary: "$75,000",
    growth: "+13%",
  },
  {
    id: "fullstack",
    title: "Full Stack Developer",
    color: "#10b981",
    skills: ["JavaScript", "React", "Node.js", "SQL"],
    salary: "$95,000",
    growth: "+22%",
  },
  {
    id: "backend",
    title: "Backend Developer",
    color: "#f59e0b",
    skills: ["Node.js", "Python", "SQL", "AWS", "Docker"],
    salary: "$90,000",
    growth: "+18%",
  },
  {
    id: "datascience",
    title: "Data Scientist",
    color: "#8b5cf6",
    skills: ["Python", "SQL", "Machine Learning"],
    salary: "$118,000",
    growth: "+31%",
  },
  {
    id: "devops",
    title: "DevOps Engineer",
    color: "#ef4444",
    skills: ["AWS", "Docker", "Python"],
    salary: "$105,000",
    growth: "+25%",
  },
]

export function SkillsTimeline() {
  const [selectedSkill, setSelectedSkill] = useState<Skill | null>(null)
  const [activeView, setActiveView] = useState<"timeline" | "paths">("timeline")
  const [hoveredPath, setHoveredPath] = useState<string | null>(null)
  const [showBranches, setShowBranches] = useState<string | null>(null)

  const sortedSkills = [...mockSkillsData].sort(
    (a, b) => new Date(a.acquiredDate).getTime() - new Date(b.acquiredDate).getTime(),
  )

  const getPathCompatibility = (path: CareerPath) => {
    const userSkills = sortedSkills.map((s) => s.name)
    const matchingSkills = path.skills.filter((skill) => userSkills.includes(skill))
    return (matchingSkills.length / path.skills.length) * 100
  }

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case "high":
        return "#ef4444"
      case "medium":
        return "#f59e0b"
      case "low":
        return "#6b7280"
      default:
        return "#6b7280"
    }
  }

  const getLevelColor = (level: number) => {
    if (level >= 80) return "#10b981"
    if (level >= 60) return "#f59e0b"
    return "#ef4444"
  }

  return (
    <div className="space-y-8">
      <Card className="border-0 shadow-xl bg-gradient-to-br from-background via-background to-primary/5">
        <CardHeader className="pb-8">
          <CardTitle className="font-playfair text-3xl flex items-center space-x-3">
            <div className="p-2 rounded-xl bg-primary/10">
              <TrendingUp className="h-6 w-6 text-primary" />
            </div>
            <span>Skills Evolution Timeline</span>
          </CardTitle>
          <CardDescription className="text-lg text-muted-foreground">
            Visualize your learning journey and discover new career opportunities through skill progression
          </CardDescription>
        </CardHeader>
        <CardContent className="px-8 pb-8">
          <Tabs value={activeView} onValueChange={(v) => setActiveView(v as "timeline" | "paths")}>
            <TabsList className="grid w-full max-w-md grid-cols-2 h-12 p-1 bg-muted/50">
              <TabsTrigger value="timeline" className="font-medium">
                Timeline Journey
              </TabsTrigger>
              <TabsTrigger value="paths" className="font-medium">
                Career Paths
              </TabsTrigger>
            </TabsList>

            <TabsContent value="timeline" className="space-y-10 mt-8">
              <div className="flex items-center justify-between p-6 rounded-2xl bg-gradient-to-r from-primary/5 to-accent/5 border border-primary/10">
                <div className="space-y-2">
                  <h3 className="font-playfair font-bold text-2xl text-foreground">Your Learning Journey</h3>
                  <div className="flex items-center space-x-6 text-muted-foreground">
                    <div className="flex items-center space-x-2">
                      <Calendar className="h-4 w-4" />
                      <span>{sortedSkills.length} skills acquired</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Trophy className="h-4 w-4" />
                      <span>{new Date().getFullYear() - 2020} years of growth</span>
                    </div>
                    <div className="flex items-center space-x-2">
                      <GitBranch className="h-4 w-4" />
                      <span>{careerPaths.length} career paths unlocked</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center space-x-6">
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-gradient-to-r from-emerald-400 to-emerald-600 shadow-lg"></div>
                    <span className="text-sm font-medium">Expert (80%+)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-gradient-to-r from-amber-400 to-amber-600 shadow-lg"></div>
                    <span className="text-sm font-medium">Proficient (60-79%)</span>
                  </div>
                  <div className="flex items-center space-x-2">
                    <div className="w-4 h-4 rounded-full bg-gradient-to-r from-rose-400 to-rose-600 shadow-lg"></div>
                    <span className="text-sm font-medium">Learning (&lt;60%)</span>
                  </div>
                </div>
              </div>

              <div className="relative py-16 overflow-x-auto">
                <div className="absolute top-1/2 left-8 right-8 transform -translate-y-1/2 z-10">
                  <div className="h-1 bg-gradient-to-r from-primary/20 via-primary to-primary/20 rounded-full shadow-lg"></div>
                  <div className="absolute inset-0 h-1 bg-gradient-to-r from-primary/40 via-primary/60 to-primary/40 rounded-full blur-sm"></div>
                </div>

                <div className="flex justify-between items-start relative px-8 min-h-[400px]">
                  {sortedSkills.map((skill, index) => {
                    const skillCareerPaths = careerPaths.filter((path) =>
                      skill.relatedFields.some((field) =>
                        path.title.toLowerCase().includes(field.toLowerCase().split(" ")[0]),
                      ),
                    )

                    return (
                      <div
                        key={index}
                        className="flex flex-col items-center group cursor-pointer relative z-20"
                        onMouseEnter={() => setShowBranches(skill.name)}
                        onMouseLeave={() => setShowBranches(null)}
                        onClick={() => setSelectedSkill(skill)}
                      >
                        {showBranches === skill.name && skillCareerPaths.length > 0 && (
                          <div className="absolute -top-32 left-1/2 transform -translate-x-1/2 z-30">
                            <div className="flex flex-col items-center space-y-2">
                              {skillCareerPaths.map((path, pathIndex) => (
                                <div key={pathIndex} className="relative">
                                  <div
                                    className="absolute top-full left-1/2 w-px bg-gradient-to-b from-transparent via-primary/60 to-primary/30 transform -translate-x-1/2"
                                    style={{ height: `${120 - pathIndex * 20}px` }}
                                  ></div>

                                  <Card className="w-48 shadow-xl border-0 bg-gradient-to-br from-background to-primary/5 animate-in slide-in-from-top-2 duration-300">
                                    <CardContent className="p-3">
                                      <div className="flex items-center space-x-2 mb-2">
                                        <div
                                          className="w-3 h-3 rounded-full shadow-sm"
                                          style={{ backgroundColor: path.color }}
                                        ></div>
                                        <span className="font-semibold text-sm">{path.title}</span>
                                        <ArrowUpRight className="h-3 w-3 text-primary ml-auto" />
                                      </div>
                                      <div className="text-xs text-muted-foreground mb-2">
                                        {path.salary} • {path.growth} growth
                                      </div>
                                      <div className="flex items-center justify-between">
                                        <Badge
                                          variant="outline"
                                          className="text-xs px-2 py-1"
                                          style={{
                                            borderColor: path.color,
                                            color: path.color,
                                            backgroundColor: `${path.color}10`,
                                          }}
                                        >
                                          {Math.round(getPathCompatibility(path))}% match
                                        </Badge>
                                        <Button size="sm" variant="ghost" className="h-6 px-2 text-xs">
                                          Explore
                                        </Button>
                                      </div>
                                    </CardContent>
                                  </Card>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}

                        <div className="relative">
                          <div
                            className="w-16 h-16 rounded-full border-4 border-background shadow-2xl transition-all duration-500 group-hover:scale-125 group-hover:shadow-3xl z-20 relative overflow-hidden"
                            style={{
                              background: `linear-gradient(135deg, ${getLevelColor(skill.level)}, ${getLevelColor(skill.level)}dd)`,
                            }}
                          >
                            <div className="absolute inset-0 bg-gradient-to-br from-white/20 to-transparent"></div>
                            <div className="w-full h-full rounded-full flex items-center justify-center relative z-10">
                              {skill.impact === "high" && <Star className="h-6 w-6 text-white drop-shadow-lg" />}
                              {skill.certifications && <Award className="h-6 w-6 text-white drop-shadow-lg" />}
                              {skill.impact !== "high" && !skill.certifications && (
                                <div className="w-3 h-3 rounded-full bg-white/80"></div>
                              )}
                            </div>
                          </div>

                          {skill.impact === "high" && (
                            <div
                              className="absolute inset-0 w-16 h-16 rounded-full animate-ping opacity-20"
                              style={{ backgroundColor: getLevelColor(skill.level) }}
                            ></div>
                          )}

                          {skillCareerPaths.length > 0 && (
                            <div className="absolute -top-2 -right-2 w-6 h-6 rounded-full bg-primary shadow-lg flex items-center justify-center animate-pulse">
                              <GitBranch className="h-3 w-3 text-white" />
                            </div>
                          )}
                        </div>

                        <div className="mt-6 text-center group-hover:transform group-hover:scale-105 transition-all duration-300">
                          <Card className="w-40 shadow-lg border-0 bg-background/95 backdrop-blur-sm group-hover:shadow-xl transition-all duration-300">
                            <CardContent className="p-4 space-y-3">
                              <div className="font-semibold text-lg text-foreground">{skill.name}</div>
                              <div className="text-sm text-muted-foreground flex items-center justify-center space-x-1">
                                <Calendar className="h-3 w-3" />
                                <span>
                                  {new Date(skill.acquiredDate).toLocaleDateString("en-US", {
                                    month: "short",
                                    year: "numeric",
                                  })}
                                </span>
                              </div>

                              <div className="space-y-2">
                                <div className="flex items-center justify-between text-sm">
                                  <span className="text-muted-foreground">Proficiency</span>
                                  <span className="font-semibold text-foreground">{skill.level}%</span>
                                </div>
                                <Progress value={skill.level} className="h-2" />
                              </div>

                              <Badge
                                variant="secondary"
                                className="text-xs px-3 py-1"
                                style={{
                                  backgroundColor: `${getImpactColor(skill.impact)}15`,
                                  color: getImpactColor(skill.impact),
                                  borderColor: `${getImpactColor(skill.impact)}30`,
                                }}
                              >
                                {skill.impact} impact
                              </Badge>

                              {skillCareerPaths.length > 0 && (
                                <div className="pt-2 border-t border-border/50">
                                  <div className="flex items-center justify-center space-x-1 text-xs text-primary">
                                    <GitBranch className="h-3 w-3" />
                                    <span>
                                      {skillCareerPaths.length} career path{skillCareerPaths.length > 1 ? "s" : ""}
                                    </span>
                                  </div>
                                </div>
                              )}
                            </CardContent>
                          </Card>
                        </div>

                        {skill.relatedFields.length > 0 && showBranches !== skill.name && (
                          <div className="mt-4 space-y-2 opacity-0 group-hover:opacity-100 transition-all duration-500">
                            {skill.relatedFields.slice(0, 2).map((field, fieldIndex) => (
                              <div key={fieldIndex} className="flex flex-col items-center">
                                <div className="w-px h-6 bg-gradient-to-b from-primary/60 to-transparent"></div>
                                <Card className="shadow-md border-0 bg-primary/5 backdrop-blur-sm">
                                  <CardContent className="px-3 py-2">
                                    <div className="flex items-center space-x-2">
                                      <GitBranch className="h-3 w-3 text-primary" />
                                      <span className="text-xs font-medium text-primary">{field}</span>
                                    </div>
                                  </CardContent>
                                </Card>
                              </div>
                            ))}
                          </div>
                        )}
                      </div>
                    )
                  })}

                  <div className="flex flex-col items-center group cursor-pointer">
                    <div className="w-16 h-16 rounded-full border-4 border-dashed border-primary/40 flex items-center justify-center transition-all duration-500 group-hover:scale-110 group-hover:border-primary group-hover:bg-primary/5">
                      <Plus className="h-8 w-8 text-primary/60 group-hover:text-primary transition-colors" />
                    </div>
                    <div className="mt-6 text-center">
                      <Card className="w-40 shadow-lg border-dashed border-primary/30 bg-primary/5 group-hover:bg-primary/10 transition-all duration-300">
                        <CardContent className="p-4 space-y-2">
                          <div className="font-semibold text-primary">Add Next Skill</div>
                          <div className="text-sm text-primary/70">Continue your journey</div>
                          <Button
                            size="sm"
                            variant="outline"
                            className="w-full border-primary/30 text-primary hover:bg-primary hover:text-primary-foreground bg-transparent"
                          >
                            <Plus className="h-4 w-4 mr-1" />
                            Add Skill
                          </Button>
                        </CardContent>
                      </Card>
                    </div>
                  </div>
                </div>
              </div>

              {selectedSkill && (
                <Card className="border-0 shadow-2xl bg-gradient-to-br from-background to-primary/5 overflow-hidden">
                  <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary/50 via-primary to-primary/50"></div>
                  <CardHeader className="pb-6">
                    <div className="flex items-center justify-between">
                      <CardTitle className="font-playfair text-2xl flex items-center space-x-3">
                        <div
                          className="w-8 h-8 rounded-full shadow-lg"
                          style={{
                            background: `linear-gradient(135deg, ${getLevelColor(selectedSkill.level)}, ${getLevelColor(selectedSkill.level)}dd)`,
                          }}
                        ></div>
                        <span>{selectedSkill.name}</span>
                      </CardTitle>
                      <div className="flex items-center space-x-3">
                        <Badge
                          variant="outline"
                          className="px-4 py-2 text-sm font-medium"
                          style={{
                            color: getImpactColor(selectedSkill.impact),
                            borderColor: getImpactColor(selectedSkill.impact),
                            backgroundColor: `${getImpactColor(selectedSkill.impact)}10`,
                          }}
                        >
                          {selectedSkill.impact} impact
                        </Badge>
                        <Button variant="outline" size="sm" onClick={() => setSelectedSkill(null)}>
                          Close
                        </Button>
                      </div>
                    </div>
                    <CardDescription className="text-base">
                      Acquired in{" "}
                      {new Date(selectedSkill.acquiredDate).toLocaleDateString("en-US", {
                        month: "long",
                        year: "numeric",
                      })}{" "}
                      • {selectedSkill.category} Category
                    </CardDescription>
                  </CardHeader>
                  <CardContent className="space-y-8">
                    <div className="grid md:grid-cols-2 gap-8">
                      <Card className="border-0 bg-background/50 shadow-lg">
                        <CardHeader>
                          <CardTitle className="text-lg">Proficiency Analysis</CardTitle>
                        </CardHeader>
                        <CardContent className="space-y-6">
                          <div className="space-y-3">
                            <div className="flex items-center justify-between">
                              <span className="font-medium">Current Level</span>
                              <span className="text-2xl font-bold text-primary">{selectedSkill.level}%</span>
                            </div>
                            <Progress value={selectedSkill.level} className="h-3" />
                            <div className="text-sm text-muted-foreground">
                              {selectedSkill.level >= 80
                                ? "Expert level - You're highly proficient"
                                : selectedSkill.level >= 60
                                  ? "Proficient - Good working knowledge"
                                  : "Learning - Building foundational skills"}
                            </div>
                          </div>

                          {selectedSkill.certifications && (
                            <div className="space-y-3">
                              <h4 className="font-medium flex items-center space-x-2">
                                <Award className="h-4 w-4 text-amber-500" />
                                <span>Certifications</span>
                              </h4>
                              <div className="flex flex-wrap gap-2">
                                {selectedSkill.certifications.map((cert, index) => (
                                  <Badge
                                    key={index}
                                    variant="secondary"
                                    className="flex items-center space-x-2 px-3 py-2 bg-amber-50 text-amber-800 border-amber-200"
                                  >
                                    <Award className="h-3 w-3" />
                                    <span>{cert}</span>
                                  </Badge>
                                ))}
                              </div>
                            </div>
                          )}
                        </CardContent>
                      </Card>

                      <Card className="border-0 bg-background/50 shadow-lg">
                        <CardHeader>
                          <CardTitle className="text-lg">Career Opportunities</CardTitle>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-3">
                            {selectedSkill.relatedFields.map((field, index) => (
                              <div key={index} className="group">
                                <Card className="border-0 bg-gradient-to-r from-primary/5 to-accent/5 group-hover:from-primary/10 group-hover:to-accent/10 transition-all duration-300 cursor-pointer">
                                  <CardContent className="flex items-center space-x-3 p-4">
                                    <div className="p-2 rounded-lg bg-primary/10 group-hover:bg-primary/20 transition-colors">
                                      <GitBranch className="h-4 w-4 text-primary" />
                                    </div>
                                    <span className="font-medium flex-1">{field}</span>
                                    <ChevronRight className="h-4 w-4 text-muted-foreground group-hover:text-primary transition-colors" />
                                  </CardContent>
                                </Card>
                              </div>
                            ))}
                          </div>
                        </CardContent>
                      </Card>
                    </div>
                  </CardContent>
                </Card>
              )}
            </TabsContent>

            <TabsContent value="paths" className="space-y-6">
              <div>
                <h3 className="font-space-grotesk font-semibold text-lg mb-2">Career Path Analysis</h3>
                <p className="text-muted-foreground mb-6">
                  Based on your current skills, here are the career paths you're most compatible with
                </p>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                  {careerPaths.map((path) => {
                    const compatibility = getPathCompatibility(path)
                    const userSkills = sortedSkills.map((s) => s.name)
                    const matchingSkills = path.skills.filter((skill) => userSkills.includes(skill))
                    const missingSkills = path.skills.filter((skill) => !userSkills.includes(skill))

                    return (
                      <Card
                        key={path.id}
                        className={`cursor-pointer transition-all duration-300 hover:shadow-lg ${
                          hoveredPath === path.id ? "ring-2 ring-primary/20" : ""
                        }`}
                        onMouseEnter={() => setHoveredPath(path.id)}
                        onMouseLeave={() => setHoveredPath(null)}
                      >
                        <CardHeader>
                          <div className="flex items-center justify-between">
                            <CardTitle className="font-space-grotesk text-lg flex items-center space-x-2">
                              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: path.color }}></div>
                              <span>{path.title}</span>
                            </CardTitle>
                            <Badge
                              variant="outline"
                              className={
                                compatibility >= 75
                                  ? "border-green-500 text-green-700"
                                  : compatibility >= 50
                                    ? "border-yellow-500 text-yellow-700"
                                    : "border-red-500 text-red-700"
                              }
                            >
                              {Math.round(compatibility)}% match
                            </Badge>
                          </div>
                          <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                            <span>{path.salary}</span>
                            <span className="text-green-600">{path.growth} growth</span>
                          </div>
                        </CardHeader>
                        <CardContent>
                          <div className="space-y-4">
                            <div>
                              <div className="flex items-center justify-between mb-2">
                                <span className="text-sm font-medium">Compatibility</span>
                                <span className="text-sm">
                                  {matchingSkills.length}/{path.skills.length} skills
                                </span>
                              </div>
                              <Progress value={compatibility} className="h-2" />
                            </div>

                            <div>
                              <h4 className="text-sm font-medium mb-2 text-green-700">Your Skills</h4>
                              <div className="flex flex-wrap gap-1">
                                {matchingSkills.map((skill, index) => (
                                  <Badge
                                    key={index}
                                    variant="secondary"
                                    className="text-xs bg-green-100 text-green-800"
                                  >
                                    {skill}
                                  </Badge>
                                ))}
                              </div>
                            </div>

                            {missingSkills.length > 0 && (
                              <div>
                                <h4 className="text-sm font-medium mb-2 text-orange-700">Skills to Learn</h4>
                                <div className="flex flex-wrap gap-1">
                                  {missingSkills.map((skill, index) => (
                                    <Badge
                                      key={index}
                                      variant="outline"
                                      className="text-xs border-orange-300 text-orange-700"
                                    >
                                      {skill}
                                    </Badge>
                                  ))}
                                </div>
                              </div>
                            )}

                            <Button size="sm" className="w-full" style={{ backgroundColor: path.color }}>
                              <Target className="h-4 w-4 mr-2" />
                              Set as Goal
                            </Button>
                          </div>
                        </CardContent>
                      </Card>
                    )
                  })}
                </div>
              </div>

              <Card>
                <CardHeader>
                  <CardTitle className="font-space-grotesk flex items-center space-x-2">
                    <Zap className="h-5 w-5 text-primary" />
                    <span>Next Steps</span>
                  </CardTitle>
                  <CardDescription>
                    Recommended skills to add to your timeline for maximum career impact
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="grid md:grid-cols-2 gap-4">
                    <div className="space-y-3">
                      <h4 className="font-medium">High Impact Skills</h4>
                      {["TypeScript", "Kubernetes", "TensorFlow", "GraphQL"].map((skill, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 rounded-full bg-red-500"></div>
                            <span className="font-medium">{skill}</span>
                          </div>
                          <Button size="sm" variant="outline">
                            <Plus className="h-4 w-4 mr-1" />
                            Add
                          </Button>
                        </div>
                      ))}
                    </div>
                    <div className="space-y-3">
                      <h4 className="font-medium">Trending Skills</h4>
                      {["Next.js", "Terraform", "Rust", "WebAssembly"].map((skill, index) => (
                        <div key={index} className="flex items-center justify-between p-3 border rounded-lg">
                          <div className="flex items-center space-x-3">
                            <div className="w-2 h-2 rounded-full bg-blue-500"></div>
                            <span className="font-medium">{skill}</span>
                          </div>
                          <Button size="sm" variant="outline">
                            <Plus className="h-4 w-4 mr-1" />
                            Add
                          </Button>
                        </div>
                      ))}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </TabsContent>
          </Tabs>
        </CardContent>
      </Card>
    </div>
  )
}
