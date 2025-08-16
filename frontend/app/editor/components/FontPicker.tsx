"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface FontPickerProps {
  selectedFont: string
  onFontChange: (font: string) => void
}

const fonts = [
  { value: "Inter", label: "Inter", style: "font-sans" },
  { value: "Georgia", label: "Georgia", style: "font-serif" },
  { value: "JetBrains Mono", label: "JetBrains Mono", style: "font-mono" },
  { value: "Playfair Display", label: "Playfair Display", style: "font-serif" },
  { value: "Roboto", label: "Roboto", style: "font-sans" },
]

export default function FontPicker({ selectedFont, onFontChange }: FontPickerProps) {
  return (
    <Card>
      <CardContent className="p-4">
        <Label className="text-sm font-medium mb-3 block">Font Family</Label>
        <Select value={selectedFont} onValueChange={onFontChange}>
          <SelectTrigger>
            <SelectValue placeholder="Select font" />
          </SelectTrigger>
          <SelectContent>
            {fonts.map((font) => (
              <SelectItem key={font.value} value={font.value}>
                <span style={{ fontFamily: font.value }}>{font.label}</span>
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </CardContent>
    </Card>
  )
}
