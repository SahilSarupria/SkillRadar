"use client"

import { Card, CardContent } from "@/components/ui/card"
import { Label } from "@/components/ui/label"

interface ColorPickerProps {
  selectedColor: string
  onColorChange: (color: string) => void
}

const colors = [
  "#3b82f6", // Blue
  "#ef4444", // Red
  "#10b981", // Green
  "#f59e0b", // Yellow
  "#8b5cf6", // Purple
  "#06b6d4", // Cyan
  "#f97316", // Orange
  "#84cc16", // Lime
  "#ec4899", // Pink
  "#6b7280", // Gray
]

export default function ColorPicker({ selectedColor, onColorChange }: ColorPickerProps) {
  return (
    <Card>
      <CardContent className="p-4">
        <Label className="text-sm font-medium mb-3 block">Primary Color</Label>
        <div className="grid grid-cols-5 gap-2">
          {colors.map((color) => (
            <button
              key={color}
              className={`w-8 h-8 rounded-full border-2 transition-all hover:scale-110 ${
                selectedColor === color ? "border-gray-400 ring-2 ring-offset-2 ring-gray-300" : "border-gray-200"
              }`}
              style={{ backgroundColor: color }}
              onClick={() => onColorChange(color)}
              aria-label={`Select ${color} color`}
            />
          ))}
        </div>
      </CardContent>
    </Card>
  )
}
