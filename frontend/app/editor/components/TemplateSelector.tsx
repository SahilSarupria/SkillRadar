"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

interface TemplateSelectorProps {
  selectedTemplate: string
  onTemplateChange: (template: string) => void
}

const templates = [
  { id: "modern", name: "Modern", preview: "Clean and contemporary design" },
  { id: "creative", name: "Creative", preview: "Artistic with gradient background" },
  { id: "professional", name: "Professional", preview: "Traditional business style" },
  { id: "minimal", name: "Minimal", preview: "Simple and elegant" },
]

export default function TemplateSelector({ selectedTemplate, onTemplateChange }: TemplateSelectorProps) {
  return (
    <Card>
      <CardContent className="p-4">
        <Label className="text-sm font-medium mb-3 block">Template</Label>
        <div className="grid grid-cols-2 gap-2">
          {templates.map((template) => (
            <div
              key={template.id}
              className={`p-3 border rounded-lg cursor-pointer transition-all hover:border-blue-300 ${
                selectedTemplate === template.id ? "border-blue-500 bg-blue-50" : "border-gray-200"
              }`}
              onClick={() => onTemplateChange(template.id)}
            >
              <div className="text-xs font-medium mb-1">{template.name}</div>
              <div className="text-xs text-gray-500">{template.preview}</div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
