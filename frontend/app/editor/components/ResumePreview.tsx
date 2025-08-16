"use client"

import { Badge } from "@/components/ui/badge"
import type { ResumeData, ResumeTheme } from "../page"
import { Mail, Phone, MapPin, Globe, Linkedin } from "lucide-react"

interface ResumePreviewProps {
  data: ResumeData
  theme: ResumeTheme
}

export default function ResumePreview({ data, theme }: ResumePreviewProps) {
  const { personalInfo, summary, skills, experience, education, projects } = data

  const getTemplateStyles = () => {
    switch (theme.template) {
      case "modern":
        return "bg-white"
      case "creative":
        return "bg-gradient-to-br from-gray-50 to-white"
      case "professional":
        return "bg-white border-l-4"
      default:
        return "bg-white"
    }
  }

  return (
    <div
      className={`min-h-[800px] p-8 ${getTemplateStyles()}`}
      style={{
        fontFamily: theme.fontFamily,
        borderLeftColor: theme.template === "professional" ? theme.primaryColor : undefined,
      }}
    >
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold mb-2" style={{ color: theme.primaryColor }}>
          {personalInfo.name || "Your Name"}
        </h1>

        <div className="flex flex-wrap gap-4 text-sm text-gray-600">
          {personalInfo.email && (
            <div className="flex items-center gap-1">
              <Mail className="h-4 w-4" />
              {personalInfo.email}
            </div>
          )}
          {personalInfo.phone && (
            <div className="flex items-center gap-1">
              <Phone className="h-4 w-4" />
              {personalInfo.phone}
            </div>
          )}
          {personalInfo.location && (
            <div className="flex items-center gap-1">
              <MapPin className="h-4 w-4" />
              {personalInfo.location}
            </div>
          )}
          {personalInfo.website && (
            <div className="flex items-center gap-1">
              <Globe className="h-4 w-4" />
              {personalInfo.website}
            </div>
          )}
          {personalInfo.linkedin && (
            <div className="flex items-center gap-1">
              <Linkedin className="h-4 w-4" />
              {personalInfo.linkedin}
            </div>
          )}
        </div>
      </div>

      {/* Professional Summary */}
      {summary && (
        <div className="mb-6">
          <h2
            className="text-lg font-semibold mb-3 pb-1 border-b"
            style={{ color: theme.primaryColor, borderColor: theme.primaryColor }}
          >
            Professional Summary
          </h2>
          <p className="text-gray-700 leading-relaxed">{summary}</p>
        </div>
      )}

      {/* Skills */}
      {skills.length > 0 && (
        <div className="mb-6">
          <h2
            className="text-lg font-semibold mb-3 pb-1 border-b"
            style={{ color: theme.primaryColor, borderColor: theme.primaryColor }}
          >
            Skills
          </h2>
          <div className="flex flex-wrap gap-2">
            {skills.map((skill, index) => (
              <Badge
                key={index}
                variant="secondary"
                style={{ backgroundColor: `${theme.primaryColor}20`, color: theme.primaryColor }}
              >
                {skill}
              </Badge>
            ))}
          </div>
        </div>
      )}

      {/* Work Experience */}
      {experience.length > 0 && (
        <div className="mb-6">
          <h2
            className="text-lg font-semibold mb-3 pb-1 border-b"
            style={{ color: theme.primaryColor, borderColor: theme.primaryColor }}
          >
            Work Experience
          </h2>
          <div className="space-y-4">
            {experience.map((exp) => (
              <div key={exp.id}>
                <div className="flex justify-between items-start mb-1">
                  <div>
                    <h3 className="font-semibold">{exp.position || "Position"}</h3>
                    <p className="text-gray-600">{exp.company || "Company"}</p>
                  </div>
                  <p className="text-sm text-gray-500">
                    {exp.startDate} - {exp.endDate || "Present"}
                  </p>
                </div>
                {exp.description && <p className="text-gray-700 text-sm leading-relaxed mt-2">{exp.description}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Education */}
      {education.length > 0 && (
        <div className="mb-6">
          <h2
            className="text-lg font-semibold mb-3 pb-1 border-b"
            style={{ color: theme.primaryColor, borderColor: theme.primaryColor }}
          >
            Education
          </h2>
          <div className="space-y-3">
            {education.map((edu) => (
              <div key={edu.id}>
                <div className="flex justify-between items-start">
                  <div>
                    <h3 className="font-semibold">
                      {edu.degree || "Degree"} in {edu.field || "Field"}
                    </h3>
                    <p className="text-gray-600">{edu.school || "School"}</p>
                  </div>
                  <p className="text-sm text-gray-500">{edu.graduationDate}</p>
                </div>
                {edu.gpa && <p className="text-sm text-gray-600">GPA: {edu.gpa}</p>}
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Projects */}
      {projects.length > 0 && (
        <div className="mb-6">
          <h2
            className="text-lg font-semibold mb-3 pb-1 border-b"
            style={{ color: theme.primaryColor, borderColor: theme.primaryColor }}
          >
            Projects
          </h2>
          <div className="space-y-4">
            {projects.map((project) => (
              <div key={project.id}>
                <div className="flex justify-between items-start mb-1">
                  <h3 className="font-semibold">{project.name || "Project Name"}</h3>
                  {project.link && (
                    <a href={project.link} className="text-sm underline" style={{ color: theme.primaryColor }}>
                      View Project
                    </a>
                  )}
                </div>
                {project.description && (
                  <p className="text-gray-700 text-sm leading-relaxed mb-2">{project.description}</p>
                )}
                {project.technologies.length > 0 && (
                  <div className="flex flex-wrap gap-1">
                    {project.technologies.map((tech, index) => (
                      <Badge
                        key={index}
                        variant="outline"
                        className="text-xs"
                        style={{ borderColor: theme.primaryColor, color: theme.primaryColor }}
                      >
                        {tech}
                      </Badge>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
