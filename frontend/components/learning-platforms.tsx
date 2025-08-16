"use client"

import { useState } from "react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import {
  ExternalLink,
  Search,
  Star,
  Clock,
  Users,
  BookOpen,
  Filter,
  TrendingUp,
  Award,
  Play,
  CheckCircle,
} from "lucide-react"

// Mock course data from different platforms
const mockCourses = [
  {
    id: 1,
    title: "AWS Certified Solutions Architect",
    provider: "Coursera",
    instructor: "Amazon Web Services",
    rating: 4.6,
    students: 125000,
    duration: "40 hours",
    level: "Intermediate",
    price: "$49/month",
    skills: ["AWS", "Cloud Computing", "Architecture"],
    description: "Master AWS cloud architecture and prepare for the Solutions Architect certification exam.",
    url: "https://coursera.org/aws-architect",
    image: "/aws-cloud-architecture.png",
    priority: "High",
    matchScore: 95,
  },
  {
    id: 2,
    title: "Complete React Developer Course",
    provider: "Udemy",
    instructor: "Maximilian Schwarzmüller",
    rating: 4.7,
    students: 89000,
    duration: "32 hours",
    level: "Beginner",
    price: "$84.99",
    skills: ["React", "JavaScript", "Frontend"],
    description: "Build modern React applications from scratch with hooks, context, and advanced patterns.",
    url: "https://udemy.com/react-complete",
    image: "/react-development-course.png",
    priority: "Medium",
    matchScore: 88,
  },
  {
    id: 3,
    title: "Machine Learning Specialization",
    provider: "Coursera",
    instructor: "Andrew Ng",
    rating: 4.9,
    students: 2100000,
    duration: "60 hours",
    level: "Intermediate",
    price: "$49/month",
    skills: ["Machine Learning", "Python", "TensorFlow"],
    description: "Learn the fundamentals of machine learning and build ML models with Python and TensorFlow.",
    url: "https://coursera.org/ml-specialization",
    image: "/machine-learning-course.png",
    priority: "High",
    matchScore: 92,
  },
  {
    id: 4,
    title: "Docker and Kubernetes Complete Guide",
    provider: "Udemy",
    instructor: "Stephen Grider",
    rating: 4.5,
    students: 156000,
    duration: "22 hours",
    level: "Intermediate",
    price: "$94.99",
    skills: ["Docker", "Kubernetes", "DevOps"],
    description: "Master containerization and orchestration with Docker and Kubernetes for production deployments.",
    url: "https://udemy.com/docker-kubernetes",
    image: "/docker-kubernetes-course.png",
    priority: "High",
    matchScore: 90,
  },
  {
    id: 5,
    title: "Data Analysis with Python",
    provider: "LinkedIn Learning",
    instructor: "Michele Vallisneri",
    rating: 4.4,
    students: 45000,
    duration: "8 hours",
    level: "Beginner",
    price: "$29.99/month",
    skills: ["Python", "Data Analysis", "Pandas"],
    description: "Learn data analysis techniques using Python, pandas, and visualization libraries.",
    url: "https://linkedin.com/learning/python-data-analysis",
    image: "/python-data-analysis-course.png",
    priority: "Medium",
    matchScore: 85,
  },
  {
    id: 6,
    title: "Project Management Professional (PMP)",
    provider: "edX",
    instructor: "University of Adelaide",
    rating: 4.3,
    students: 78000,
    duration: "50 hours",
    level: "Advanced",
    price: "$299",
    skills: ["Project Management", "Leadership", "Agile"],
    description: "Comprehensive PMP certification preparation covering all project management knowledge areas.",
    url: "https://edx.org/pmp-certification",
    image: "/project-management-course.png",
    priority: "Medium",
    matchScore: 82,
  },
]

const platforms = [
  { name: "All Platforms", value: "all", logo: "🎓" },
  { name: "Coursera", value: "Coursera", logo: "📚" },
  { name: "Udemy", value: "Udemy", logo: "🎯" },
  { name: "LinkedIn Learning", value: "LinkedIn Learning", logo: "💼" },
  { name: "edX", value: "edX", logo: "🏛️" },
  { name: "Pluralsight", value: "Pluralsight", logo: "⚡" },
]

const skillCategories = [
  "All Skills",
  "Cloud Computing",
  "Programming",
  "Data Science",
  "DevOps",
  "Project Management",
  "Design",
  "Marketing",
]

export function LearningPlatforms() {
  const [searchQuery, setSearchQuery] = useState("")
  const [selectedPlatform, setSelectedPlatform] = useState("all")
  const [selectedLevel, setSelectedLevel] = useState("all")
  const [selectedSkill, setSelectedSkill] = useState("All Skills")
  const [activeTab, setActiveTab] = useState("recommended")

  const filteredCourses = mockCourses.filter((course) => {
    const matchesSearch =
      course.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      course.skills.some((skill) => skill.toLowerCase().includes(searchQuery.toLowerCase()))
    const matchesPlatform = selectedPlatform === "all" || course.provider === selectedPlatform
    const matchesLevel = selectedLevel === "all" || course.level.toLowerCase() === selectedLevel
    const matchesSkill = selectedSkill === "All Skills" || course.skills.includes(selectedSkill)

    return matchesSearch && matchesPlatform && matchesLevel && matchesSkill
  })

  const recommendedCourses = filteredCourses.filter((course) => course.priority === "High").slice(0, 3)
  const trendingCourses = filteredCourses.sort((a, b) => b.students - a.students).slice(0, 4)

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case "High":
        return "bg-red-100 text-red-800 dark:bg-red-900/20 dark:text-red-300"
      case "Medium":
        return "bg-yellow-100 text-yellow-800 dark:bg-yellow-900/20 dark:text-yellow-300"
      default:
        return "bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-300"
    }
  }

  return (
    <div className="space-y-8">
      {/* Search and Filters */}
      <Card>
        <CardHeader>
          <CardTitle className="font-space-grotesk flex items-center space-x-2">
            <Search className="h-5 w-5 text-primary" />
            <span>Find Your Perfect Course</span>
          </CardTitle>
          <CardDescription>
            Search and filter courses from top learning platforms based on your skill gaps and career goals.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex flex-col md:flex-row gap-4">
            <div className="flex-1">
              <Input
                placeholder="Search courses, skills, or topics..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full"
              />
            </div>
            <div className="flex gap-2">
              <Select value={selectedPlatform} onValueChange={setSelectedPlatform}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Platform" />
                </SelectTrigger>
                <SelectContent>
                  {platforms.map((platform) => (
                    <SelectItem key={platform.value} value={platform.value}>
                      {platform.logo} {platform.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={selectedLevel} onValueChange={setSelectedLevel}>
                <SelectTrigger className="w-32">
                  <SelectValue placeholder="Level" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Levels</SelectItem>
                  <SelectItem value="beginner">Beginner</SelectItem>
                  <SelectItem value="intermediate">Intermediate</SelectItem>
                  <SelectItem value="advanced">Advanced</SelectItem>
                </SelectContent>
              </Select>
              <Select value={selectedSkill} onValueChange={setSelectedSkill}>
                <SelectTrigger className="w-40">
                  <SelectValue placeholder="Skill" />
                </SelectTrigger>
                <SelectContent>
                  {skillCategories.map((skill) => (
                    <SelectItem key={skill} value={skill}>
                      {skill}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          </div>
          <div className="flex items-center justify-between">
            <p className="text-sm text-muted-foreground">
              Found {filteredCourses.length} courses matching your criteria
            </p>
            <Button variant="outline" size="sm">
              <Filter className="h-4 w-4 mr-2" />
              More Filters
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* Course Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-6">
        <TabsList className="grid w-full max-w-md grid-cols-3">
          <TabsTrigger value="recommended">Recommended</TabsTrigger>
          <TabsTrigger value="trending">Trending</TabsTrigger>
          <TabsTrigger value="all">All Courses</TabsTrigger>
        </TabsList>

        <TabsContent value="recommended" className="space-y-6">
          <div className="mb-6">
            <h2 className="font-space-grotesk font-semibold text-xl mb-2">Recommended for You</h2>
            <p className="text-muted-foreground">
              Courses specifically selected based on your skill gap analysis and career goals.
            </p>
          </div>
          <div className="grid lg:grid-cols-3 gap-6">
            {recommendedCourses.map((course) => (
              <Card key={course.id} className="overflow-hidden">
                <div className="relative">
                  <img
                    src={course.image || "/placeholder.svg"}
                    alt={course.title}
                    className="w-full h-48 object-cover"
                  />
                  <Badge className={`absolute top-3 right-3 ${getPriorityColor(course.priority)}`}>
                    {course.priority} Priority
                  </Badge>
                </div>
                <CardHeader className="pb-3">
                  <div className="flex items-center justify-between mb-2">
                    <Badge variant="outline">{course.provider}</Badge>
                    <div className="flex items-center space-x-1">
                      <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                      <span className="text-sm font-medium">{course.rating}</span>
                    </div>
                  </div>
                  <CardTitle className="font-space-grotesk text-lg leading-tight">{course.title}</CardTitle>
                  <CardDescription className="text-sm">{course.instructor}</CardDescription>
                </CardHeader>
                <CardContent className="space-y-4">
                  <p className="text-sm text-muted-foreground line-clamp-2">{course.description}</p>
                  <div className="flex flex-wrap gap-1">
                    {course.skills.slice(0, 3).map((skill) => (
                      <Badge key={skill} variant="secondary" className="text-xs">
                        {skill}
                      </Badge>
                    ))}
                  </div>
                  <div className="flex items-center justify-between text-sm text-muted-foreground">
                    <div className="flex items-center space-x-1">
                      <Clock className="h-4 w-4" />
                      <span>{course.duration}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="h-4 w-4" />
                      <span>{course.students.toLocaleString()}</span>
                    </div>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="font-semibold text-primary">{course.price}</span>
                    <div className="flex items-center space-x-1 text-green-600">
                      <CheckCircle className="h-4 w-4" />
                      <span className="text-sm font-medium">{course.matchScore}% match</span>
                    </div>
                  </div>
                  <Button className="w-full" asChild>
                    <a href={course.url} target="_blank" rel="noopener noreferrer">
                      <ExternalLink className="h-4 w-4 mr-2" />
                      Enroll Now
                    </a>
                  </Button>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="trending" className="space-y-6">
          <div className="mb-6">
            <h2 className="font-space-grotesk font-semibold text-xl mb-2 flex items-center space-x-2">
              <TrendingUp className="h-5 w-5 text-primary" />
              <span>Trending Courses</span>
            </h2>
            <p className="text-muted-foreground">Most popular courses with high enrollment and excellent ratings.</p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {trendingCourses.map((course) => (
              <Card key={course.id} className="overflow-hidden">
                <div className="relative">
                  <img
                    src={course.image || "/placeholder.svg"}
                    alt={course.title}
                    className="w-full h-32 object-cover"
                  />
                  <div className="absolute top-2 left-2">
                    <Badge variant="secondary" className="bg-black/70 text-white">
                      <TrendingUp className="h-3 w-3 mr-1" />
                      Trending
                    </Badge>
                  </div>
                </div>
                <CardContent className="p-4 space-y-3">
                  <div className="flex items-center justify-between">
                    <Badge variant="outline" className="text-xs">
                      {course.provider}
                    </Badge>
                    <div className="flex items-center space-x-1">
                      <Star className="h-3 w-3 fill-yellow-400 text-yellow-400" />
                      <span className="text-xs">{course.rating}</span>
                    </div>
                  </div>
                  <h3 className="font-space-grotesk font-medium text-sm leading-tight line-clamp-2">{course.title}</h3>
                  <div className="flex items-center justify-between text-xs text-muted-foreground">
                    <span>{course.duration}</span>
                    <span>{course.students.toLocaleString()} students</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm font-semibold text-primary">{course.price}</span>
                    <Button size="sm" variant="outline" asChild>
                      <a href={course.url} target="_blank" rel="noopener noreferrer">
                        <Play className="h-3 w-3 mr-1" />
                        View
                      </a>
                    </Button>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
        </TabsContent>

        <TabsContent value="all" className="space-y-6">
          <div className="mb-6">
            <h2 className="font-space-grotesk font-semibold text-xl mb-2">All Courses</h2>
            <p className="text-muted-foreground">Browse all available courses from our partner learning platforms.</p>
          </div>
          <div className="grid md:grid-cols-2 gap-6">
            {filteredCourses.map((course) => (
              <Card key={course.id} className="overflow-hidden">
                <div className="flex">
                  <img
                    src={course.image || "/placeholder.svg"}
                    alt={course.title}
                    className="w-32 h-32 object-cover flex-shrink-0"
                  />
                  <div className="flex-1 p-4">
                    <div className="flex items-center justify-between mb-2">
                      <Badge variant="outline" className="text-xs">
                        {course.provider}
                      </Badge>
                      <div className="flex items-center space-x-1">
                        <Star className="h-4 w-4 fill-yellow-400 text-yellow-400" />
                        <span className="text-sm">{course.rating}</span>
                      </div>
                    </div>
                    <h3 className="font-space-grotesk font-medium mb-1 line-clamp-2">{course.title}</h3>
                    <p className="text-sm text-muted-foreground mb-2">{course.instructor}</p>
                    <div className="flex flex-wrap gap-1 mb-3">
                      {course.skills.slice(0, 2).map((skill) => (
                        <Badge key={skill} variant="secondary" className="text-xs">
                          {skill}
                        </Badge>
                      ))}
                    </div>
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3 text-xs text-muted-foreground">
                        <span>{course.duration}</span>
                        <span>{course.level}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <span className="text-sm font-semibold text-primary">{course.price}</span>
                        <Button size="sm" asChild>
                          <a href={course.url} target="_blank" rel="noopener noreferrer">
                            <ExternalLink className="h-3 w-3 mr-1" />
                            Enroll
                          </a>
                        </Button>
                      </div>
                    </div>
                  </div>
                </div>
              </Card>
            ))}
          </div>
        </TabsContent>
      </Tabs>

      {/* Platform Partners */}
      <Card className="bg-muted/30">
        <CardHeader>
          <CardTitle className="font-space-grotesk text-center">Our Learning Partners</CardTitle>
          <CardDescription className="text-center">
            We partner with the world's leading learning platforms to bring you the best courses.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-8 items-center">
            {platforms.slice(1).map((platform) => (
              <div key={platform.value} className="text-center">
                <div className="text-4xl mb-2">{platform.logo}</div>
                <p className="text-sm font-medium">{platform.name}</p>
              </div>
            ))}
            <div className="text-center">
              <div className="text-4xl mb-2">🎨</div>
              <p className="text-sm font-medium">Skillshare</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Learning Path Suggestion */}
      <Card className="bg-primary/5 border-primary/20">
        <CardHeader>
          <CardTitle className="font-space-grotesk flex items-center space-x-2">
            <Award className="h-5 w-5 text-primary" />
            <span>Create Your Learning Path</span>
          </CardTitle>
          <CardDescription>
            Get a personalized learning roadmap based on your career goals and current skill level.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col md:flex-row items-center justify-between space-y-4 md:space-y-0">
            <div className="flex-1">
              <p className="text-sm text-muted-foreground mb-4">
                Our AI will create a structured learning path with courses from multiple platforms, progress tracking,
                and milestone achievements to help you reach your career goals faster.
              </p>
              <div className="flex items-center space-x-4 text-sm">
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Personalized curriculum</span>
                </div>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Progress tracking</span>
                </div>
                <div className="flex items-center space-x-1">
                  <CheckCircle className="h-4 w-4 text-green-600" />
                  <span>Certificate goals</span>
                </div>
              </div>
            </div>
            <Button size="lg" className="ml-4">
              <BookOpen className="h-4 w-4 mr-2" />
              Create Learning Path
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}
