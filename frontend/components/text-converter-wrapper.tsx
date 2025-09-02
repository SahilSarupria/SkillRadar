"use client"

import { useState } from "react"
import { TextConverter } from "./text-converter"
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Sparkles, LayoutTemplate, ChevronLeft, ChevronRight } from "lucide-react"

export function TextConverterWrapper() {
  const [mode, setMode] = useState<"initial" | "editor">("initial")
  const [aiSidebarOpen, setAiSidebarOpen] = useState(false)
  const [aiPrompt, setAiPrompt] = useState("")
  const [isGenerating, setIsGenerating] = useState(false)
  const [resumeContent, setResumeContent] = useState<string>("")

  // Simulate AI generation (replace with your actual API call)
  const handleAIGenerate = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsGenerating(true)
    setTimeout(() => {
      setResumeContent(`Generated resume for: ${aiPrompt}`)
      setIsGenerating(false)
      setAiSidebarOpen(false)
      setMode("editor")
    }, 1200)
  }

  // Initial state: show two cards
  if (mode === "initial") {
    return (
      <div className="flex justify-center items-center min-h-[60vh] gap-8 w-full">
        {/* AI Prompt Card */}
        <div className="flex-1 max-w-xs">
          <Card className="shadow-2xl rounded-2xl bg-gradient-to-br from-white to-blue-50 hover:scale-105 transition-transform duration-300">
            <CardHeader className="flex flex-row items-center gap-3">
              <Sparkles className="h-7 w-7 text-primary" />
              <div>
                <CardTitle className="text-xl">Start with AI Prompt</CardTitle>
                <CardDescription>
                  Let AI generate your resume from a single prompt.
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <form className="space-y-4" onSubmit={handleAIGenerate}>
                <textarea
                  className="w-full min-h-[80px] border rounded-lg p-3"
                  placeholder="Describe your career, skills, and goals..."
                  value={aiPrompt}
                  onChange={e => setAiPrompt(e.target.value)}
                  disabled={isGenerating}
                />
                <Button className="w-full mt-2" type="submit" disabled={isGenerating || !aiPrompt}>
                  {isGenerating ? "Generating..." : "Generate & Edit"}
                </Button>
              </form>
            </CardContent>
          </Card>
        </div>
        {/* Visual Editor Card */}
        <div className="flex-1 max-w-xs">
          <Card className="shadow-2xl rounded-2xl bg-gradient-to-br from-white to-indigo-50 hover:scale-105 transition-transform duration-300 cursor-pointer"
            onClick={() => setMode("editor")}>
            <CardHeader className="flex flex-row items-center gap-3">
              <LayoutTemplate className="h-7 w-7 text-indigo-600" />
              <div>
                <CardTitle className="text-xl">Start with Visual Editor</CardTitle>
                <CardDescription>
                  Build your resume visually from scratch.
                </CardDescription>
              </div>
            </CardHeader>
            <CardContent>
              <Button className="w-full mt-4" variant="outline">
                Open Editor
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    )
  }

  // Editor state: show sidebar and editor
  return (
    <div className="flex min-h-[80vh] items-stretch justify-center py-10 gap-4 w-full">
      {/* AI Prompt Sidebar/Card */}
      <div
        className={`
          transition-all duration-500
          ${aiSidebarOpen ? "w-[380px] md:w-[420px]" : "w-[80px]"}
          flex-shrink-0
          relative
        `}
        style={{
          minWidth: aiSidebarOpen ? 120 : 60,
        }}
      >
        <Card
          className={`
            h-full shadow-2xl rounded-2xl transition-all duration-500
            bg-gradient-to-br from-white to-blue-50
            flex flex-col
            overflow-hidden
            ${aiSidebarOpen ? "p-0" : "items-center justify-center rounded-3xl shadow-xl"}
          `}
          style={{
            borderRadius: aiSidebarOpen ? "1rem" : "2rem",
            boxShadow: aiSidebarOpen
              ? "0 10px 40px 0 rgba(56, 189, 248, 0.10)"
              : "0 4px 24px 0 rgba(56, 189, 248, 0.15)",
            transition: "border-radius 0.5s, box-shadow 0.5s",
          }}
        >
          <div
            className={`transition-opacity duration-300 ${aiSidebarOpen ? "opacity-100" : "opacity-0 pointer-events-none"}`}
          >
            {aiSidebarOpen && (
              <>
                <CardHeader className="flex flex-row items-center gap-3">
                  <Sparkles className="h-7 w-7 text-primary" />
                  <div>
                    <CardTitle className="text-xl">AI Prompt</CardTitle>
                    <CardDescription>
                      Generate a resume with a single prompt.
                    </CardDescription>
                  </div>
                  <Button
                    size="icon"
                    variant="ghost"
                    className="ml-auto"
                    onClick={() => setAiSidebarOpen(false)}
                    title="Collapse"
                  >
                    <ChevronLeft />
                  </Button>
                </CardHeader>
                <CardContent>
                  <form className="space-y-4" onSubmit={handleAIGenerate}>
                    <textarea
                      className="w-full min-h-[100px] border rounded-lg p-3"
                      placeholder="Describe your career, skills, and goals..."
                      value={aiPrompt}
                      onChange={e => setAiPrompt(e.target.value)}
                      disabled={isGenerating}
                    />
                    <Button className="w-full" type="submit" disabled={isGenerating || !aiPrompt}>
                      {isGenerating ? "Generating..." : "Generate Resume"}
                    </Button>
                  </form>
                </CardContent>
              </>
            )}
          </div>
          {!aiSidebarOpen && (
            <Button
              variant="ghost"
              className="h-full w-full flex flex-col items-center justify-center transition-all duration-300"
              onClick={() => {
                setMode("initial")
                setAiSidebarOpen(false)
              }}
              title="Open AI Prompt"
            >
              <Sparkles className="h-7 w-7 text-primary mb-2 transition-all duration-300" />
              <ChevronRight />
            </Button>
          )}
        </Card>
      </div>

      {/* Editor (always open in this mode) */}
      <div className="flex-1 min-w-0">
        <TextConverter
          initialContent={resumeContent}
          onContentChange={setResumeContent}
        />
      </div>
    </div>
  )
}