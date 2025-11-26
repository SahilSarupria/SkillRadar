"use client"

import { useState, useMemo } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import { GitBranch, Lightbulb, ArrowRight, TrendingUp, Briefcase, Users, Clock } from "lucide-react"
import { cn } from "@/lib/utils"

interface CareerNode {
  id: string
  title: string
  description: string
  salary: string
  growth: string
  level: "entry" | "mid" | "senior"
  industry?: string
  requiredSkills: string[]
  matchedIndirectSkills: number
  isIndirectBranch: boolean
  isCurrentPath: boolean
}

interface SkillsBranchMapVisualProps {
  currentPath: { id: string; title: string; requiredSkills: string[] }
  indirectBranches: any[]
  directBranches: any[]
  allSkills: { id: string; name: string }[]
  completedSkills: Set<string>
  onPathSelect: (pathId: string) => void
}

export function SkillsBranchMapVisual({
  currentPath,
  indirectBranches = [],
  directBranches = [],
  allSkills,
  completedSkills,
  onPathSelect,
}: SkillsBranchMapVisualProps) {
  const [nodes, setNodes] = useState<CareerNode[]>([])
  const [selectedBranch, setSelectedBranch] = useState<string | null>(null)

  // Organize nodes with visual positioning
  const organizedNodes = useMemo(() => {
    const organized: CareerNode[] = [
      {
        id: currentPath.id,
        title: currentPath.title,
        description: "Your current path",
        salary: "Competitive",
        growth: "+15%",
        level: "mid" as const,
        requiredSkills: currentPath.requiredSkills,
        matchedIndirectSkills: 0,
        isIndirectBranch: false,
        isCurrentPath: true,
      },
    ]

    // Add indirect branches
    indirectBranches.forEach((branch, idx) => {
      organized.push({
        id: branch.id,
        title: branch.title,
        description: branch.description,
        salary: branch.salary,
        growth: branch.growth,
        level: branch.level,
        industry: branch.industry,
        requiredSkills: branch.requiredSkills,
        matchedIndirectSkills: branch.matchedIndirectSkillsCount || 0,
        isIndirectBranch: true,
        isCurrentPath: false,
      })
    })

    // Add direct branches
    directBranches.forEach((branch, idx) => {
      organized.push({
        id: branch.path.id,
        title: branch.path.title,
        description: branch.path.description,
        salary: branch.path.salary,
        growth: branch.path.growth,
        level: branch.path.level,
        industry: branch.path.industry,
        requiredSkills: branch.path.requiredSkills,
        matchedIndirectSkills: 0,
        isIndirectBranch: false,
        isCurrentPath: false,
      })
    })

    return organized
  }, [currentPath, indirectBranches, directBranches])

  if (!indirectBranches || indirectBranches.length === 0) {
    return null
  }

  const svgWidth = 1000
  const svgHeight = 600
  const centerX = svgWidth / 2
  const centerY = svgHeight / 2
  const radius = 150

  // Calculate positions for nodes in a circular layout
  const nodePositions = organizedNodes.map((node, idx) => {
    if (node.isCurrentPath) {
      return { id: node.id, x: centerX, y: centerY }
    }
    const angle = (idx / organizedNodes.length) * Math.PI * 2
    const x = centerX + radius * Math.cos(angle)
    const y = centerY + radius * Math.sin(angle)
    return { id: node.id, x, y }
  })

  return (
    <Card className="border-2 border-purple-200 dark:border-purple-900 bg-gradient-to-br from-purple-50/50 to-background dark:from-purple-950/10">
      <CardHeader>
        <CardTitle className="flex items-center gap-2">
          <GitBranch className="h-5 w-5 text-purple-600 dark:text-purple-400" />
          Career Branching Map
        </CardTitle>
        <CardDescription>
          Visual representation of your career paths based on acquired skills. Click branches to explore new
          opportunities.
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-6">
        {/* SVG Map */}
        <div className="w-full bg-background rounded-lg border border-border/50 overflow-x-auto">
          <svg width={svgWidth} height={svgHeight} className="mx-auto">
            <defs>
              <marker id="arrowIndirect" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 Z" fill="#a855f7" />
              </marker>
              <marker id="arrowDirect" markerWidth="10" markerHeight="10" refX="5" refY="5" orient="auto">
                <path d="M 0 0 L 10 5 L 0 10 Z" fill="#f59e0b" />
              </marker>
            </defs>

            {/* Draw connections */}
            {organizedNodes.map((node, idx) => {
              if (node.isCurrentPath) return null
              const fromPos = nodePositions[0] // Current path
              const toPos = nodePositions[idx]

              return (
                <line
                  key={`line-${node.id}`}
                  x1={fromPos.x}
                  y1={fromPos.y}
                  x2={toPos.x}
                  y2={toPos.y}
                  stroke={node.isIndirectBranch ? "#a855f7" : "#f59e0b"}
                  strokeWidth={node.isIndirectBranch ? 3 : 2}
                  strokeDasharray={node.isIndirectBranch ? "5,5" : "0"}
                  opacity="0.6"
                  markerEnd={node.isIndirectBranch ? "url(#arrowIndirect)" : "url(#arrowDirect)"}
                />
              )
            })}

            {/* Draw nodes */}
            {nodePositions.map((pos, idx) => {
              const node = organizedNodes[idx]
              const isHovered = selectedBranch === node.id

              return (
                <g key={`node-${node.id}`}>
                  {/* Glow effect for hovered nodes */}
                  {isHovered && (
                    <circle
                      cx={pos.x}
                      cy={pos.y}
                      r={65}
                      fill={node.isIndirectBranch ? "#a855f7" : "#f59e0b"}
                      opacity="0.1"
                    />
                  )}

                  {/* Main node circle */}
                  <circle
                    cx={pos.x}
                    cy={pos.y}
                    r={55}
                    fill={node.isCurrentPath ? "#3b82f6" : node.isIndirectBranch ? "#a855f7" : "#f59e0b"}
                    opacity={node.isCurrentPath ? 1 : isHovered ? 0.9 : 0.8}
                    stroke={node.isCurrentPath ? "#1d4ed8" : node.isIndirectBranch ? "#7c3aed" : "#d97706"}
                    strokeWidth="2"
                    className="cursor-pointer transition-opacity"
                    onMouseEnter={() => setSelectedBranch(node.id)}
                    onMouseLeave={() => setSelectedBranch(null)}
                    onClick={() => !node.isCurrentPath && onPathSelect(node.id)}
                  />

                  {/* Node icon/label */}
                  <text
                    x={pos.x}
                    y={pos.y - 10}
                    textAnchor="middle"
                    fill="white"
                    fontSize="12"
                    fontWeight="bold"
                    className="pointer-events-none"
                  >
                    {node.title.split(" ")[0]}
                  </text>
                  <text
                    x={pos.x}
                    y={pos.y + 10}
                    textAnchor="middle"
                    fill="white"
                    fontSize="11"
                    className="pointer-events-none"
                  >
                    {node.matchedIndirectSkills > 0 ? `+${node.matchedIndirectSkills} skills` : node.level}
                  </text>
                </g>
              )
            })}
          </svg>
        </div>

        {/* Branch Details */}
        <div className="space-y-4">
          {/* Indirect Branches */}
          {indirectBranches.length > 0 && (
            <div className="space-y-3">
              <h4 className="text-sm font-bold text-purple-700 dark:text-purple-300 flex items-center gap-2">
                <Lightbulb className="h-4 w-4" />
                New Career Branches (From Extra Skills)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {indirectBranches.map((branch) => (
                  <BranchCard
                    key={branch.id}
                    branch={branch}
                    isIndirect={true}
                    isSelected={selectedBranch === branch.id}
                    onSelect={() => {
                      setSelectedBranch(branch.id)
                      onPathSelect(branch.id)
                    }}
                    onHover={() => setSelectedBranch(branch.id)}
                    onHoverEnd={() => setSelectedBranch(null)}
                  />
                ))}
              </div>
            </div>
          )}

          {/* Direct Branches */}
          {directBranches.length > 0 && (
            <div className="space-y-3 pt-4 border-t border-border/50">
              <h4 className="text-sm font-bold text-amber-700 dark:text-amber-300 flex items-center gap-2">
                <TrendingUp className="h-4 w-4" />
                Other Career Paths (Partial Match)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                {directBranches.map((branch) => (
                  <BranchCard
                    key={branch.path.id}
                    branch={branch.path}
                    isIndirect={false}
                    coverage={branch.coverage}
                    missingSkills={branch.missingSkills}
                    isSelected={selectedBranch === branch.path.id}
                    onSelect={() => {
                      setSelectedBranch(branch.path.id)
                      onPathSelect(branch.path.id)
                    }}
                    onHover={() => setSelectedBranch(branch.path.id)}
                    onHoverEnd={() => setSelectedBranch(null)}
                  />
                ))}
              </div>
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
}

interface BranchCardProps {
  branch: any
  isIndirect: boolean
  coverage?: number
  missingSkills?: string[]
  isSelected: boolean
  onSelect: () => void
  onHover: () => void
  onHoverEnd: () => void
}

function BranchCard({
  branch,
  isIndirect,
  coverage = 0,
  missingSkills = [],
  isSelected,
  onSelect,
  onHover,
  onHoverEnd,
}: BranchCardProps) {
  return (
    <div
      className={cn(
        "p-4 bg-background rounded-lg border-2 transition-all cursor-pointer",
        isIndirect
          ? isSelected
            ? "border-purple-500 shadow-lg shadow-purple-500/20 bg-purple-50 dark:bg-purple-950/20"
            : "border-purple-200 dark:border-purple-900 hover:border-purple-400"
          : isSelected
            ? "border-amber-500 shadow-lg shadow-amber-500/20 bg-amber-50 dark:bg-amber-950/20"
            : "border-amber-200 dark:border-amber-900 hover:border-amber-400",
      )}
      onMouseEnter={onHover}
      onMouseLeave={onHoverEnd}
      onClick={onSelect}
    >
      <div className="space-y-3">
        {/* Header */}
        <div className="flex items-start justify-between gap-2">
          <div className="flex-1">
            <div className="flex items-center gap-2">
              {isIndirect && <Lightbulb className="h-4 w-4 text-purple-600 dark:text-purple-400 flex-shrink-0" />}
              <h5 className="font-bold text-foreground text-sm">{branch.title}</h5>
            </div>
            <p className="text-xs text-muted-foreground mt-1">{branch.description}</p>
          </div>
          {isIndirect && (
            <Badge className="bg-purple-500/20 text-purple-700 dark:text-purple-300 border-0 flex-shrink-0">
              ✨ New
            </Badge>
          )}
        </div>

        {/* Meta Info */}
        <div className="grid grid-cols-2 gap-2 text-xs">
          <div className="flex items-center gap-1.5">
            <TrendingUp className="h-3 w-3 text-primary" />
            <span className="text-muted-foreground">
              <span className="font-semibold text-foreground">{branch.growth}</span>
            </span>
          </div>
          <div className="flex items-center gap-1.5">
            <Briefcase className="h-3 w-3 text-primary" />
            <span className="text-muted-foreground">
              <span className="font-semibold text-foreground">{branch.salary}</span>
            </span>
          </div>
          {branch.industry && (
            <div className="flex items-center gap-1.5">
              <Users className="h-3 w-3 text-primary" />
              <span className="text-muted-foreground capitalize">
                <span className="font-semibold text-foreground">{branch.industry}</span>
              </span>
            </div>
          )}
          <div className="flex items-center gap-1.5">
            <Clock className="h-3 w-3 text-primary" />
            <span className="text-muted-foreground capitalize">{branch.level}</span>
          </div>
        </div>

        {/* Skills Progress */}
        {!isIndirect && coverage !== undefined && (
          <div className="space-y-2 pt-2 border-t border-border/50">
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">Progress</span>
              <span className="font-bold text-amber-600 dark:text-amber-400">{Math.round(coverage * 100)}%</span>
            </div>
            <div className="w-full h-1.5 bg-muted rounded-full overflow-hidden">
              <div className="h-full bg-amber-500 transition-all" style={{ width: `${coverage * 100}%` }} />
            </div>
            {missingSkills && missingSkills.length > 0 && (
              <p className="text-xs text-muted-foreground">{missingSkills.length} skills to learn</p>
            )}
          </div>
        )}

        {/* Action */}
        <Button size="sm" className="w-full text-xs" variant={isSelected ? "default" : "outline"} onClick={onSelect}>
          {isIndirect ? "Explore Branch" : "View Path"} <ArrowRight className="h-3 w-3 ml-1" />
        </Button>
      </div>
    </div>
  )
}
