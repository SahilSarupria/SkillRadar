"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Progress } from "@/components/ui/progress"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts"
import {
  FileText,
  BookOpen,
  Award,
  Calendar,
  Target,
  Download,
  Eye,
  Edit,
  Trash2,
  CheckCircle,
  Play,
} from "lucide-react"

// Mock user data
const mockUserData = {
  profile: {
    name: "John Doe",
    email: "john.doe@email.com",
    avatar: "/user-avatar.png",
    joinDate: "March 2024",
    plan: "Pro",
    resumeScore: 78,
    skillsAssessed: 24,
    coursesCompleted: 8,
    certificationsEarned: 3,
  },
  recentActivity: [
    {
      id: 1,
      type: "resume_analysis",
      title: "Software Engineer Resume Analysis",
      date: "2024-01-15",
      score: 78,
      status: "completed",
    },
    {
      id: 2,
      type: "skill_assessment",
      title: "React Skills Gap Analysis",
      date: "2024-01-14",
      score: 85,
      status: "completed",
    },
    {
      id: 3,
      type: "course_enrollment",
      title: "AWS Solutions Architect Course",
      date: "2024-01-12",
      progress: 45,
      status: "in_progress",
    },
    {
      id: 4,
      type: "text_conversion",
      title: "Career Summary Conversion",
      date: "2024-01-10",
      status: "completed",
    },
  ],
  resumeHistory: [
    {
      id: 1,
      name: "Software_Engineer_Resume_v3.pdf",
      uploadDate: "2024-01-15",
      score: 78,
      status: "analyzed",
      improvements: 5,
    },
    {
      id: 2,
      name: "Frontend_Developer_Resume.pdf",
      uploadDate: "2024-01-08",
      score: 72,
      status: "analyzed",
      improvements: 8,
    },
    {
      id: 3,
      name: "Full_Stack_Resume_Draft.pdf",
      uploadDate: "2024-01-02",
      score: 65,
      status: "analyzed",
      improvements: 12,
    },
  ],
  learningProgress: [
    {
      id: 1,
      course: "AWS Solutions Architect",
      provider: "Coursera",
      progress: 45,
      timeSpent: "12 hours",
      status: "in_progress",
      dueDate: "2024-02-15",
    },
    {
      id: 2,
      course: "Advanced React Patterns",
      provider: "Udemy",
      progress: 100,
      timeSpent: "18 hours",
      status: "completed",
      completedDate: "2024-01-10",
    },
    {
      id: 3,
      course: "Docker & Kubernetes",
      provider: "LinkedIn Learning",
      progress: 25,
      timeSpent: "6 hours",
      status: "in_progress",
      dueDate: "2024-03-01",
    },
  ],
  skillProgress: [
    { skill: "JavaScript", current: 85, target: 90, improvement: 5 },
    { skill: "React", current: 80, target: 85, improvement: 8 },
    { skill: "AWS", current: 45, target: 75, improvement: 15 },
    { skill: "Docker", current: 30, target: 70, improvement: 20 },
    { skill: "TypeScript", current: 60, target: 80, improvement: 12 },
  ],
  monthlyProgress: [
    { month: "Aug", score: 45, courses: 0 },
    { month: "Sep", score: 52, courses: 1 },
    { month: "Oct", score: 58, courses: 2 },
    { month: "Nov", score: 65, courses: 4 },
    { month: "Dec", score: 72, courses: 6 },
    { month: "Jan", score: 78, courses: 8 },
  ],
  achievements: [
    {
      id: 1,
      title: "First Resume Analysis",
      icon: "🎯",
      date: "2024-01-02",
      description: "Completed your first resume analysis",
    },
    { id: 2, title: "Skill Gap Identifier", icon: "📊", date: "2024-01-05", description: "Identified 5+ skill gaps" },
    { id: 3, title: "Learning Enthusiast", icon: "📚", date: "2024-01-10", description: "Completed 5 courses" },
    {
      id: 4,
      title: "Resume Optimizer",
      icon: "⚡",
      date: "2024-01-15",
      description: "Improved resume score by 20+ points",
    },
  ],
}

export function UserDashboard() {
  const [activeTab, setActiveTab] = useState("overview")

  const getActivityIcon = (type: string) => {
    switch (type) {
      case "resume_analysis":
        return <FileText className="h-4 w-4" />
      case "skill_assessment":
        return <Target className="h-4 w-4" />
      case "course_enrollment":
        return <BookOpen className="h-4 w-4" />
      case "text_conversion":
        return <Edit className="h-4 w-4" />
      default:
        return <FileText className="h-4 w-4" />
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case "completed":
        return "text-green-600"
      case "in_progress":
        return "text-blue-600"
      case "analyzed":
        return "text-primary"
      default:
        return "text-muted-foreground"
    }
  }

  const getScoreColor = (score: number) => {
    if (score >= 80) return "text-green-600"
    if (score >= 60) return "text-yellow-600"
    return "text-red-600"
  }

  return (
    <div className="space-y-6">
      {/* Profile Header */}
      <Card>
        <CardContent className="p-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <Avatar className="h-16 w-16">
                <AvatarImage src={mockUserData.profile.avatar || "/placeholder.svg"} alt={mockUserData.profile.name} />
                <AvatarFallback className="text-lg">
                  {mockUserData.profile.name
                    .split(" ")
                    .map((n) => n[0])
                    .join("")}
                </AvatarFallback>
              </Avatar>
              <div>
                <h2 className="font-space-grotesk font-bold text-2xl">{mockUserData.profile.name}</h2>
                <p className="text-muted-foreground">{mockUserData.profile.email}</p>
                <div className="flex items-center space-x-4 mt-2">
                  <Badge variant="secondary">
                    <Award className="h-3 w-3 mr-1" />
                    {mockUserData.profile.plan} Plan
                  </Badge>
                  <span className="text-sm text-muted-foreground">Member since {mockUserData.profile.joinDate}</span>
                </div>
              </div>
            </div>
            <Button variant="outline">
              <Edit className="h-4 w-4 mr-2" />
              Edit Profile
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Quick Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <Card>
          <CardContent className="p-4 text-center">
            <div className={`text-2xl font-bold mb-1 ${getScoreColor(mockUserData.profile.resumeScore)}`}>
              {mockUserData.profile.resumeScore}
            </div>
            <div className="text-sm text-muted-foreground">Resume Score</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-primary mb-1">{mockUserData.profile.skillsAssessed}</div>
            <div className="text-sm text-muted-foreground">Skills Assessed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-green-600 mb-1">{mockUserData.profile.coursesCompleted}</div>
            <div className="text-sm text-muted-foreground">Courses Completed</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-2xl font-bold text-yellow-600 mb-1">{mockUserData.profile.certificationsEarned}</div>
            <div className="text-sm text-muted-foreground">Certifications</div>
          </CardContent>
        </Card>
      </div>

      {/* Main Dashboard Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full max-w-2xl grid-cols-5">
          <TabsTrigger value="overview">Overview</TabsTrigger>
          <TabsTrigger value="resumes">Resumes</TabsTrigger>
          <TabsTrigger value="learning">Learning</TabsTrigger>
          <TabsTrigger value="skills">Skills</TabsTrigger>
          <TabsTrigger value="achievements">Awards</TabsTrigger>
        </TabsList>

        <TabsContent value="overview" className="space-y-6">
          <div className="grid lg:grid-cols-2 gap-6">
            {/* Recent Activity */}
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Recent Activity</CardTitle>
                <CardDescription>Your latest actions and progress updates</CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {mockUserData.recentActivity.map((activity) => (
                    <div key={activity.id} className="flex items-center space-x-3 p-3 border rounded-lg">
                      <div className="bg-primary/10 rounded-full p-2">{getActivityIcon(activity.type)}</div>
                      <div className="flex-1">
                        <p className="font-medium text-sm">{activity.title}</p>
                        <div className="flex items-center space-x-2 mt-1">
                          <span className="text-xs text-muted-foreground">{activity.date}</span>
                          {activity.score && (
                            <Badge variant="outline" className="text-xs">
                              Score: {activity.score}
                            </Badge>
                          )}
                          {activity.progress && (
                            <Badge variant="outline" className="text-xs">
                              {activity.progress}% complete
                            </Badge>
                          )}
                        </div>
                      </div>
                      <div className={`text-xs font-medium ${getStatusColor(activity.status)}`}>
                        {activity.status.replace("_", " ")}
                      </div>
                    </div>
                  ))}
                </div>
              </CardContent>
            </Card>

            {/* Progress Chart */}
            <Card>
              <CardHeader>
                <CardTitle className="font-space-grotesk">Progress Over Time</CardTitle>
                <CardDescription>Your resume score and learning progress</CardDescription>
              </CardHeader>
              <CardContent>
                <ResponsiveContainer width="100%" height={300}>
                  <LineChart data={mockUserData.monthlyProgress}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="month" />
                    <YAxis />
                    <Tooltip />
                    <Line type="monotone" dataKey="score" stroke="#059669" strokeWidth={2} name="Resume Score" />
                    <Line type="monotone" dataKey="courses" stroke="#10b981" strokeWidth={2} name="Courses Completed" />
                  </LineChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </div>

          {/* Quick Actions */}
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Quick Actions</CardTitle>
              <CardDescription>Jump back into your career development activities</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-4 gap-4">
                <Button className="h-20 flex-col space-y-2 bg-transparent" variant="outline" asChild>
                  <a href="/analyzer">
                    <FileText className="h-6 w-6" />
                    <span>Analyze Resume</span>
                  </a>
                </Button>
                <Button className="h-20 flex-col space-y-2 bg-transparent" variant="outline" asChild>
                  <a href="/skills">
                    <Target className="h-6 w-6" />
                    <span>Check Skills</span>
                  </a>
                </Button>
                <Button className="h-20 flex-col space-y-2 bg-transparent" variant="outline" asChild>
                  <a href="/learning">
                    <BookOpen className="h-6 w-6" />
                    <span>Find Courses</span>
                  </a>
                </Button>
                <Button className="h-20 flex-col space-y-2 bg-transparent" variant="outline" asChild>
                  <a href="/converter">
                    <Edit className="h-6 w-6" />
                    <span>Convert Text</span>
                  </a>
                </Button>
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="resumes" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Resume History</CardTitle>
              <CardDescription>All your uploaded and analyzed resumes</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {mockUserData.resumeHistory.map((resume) => (
                  <div key={resume.id} className="flex items-center justify-between p-4 border rounded-lg">
                    <div className="flex items-center space-x-4">
                      <div className="bg-primary/10 rounded-lg p-3">
                        <FileText className="h-6 w-6 text-primary" />
                      </div>
                      <div>
                        <h3 className="font-medium">{resume.name}</h3>
                        <div className="flex items-center space-x-4 mt-1 text-sm text-muted-foreground">
                          <span>Uploaded {resume.uploadDate}</span>
                          <Badge variant="outline" className={getScoreColor(resume.score)}>
                            Score: {resume.score}
                          </Badge>
                          <span>{resume.improvements} improvements suggested</span>
                        </div>
                      </div>
                    </div>
                    <div className="flex items-center space-x-2">
                      <Button size="sm" variant="outline">
                        <Eye className="h-4 w-4 mr-1" />
                        View
                      </Button>
                      <Button size="sm" variant="outline">
                        <Download className="h-4 w-4 mr-1" />
                        Download
                      </Button>
                      <Button size="sm" variant="outline">
                        <Trash2 className="h-4 w-4 mr-1" />
                        Delete
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="learning" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Learning Progress</CardTitle>
              <CardDescription>Track your enrolled courses and learning achievements</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {mockUserData.learningProgress.map((course) => (
                  <div key={course.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-3">
                      <div>
                        <h3 className="font-medium">{course.course}</h3>
                        <p className="text-sm text-muted-foreground">{course.provider}</p>
                      </div>
                      <Badge variant={course.status === "completed" ? "default" : "secondary"}>
                        {course.status === "completed" ? (
                          <CheckCircle className="h-3 w-3 mr-1" />
                        ) : (
                          <Play className="h-3 w-3 mr-1" />
                        )}
                        {course.status.replace("_", " ")}
                      </Badge>
                    </div>
                    <div className="space-y-2">
                      <div className="flex items-center justify-between text-sm">
                        <span>Progress</span>
                        <span className="font-medium">{course.progress}%</span>
                      </div>
                      <Progress value={course.progress} />
                      <div className="flex items-center justify-between text-sm text-muted-foreground">
                        <span>Time spent: {course.timeSpent}</span>
                        {course.status === "completed" ? (
                          <span>Completed {course.completedDate}</span>
                        ) : (
                          <span>Due {course.dueDate}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="skills" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Skill Development Progress</CardTitle>
              <CardDescription>Track your skill improvements and targets</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-6">
                {mockUserData.skillProgress.map((skill, index) => (
                  <div key={index} className="space-y-3">
                    <div className="flex items-center justify-between">
                      <h3 className="font-medium">{skill.skill}</h3>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm text-muted-foreground">
                          {skill.current}% → {skill.target}%
                        </span>
                        <Badge variant="outline" className="text-green-600 border-green-600">
                          +{skill.improvement}
                        </Badge>
                      </div>
                    </div>
                    <div className="space-y-1">
                      <div className="flex justify-between text-xs text-muted-foreground">
                        <span>Current Level</span>
                        <span>Target Level</span>
                      </div>
                      <div className="relative">
                        <Progress value={skill.target} className="opacity-30" />
                        <Progress value={skill.current} className="absolute top-0" />
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="achievements" className="space-y-6">
          <Card>
            <CardHeader>
              <CardTitle className="font-space-grotesk">Achievements & Milestones</CardTitle>
              <CardDescription>Celebrate your career development accomplishments</CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid md:grid-cols-2 gap-4">
                {mockUserData.achievements.map((achievement) => (
                  <div key={achievement.id} className="flex items-center space-x-4 p-4 border rounded-lg">
                    <div className="text-3xl">{achievement.icon}</div>
                    <div className="flex-1">
                      <h3 className="font-medium">{achievement.title}</h3>
                      <p className="text-sm text-muted-foreground mb-1">{achievement.description}</p>
                      <div className="flex items-center space-x-2 text-xs text-muted-foreground">
                        <Calendar className="h-3 w-3" />
                        <span>Earned {achievement.date}</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  )
}
