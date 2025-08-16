import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { CheckCircle, TrendingUp, Users, Zap } from "lucide-react"

export function FeaturesSection() {
  return (
    <section className="py-20 bg-muted/30">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h2 className="font-space-grotesk font-bold text-3xl lg:text-4xl text-foreground mb-4">
            Everything You Need to Succeed
          </h2>
          <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
            Our comprehensive platform provides all the tools and insights you need to optimize your resume and advance
            your career.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-8 mb-16">
          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center space-x-2 mb-2">
                <CheckCircle className="h-6 w-6 text-primary" />
                <CardTitle className="font-space-grotesk">Comprehensive Resume Analysis</CardTitle>
              </div>
              <CardDescription>
                Get detailed feedback on every aspect of your resume with our advanced AI analysis engine.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Content Quality</Badge>
                  <span className="text-sm text-muted-foreground">Analyze impact and relevance</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">ATS Optimization</Badge>
                  <span className="text-sm text-muted-foreground">Ensure compatibility with hiring systems</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Format & Design</Badge>
                  <span className="text-sm text-muted-foreground">Professional presentation standards</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center space-x-2 mb-2">
                <TrendingUp className="h-6 w-6 text-primary" />
                <CardTitle className="font-space-grotesk">Skill Gap Analysis</CardTitle>
              </div>
              <CardDescription>
                Identify the skills you need to develop for your target roles and career advancement.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Market Trends</Badge>
                  <span className="text-sm text-muted-foreground">Stay ahead of industry demands</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Role Matching</Badge>
                  <span className="text-sm text-muted-foreground">Compare against job requirements</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Priority Ranking</Badge>
                  <span className="text-sm text-muted-foreground">Focus on high-impact skills first</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center space-x-2 mb-2">
                <Users className="h-6 w-6 text-primary" />
                <CardTitle className="font-space-grotesk">Learning Recommendations</CardTitle>
              </div>
              <CardDescription>
                Get personalized course and resource recommendations from top learning platforms.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Coursera</Badge>
                  <Badge variant="secondary">Udemy</Badge>
                  <Badge variant="secondary">LinkedIn Learning</Badge>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">edX</Badge>
                  <Badge variant="secondary">Pluralsight</Badge>
                  <Badge variant="secondary">Skillshare</Badge>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card className="border-border">
            <CardHeader>
              <div className="flex items-center space-x-2 mb-2">
                <Zap className="h-6 w-6 text-primary" />
                <CardTitle className="font-space-grotesk">Smart Text Converter</CardTitle>
              </div>
              <CardDescription>
                Transform unstructured text into professional resume format with AI-powered formatting.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Auto-Format</Badge>
                  <span className="text-sm text-muted-foreground">Professional layout generation</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Content Enhancement</Badge>
                  <span className="text-sm text-muted-foreground">Improve clarity and impact</span>
                </div>
                <div className="flex items-center space-x-2">
                  <Badge variant="secondary">Multiple Templates</Badge>
                  <span className="text-sm text-muted-foreground">Choose from various styles</span>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </section>
  )
}
