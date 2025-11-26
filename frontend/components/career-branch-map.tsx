"use client"

import { useState, useMemo, useEffect } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { GitBranch, ArrowRight, Zap, Target, Briefcase, TrendingUp, Users, Clock } from "lucide-react"
import { cn } from "@/lib/utils"

interface Skill {
  id: string
  name: string
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
}

interface BranchInfo {
  path: CareerPath
  acquiredSkills: number
  totalRequired: number
  coverage: number
  isAccessible: boolean
  missingSkills: string[]
}

interface CareerBranchMapProps {
  selectedPath: CareerPath
  completedSkills: Set<string>
  allPaths: CareerPath[]
  allSkills: { id: string; name: string }[]
  onPathSelect: (pathId: string) => void
}

export function CareerBranchMap({
  selectedPath,
  completedSkills,
  allPaths,
  allSkills,
  onPathSelect,
}: CareerBranchMapProps) {
  const [animateIn, setAnimateIn] = useState(false)

  useEffect(() => {
    setAnimateIn(true)
  }, [])

  const branches = useMemo<BranchInfo[]>(() => {
    return allPaths.map((path) => {
      const requiredSet = new Set(path.requiredSkills)
      const acquiredInPath = Array.from(completedSkills).filter((s) => requiredSet.has(s)).length
      const coverage = requiredSet.size > 0 ? acquiredInPath / requiredSet.size : 0
      const missingSkills = path.requiredSkills.filter((s) => !completedSkills.has(s))
      const isAccessible = coverage >= 0.5 && path.id !== selectedPath.id

      return {
        path,
        acquiredSkills: acquiredInPath,
        totalRequired: requiredSet.size,
        coverage,
        isAccessible,
        missingSkills,
      }
    })
  }, [completedSkills, allPaths, selectedPath.id])

  const accessibleBranches = branches.filter((b) => b.isAccessible && b.coverage > 0)
  const fullyAccessibleBranches = accessibleBranches.filter((b) => b.coverage === 1)

  if (accessibleBranches.length === 0) {
    return null
  }

  const BranchCard = ({
    branch,
    isFullyAccessible,
  }: {
    branch: BranchInfo
    isFullyAccessible: boolean
  }) => (
    <div
      className={cn(
        "group relative p-5 bg-background border-2 rounded-lg transition-all duration-300 hover:shadow-lg cursor-pointer",
        isFullyAccessible
          ? "border-emerald-500/30 hover:border-emerald-500 hover:shadow-emerald-500/20"
          : "border-amber-500/30 hover:border-amber-500 hover:shadow-amber-500/20",
      )}
      onClick={() => onPathSelect(branch.path.id)}
    >
      <div className="space-y-4">
        {/* Header */}
        <div className="flex items-start justify-between">
          <div className="flex-1">
            <h5 className="font-bold text-lg text-foreground group-hover:text-primary transition-colors">
              {branch.path.title}
            </h5>
            <p className="text-sm text-muted-foreground mt-1">{branch.path.description}</p>
          </div>
          <div
            className={cn(
              "h-8 px-3 rounded-full text-xs font-bold flex items-center whitespace-nowrap ml-2",
              isFullyAccessible
                ? "bg-emerald-500/20 text-emerald-700 dark:text-emerald-300"
                : "bg-amber-500/20 text-amber-700 dark:text-amber-300",
            )}
          >
            {isFullyAccessible ? "✓ Ready" : `${Math.round(branch.coverage * 100)}%`}
          </div>
        </div>

        {/* Meta Information */}
        <div className="grid grid-cols-2 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <TrendingUp className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">
              Growth: <span className="font-semibold text-foreground">{branch.path.growth}</span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Briefcase className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">
              Salary: <span className="font-semibold text-foreground">{branch.path.salary}</span>
            </span>
          </div>
          {branch.path.industry && (
            <div className="flex items-center gap-2">
              <Users className="h-4 w-4 text-primary" />
              <span className="text-muted-foreground">
                Industry: <span className="font-semibold text-foreground">{branch.path.industry}</span>
              </span>
            </div>
          )}
          <div className="flex items-center gap-2">
            <Clock className="h-4 w-4 text-primary" />
            <span className="text-muted-foreground">
              Level: <span className="font-semibold text-foreground capitalize">{branch.path.level}</span>
            </span>
          </div>
        </div>

        {/* Skills Progress */}
        {!isFullyAccessible && (
          <div className="space-y-3 pt-2 border-t border-border/50">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground font-medium">
                {branch.acquiredSkills} of {branch.totalRequired} skills acquired
              </span>
              <span
                className={cn(
                  "font-bold",
                  branch.missingSkills.length > 0
                    ? "text-amber-600 dark:text-amber-400"
                    : "text-emerald-600 dark:text-emerald-400",
                )}
              >
                {branch.missingSkills.length} to learn
              </span>
            </div>

            {/* Progress bar */}
            <div className="w-full h-2.5 bg-muted rounded-full overflow-hidden">
              <div
                className={cn(
                  "h-full transition-all duration-300",
                  isFullyAccessible ? "bg-emerald-500" : "bg-amber-500",
                )}
                style={{ width: `${branch.coverage * 100}%` }}
              />
            </div>

            {/* Missing skills */}
            <div className="space-y-2">
              <p className="text-xs font-semibold text-muted-foreground">Skills to acquire:</p>
              <div className="flex flex-wrap gap-2">
                {branch.missingSkills.slice(0, 4).map((skillId) => {
                  const skill = allSkills.find((s) => s.id === skillId)
                  return (
                    <Badge
                      key={skillId}
                      variant="secondary"
                      className="text-xs bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800"
                    >
                      {skill?.name || skillId}
                    </Badge>
                  )
                })}
                {branch.missingSkills.length > 4 && (
                  <Badge
                    variant="secondary"
                    className="text-xs bg-amber-500/10 text-amber-700 dark:text-amber-300 border-amber-200 dark:border-amber-800"
                  >
                    +{branch.missingSkills.length - 4} more
                  </Badge>
                )}
              </div>
            </div>
          </div>
        )}

        {/* Call to Action */}
        <Button
          size="sm"
          className={cn(
            "w-full",
            isFullyAccessible
              ? "bg-emerald-600 hover:bg-emerald-700 text-white"
              : "border-amber-200 hover:bg-amber-50 dark:hover:bg-amber-900/20 bg-transparent",
          )}
          variant={isFullyAccessible ? "default" : "outline"}
          onClick={() => onPathSelect(branch.path.id)}
        >
          {isFullyAccessible ? "Switch to this path" : "Explore Path"}
          <ArrowRight className="h-3 w-3 ml-2" />
        </Button>
      </div>
    </div>
  )

  return (
    <Card className="border-2 bg-gradient-to-br from-background to-primary/5 border-primary/10">
      <CardHeader>
        <div className="space-y-1">
          <CardTitle className="flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-primary" />
            Career Path Branches Unlocked!
          </CardTitle>
          <CardDescription>Based on your acquired skills, explore these career opportunities</CardDescription>
        </div>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {/* Fully Accessible Paths */}
          {fullyAccessibleBranches.length > 0 && (
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-emerald-900 dark:text-emerald-100 flex items-center gap-2">
                <Target className="h-4 w-4" />
                Ready to Switch
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {fullyAccessibleBranches.map((branch) => (
                  <BranchCard key={branch.path.id} branch={branch} isFullyAccessible={true} />
                ))}
              </div>
            </div>
          )}

          {/* Partially Accessible Paths */}
          {accessibleBranches.filter((b) => b.coverage < 1).length > 0 && (
            <div className="space-y-4">
              <h4 className="text-sm font-bold text-amber-900 dark:text-amber-100 flex items-center gap-2">
                <Zap className="h-4 w-4" />
                Almost There
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {accessibleBranches
                  .filter((b) => b.coverage < 1)
                  .map((branch) => (
                    <BranchCard key={branch.path.id} branch={branch} isFullyAccessible={false} />
                  ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}
