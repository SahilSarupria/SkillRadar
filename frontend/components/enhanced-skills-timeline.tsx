"use client"

import { useState, useCallback, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { GitBranch, Target, CheckCircle2, Circle, MapPin, Trophy, Loader2 } from "lucide-react"
import { cn } from "@/lib/utils"
import { CareerBranchMap } from "@/components/career-branch-map"
import { SkillsBranchMapVisual } from "@/components/skills-branch-map-visual"
import { useToast } from "@/hooks/use-toast"

interface Skill {
  id: string
  name: string
  proficiency: number
}

interface Milestone {
  id: string
  title: string
  skills: Skill[]
  completed: boolean
  order: number
}

interface CareerPath {
  id: string
  title: string
  description: string
  requiredSkills: string[]
  salary: string
  growth: string
  level: "entry" | "mid" | "senior"
  color: string
  industry?: string
  matchedIndirectSkillsCount?: number
}

export function EnhancedSkillsTimeline() {
  const [selectedPath, setSelectedPath] = useState<string | null>(null)
  const [completedSkills, setCompletedSkills] = useState<Set<string>>(new Set())
  const [milestones, setMilestones] = useState<Milestone[]>([])
  const [careerPaths, setCareerPaths] = useState<CareerPath[]>([])
  const [allSkills, setAllSkills] = useState<Skill[]>([])
  const [showBranches, setShowBranches] = useState(false)
  const [detectedBranches, setDetectedBranches] = useState<CareerPath[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [isLoadingPath, setIsLoadingPath] = useState(false)
  const [indirectBranches, setIndirectBranches] = useState<CareerPath[]>([])
  const [isLoadingBranches, setIsLoadingBranches] = useState(false)
  const { toast } = useToast()

  useEffect(() => {
    async function fetchJobRoles() {
      try {
        setIsLoading(true)
        const res = await fetch("http://localhost:8000/api/skills/job-roles/", {
          credentials: "include",
        })
        if (!res.ok) throw new Error("Failed to fetch job roles")

        const data = await res.json()
        const jobRoles = data.results || []

        const transformedPaths: CareerPath[] = jobRoles.map((job: any) => ({
          id: String(job.id),
          title: job.title || "",
          description: job.description || "Specialize in this career path",
          requiredSkills: [],
          salary: job.salary || "Competitive",
          growth: job.growth_rate ? `+${job.growth_rate}%` : "+15%",
          level: (job.level || "mid") as "entry" | "mid" | "senior",
          color: getColorForLevel(job.level),
          industry: job.industry,
        }))

        setCareerPaths(transformedPaths)
        if (transformedPaths.length > 0) {
          setSelectedPath(String(transformedPaths[0].id))
        }
      } catch (error) {
        console.error("[v0] Error fetching job roles:", error)
        toast({
          title: "Error loading job roles",
          description: "Failed to fetch job roles from server",
          variant: "destructive",
        })
      } finally {
        setIsLoading(false)
      }
    }

    fetchJobRoles()
  }, [toast])

  useEffect(() => {
    async function fetchPathDetails() {
      if (!selectedPath) return

      try {
        setIsLoadingPath(true)
        const res = await fetch(`http://localhost:8000/api/skills/job-roles/get-goal/${selectedPath}/`, {
          credentials: "include",
        })
        if (!res.ok) throw new Error("Failed to fetch path details")

        const goalData = await res.json()
        const requiredSkillsData = goalData.required_skills || []

        const skillObjects: Skill[] = requiredSkillsData.map((skillName: string, index: number) => ({
          id: `skill-${index}-${skillName.toLowerCase().replace(/\s+/g, "-")}`,
          name: skillName,
          proficiency: 0,
        }))

        setAllSkills(skillObjects)

        setCareerPaths((prev) =>
          prev.map((p) => (p.id === selectedPath ? { ...p, requiredSkills: skillObjects.map((s) => s.id) } : p)),
        )

        setCompletedSkills(new Set())
      } catch (error) {
        console.error("[v0] Error fetching path details:", error)
        toast({
          title: "Error loading path details",
          description: "Failed to fetch required skills",
          variant: "destructive",
        })
      } finally {
        setIsLoadingPath(false)
      }
    }

    fetchPathDetails()
  }, [selectedPath, toast])

  useEffect(() => {
    const path = careerPaths.find((p) => p.id === selectedPath)
    if (!path) return

    const newMilestones: Milestone[] = allSkills.map((skill, index) => ({
      id: skill.id,
      title: skill.name,
      skills: [skill],
      completed: completedSkills.has(skill.id),
      order: index,
    }))

    setMilestones(newMilestones)
  }, [selectedPath, completedSkills, allSkills, careerPaths])

  const detectAlternativePaths = useCallback(() => {
    const acquiredSkillIds = Array.from(completedSkills)

    const pathScores = careerPaths
      .map((path) => {
        if (path.id === selectedPath) return null

        const requiredSet = new Set(path.requiredSkills)
        const acquiredInPath = acquiredSkillIds.filter((s) => requiredSet.has(s)).length
        const coverage = requiredSet.size > 0 ? acquiredInPath / requiredSet.size : 0

        if (coverage >= 0.3 && coverage < 1) {
          return { path, coverage }
        }
        return null
      })
      .filter(Boolean) as Array<{ path: CareerPath; coverage: number }>

    return pathScores.sort((a, b) => b.coverage - a.coverage).map((p) => p.path)
  }, [completedSkills, selectedPath, careerPaths])

  const detectIndirectSkillBranches = useCallback(async () => {
    const currentPath = careerPaths.find((p) => p.id === selectedPath)
    if (!currentPath) return

    const requiredSkillSet = new Set(currentPath.requiredSkills)

    // Find acquired skills that are NOT required for the current path
    const indirectSkills = Array.from(completedSkills).filter((skillId) => !requiredSkillSet.has(skillId))

    if (indirectSkills.length === 0) {
      setIndirectBranches([])
      return
    }

    try {
      setIsLoadingBranches(true)

      // Fetch all job roles and find which ones match the indirect skills
      const res = await fetch("http://localhost:8000/api/skills/job-roles/", {
        credentials: "include",
      })
      if (!res.ok) throw new Error("Failed to fetch job roles for branching")

      const data = await res.json()
      const jobRoles = data.results || []

      // For each job role, check if it requires any of the indirect skills
      const branchesPromises = jobRoles.map(async (job: any) => {
        if (String(job.id) === selectedPath) return null

        try {
          const detailRes = await fetch(`http://localhost:8000/api/skills/job-roles/get-goal/${job.id}/`, {
            credentials: "include",
          })
          if (!detailRes.ok) return null

          const goalData = await detailRes.json()
          const requiredSkillsData = goalData.required_skills || []

          // Check how many indirect skills this role requires
          const matchingIndirectSkills = indirectSkills.filter((skillId) => {
            const skillObj = allSkills.find((s) => s.id === skillId)
            return skillObj && requiredSkillsData.includes(skillObj.name)
          })

          if (matchingIndirectSkills.length > 0) {
            const requiredSkillObjects = requiredSkillsData.map((skillName: string, index: number) => ({
              id: `skill-${index}-${skillName.toLowerCase().replace(/\s+/g, "-")}`,
              name: skillName,
            }))

            return {
              id: String(job.id),
              title: job.title || "",
              description: job.description || "Expand your career with this path",
              requiredSkills: requiredSkillObjects.map((s) => s.id),
              salary: job.salary || "Competitive",
              growth: job.growth_rate ? `+${job.growth_rate}%` : "+15%",
              level: (job.level || "mid") as "entry" | "mid" | "senior",
              color: getColorForLevel(job.level),
              industry: job.industry,
              matchedIndirectSkillsCount: matchingIndirectSkills.length,
            }
          }

          return null
        } catch (error) {
          console.error("[v0] Error fetching branch role details:", error)
          return null
        }
      })

      const branchResults = await Promise.all(branchesPromises)
      const validBranches = branchResults.filter(Boolean) as Array<CareerPath & { matchedIndirectSkillsCount: number }>

      // Sort by number of matched indirect skills
      const sortedBranches = validBranches.sort(
        (a, b) => (b.matchedIndirectSkillsCount || 0) - (a.matchedIndirectSkillsCount || 0),
      )

      setIndirectBranches(sortedBranches)
    } catch (error) {
      console.error("[v0] Error detecting indirect branches:", error)
    } finally {
      setIsLoadingBranches(false)
    }
  }, [selectedPath, completedSkills, allSkills, careerPaths])

  const handleSkillComplete = useCallback(
    (skillId: string) => {
      setCompletedSkills((prev) => {
        const newSet = new Set(prev)
        if (newSet.has(skillId)) {
          newSet.delete(skillId)
        } else {
          newSet.add(skillId)
        }
        return newSet
      })

      const branches = detectAlternativePaths()
      if (branches.length > 0) {
        setDetectedBranches(branches)
        setShowBranches(true)
      }

      detectIndirectSkillBranches()
    },
    [detectAlternativePaths, detectIndirectSkillBranches],
  )

  useEffect(() => {
    detectIndirectSkillBranches()
  }, [selectedPath, detectIndirectSkillBranches])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="space-y-4 text-center">
          <Loader2 className="h-8 w-8 animate-spin mx-auto text-primary" />
          <p className="text-muted-foreground">Loading your career paths...</p>
        </div>
      </div>
    )
  }

  const currentPath = careerPaths.find((p) => p.id === selectedPath)
  const totalRequired = currentPath?.requiredSkills.length || 0
  const completedCount = milestones.filter((m) => completedSkills.has(m.id)).length
  const completionPercentage = totalRequired > 0 ? (completedCount / totalRequired) * 100 : 0

  return (
    <div className="space-y-8 p-6 max-w-7xl mx-auto">
      <div className="space-y-2">
        <h1 className="text-4xl font-bold text-foreground flex items-center gap-2">
          <MapPin className="h-8 w-8 text-primary" />
          Career Path Timeline
        </h1>
        <p className="text-lg text-muted-foreground">
          Visualize your journey with dynamic milestones that adapt as you acquire new skills
        </p>
      </div>

      <Card className="border-2 border-primary/10 bg-gradient-to-br from-background to-primary/5">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Target className="h-5 w-5 text-primary" />
            Select Your Target Role
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4 gap-2">
            {careerPaths.map((path) => (
              <Button
                key={path.id}
                onClick={() => setSelectedPath(path.id)}
                variant={selectedPath === path.id ? "default" : "outline"}
                className="h-auto flex flex-col items-start p-3 justify-start"
                disabled={isLoadingPath && selectedPath === path.id}
              >
                <span className="font-semibold text-sm">{path.title}</span>
                <span className="text-xs text-muted-foreground mt-1">{path.industry || path.level}</span>
                {path.salary && <span className="text-xs font-medium mt-1">{path.salary}</span>}
              </Button>
            ))}
          </div>

          {currentPath && !isLoadingPath && (
            <div className="mt-6 p-4 bg-background rounded-lg border border-border/50">
              <div className="space-y-3">
                <div className="flex items-center justify-between">
                  <span className="font-semibold text-foreground">{currentPath.title}</span>
                  <span className="text-sm font-medium text-primary">{completionPercentage.toFixed(0)}% Complete</span>
                </div>
                <Progress value={completionPercentage} className="h-3" />
                <p className="text-sm text-muted-foreground">{currentPath.description}</p>
                <div className="flex gap-2 flex-wrap">
                  {currentPath.industry && <Badge variant="secondary">{currentPath.industry}</Badge>}
                  <Badge variant="outline">{currentPath.level}</Badge>
                  <Badge variant="outline">{currentPath.growth}</Badge>
                </div>
              </div>
            </div>
          )}

          {isLoadingPath && (
            <div className="flex items-center gap-2 text-muted-foreground">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Loading path details...</span>
            </div>
          )}
        </CardContent>
      </Card>

      {!isLoadingPath && (
        <Card className="border-2 border-primary/10">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="flex items-center gap-2">
                  <GitBranch className="h-5 w-5 text-primary" />
                  Your Learning Journey
                </CardTitle>
                <CardDescription>Complete milestones in any order. Non-required skills open new paths.</CardDescription>
              </div>
              <div className="flex items-center gap-2">
                <CircularProgress value={completedCount} total={totalRequired} />
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-6">
              <div className="relative pl-8 pb-6 border-l-2 border-primary/30">
                <div className="absolute -left-4 top-0 w-6 h-6 bg-primary rounded-full border-4 border-background shadow-lg flex items-center justify-center">
                  <Circle className="h-2 w-2 text-background fill-background" />
                </div>
                <div className="space-y-1">
                  <p className="text-xs font-semibold text-primary uppercase tracking-wide">Current Position</p>
                  <h3 className="text-lg font-bold text-foreground">Start Your Journey</h3>
                  <p className="text-sm text-muted-foreground">
                    {totalRequired} skills to acquire for {currentPath?.title}
                  </p>
                </div>
              </div>

              <div className="space-y-4">
                {milestones.map((milestone, index) => {
                  const isCompleted = completedSkills.has(milestone.id)
                  const isNextMilestone = index === completedCount

                  return (
                    <div key={milestone.id} className="relative">
                      {index < milestones.length - 1 && (
                        <div
                          className={cn(
                            "absolute left-3 top-12 w-0.5 h-8 transition-colors",
                            isCompleted ? "bg-primary" : "bg-primary/20",
                          )}
                        />
                      )}

                      <div className={cn("pl-8 pb-6 relative", isCompleted && "opacity-75")}>
                        <button
                          onClick={() => handleSkillComplete(milestone.id)}
                          className={cn(
                            "absolute -left-4 top-0 w-6 h-6 rounded-full border-4 border-background transition-all duration-300",
                            isCompleted
                              ? "bg-primary shadow-lg shadow-primary/50"
                              : isNextMilestone
                                ? "bg-primary/30 border-primary/50 hover:bg-primary/50"
                                : "bg-muted hover:bg-muted/80",
                          )}
                        >
                          {isCompleted ? (
                            <CheckCircle2 className="h-full w-full text-background p-1" />
                          ) : (
                            <Circle className="h-full w-full text-muted-foreground p-1" />
                          )}
                        </button>

                        <Card
                          className={cn(
                            "cursor-pointer transition-all duration-300 hover:shadow-md",
                            isCompleted && "bg-primary/5 border-primary/30",
                            isNextMilestone && "ring-2 ring-primary/50 shadow-md",
                          )}
                        >
                          <CardContent className="p-4 space-y-3">
                            <div className="flex items-start justify-between">
                              <div className="space-y-1 flex-1">
                                <div className="flex items-center gap-2">
                                  <h4 className="font-bold text-foreground">{milestone.title}</h4>
                                  {isCompleted && (
                                    <Badge className="bg-primary/20 text-primary border-0">Mastered</Badge>
                                  )}
                                  {isNextMilestone && !isCompleted && (
                                    <Badge variant="outline" className="border-primary/50 text-primary bg-primary/5">
                                      Next Up
                                    </Badge>
                                  )}
                                </div>
                                <p className="text-xs text-muted-foreground">
                                  Step {index + 1} of {totalRequired}
                                </p>
                              </div>
                            </div>

                            <div className="space-y-2">
                              <div className="flex items-center justify-between text-xs">
                                <span className="text-muted-foreground">Proficiency</span>
                                <span className="font-semibold text-foreground">{isCompleted ? "100" : "0"}%</span>
                              </div>
                              <Progress value={isCompleted ? 100 : 0} className="h-2" />
                            </div>

                            <div className="pt-2 flex gap-2">
                              <Button
                                size="sm"
                                variant={isCompleted ? "secondary" : "default"}
                                className="w-full"
                                onClick={() => handleSkillComplete(milestone.id)}
                              >
                                {isCompleted ? (
                                  <>
                                    <CheckCircle2 className="h-4 w-4 mr-2" />
                                    Mark as Incomplete
                                  </>
                                ) : (
                                  <>
                                    <CheckCircle2 className="h-4 w-4 mr-2" />
                                    Mark Complete
                                  </>
                                )}
                              </Button>
                            </div>
                          </CardContent>
                        </Card>
                      </div>
                    </div>
                  )
                })}
              </div>

              {completedCount === totalRequired && totalRequired > 0 && (
                <div className="relative pl-8 pb-6 border-l-2 border-primary">
                  <div className="absolute -left-4 top-0 w-6 h-6 bg-primary rounded-full border-4 border-background shadow-lg shadow-primary/50 flex items-center justify-center">
                    <Trophy className="h-3 w-3 text-background" />
                  </div>
                  <div className="space-y-2 bg-primary/10 border border-primary/30 rounded-lg p-4">
                    <p className="text-xs font-semibold text-primary uppercase tracking-wide">
                      🎉 Achievement Unlocked
                    </p>
                    <h3 className="text-lg font-bold text-foreground">You&apos;re ready for {currentPath?.title}!</h3>
                    <p className="text-sm text-muted-foreground">
                      Congratulations! You&apos;ve completed all required skills.
                    </p>
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {isLoadingBranches && (
        <Card className="border-2 border-blue-500/10 bg-gradient-to-br from-background to-blue-500/5">
          <CardContent className="pt-6">
            <div className="flex items-center gap-3 text-center justify-center">
              <Loader2 className="h-5 w-5 animate-spin text-primary" />
              <p className="text-muted-foreground">Detecting career branches based on your skills...</p>
            </div>
          </CardContent>
        </Card>
      )}

      {indirectBranches.length > 0 && (
        <SkillsBranchMapVisual
          currentPath={currentPath || { id: selectedPath || "", title: "Loading...", requiredSkills: [] }}
          indirectBranches={indirectBranches}
          directBranches={detectedBranches.map((branch) => ({
            path: branch,
            coverage: 0,
            missingSkills: [],
          }))}
          allSkills={allSkills}
          completedSkills={completedSkills}
          onPathSelect={(pathId) => setSelectedPath(pathId)}
        />
      )}

      {detectedBranches.length > 0 && !indirectBranches.length && (
        <CareerBranchMap
          selectedPath={currentPath}
          completedSkills={completedSkills}
          allPaths={careerPaths}
          allSkills={allSkills}
          onPathSelect={(pathId) => {
            setSelectedPath(pathId)
            setCompletedSkills(new Set())
            setDetectedBranches([])
            setIndirectBranches([])
          }}
        />
      )}
    </div>
  )
}

function CircularProgress({ value, total }: { value: number; total: number }) {
  const percentage = total > 0 ? (value / total) * 100 : 0
  const circumference = 2 * Math.PI * 45

  return (
    <div className="relative w-24 h-24 flex items-center justify-center">
      <svg className="absolute -rotate-90" width="96" height="96" viewBox="0 0 96 96">
        <circle cx="48" cy="48" r="45" fill="none" stroke="currentColor" strokeWidth="3" className="text-primary/10" />
        <circle
          cx="48"
          cy="48"
          r="45"
          fill="none"
          stroke="currentColor"
          strokeWidth="3"
          strokeDasharray={circumference}
          strokeDashoffset={circumference - (percentage / 100) * circumference}
          className="text-primary transition-all duration-500"
          strokeLinecap="round"
        />
      </svg>
      <div className="text-center">
        <div className="text-2xl font-bold text-foreground">{value}</div>
        <div className="text-xs text-muted-foreground">of {total}</div>
      </div>
    </div>
  )
}

function getColorForLevel(level: string): string {
  const colorMap: Record<string, string> = {
    entry: "#3b82f6",
    mid: "#10b981",
    senior: "#f59e0b",
  }
  return colorMap[level] || "#6366f1"
}
