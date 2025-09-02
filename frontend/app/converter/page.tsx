import { Navigation } from "@/components/navigation"
import { Footer } from "@/components/footer"
import { TextConverterWrapper } from "@/components/text-converter-wrapper"

export default function ConverterPage() {
  return (
    <div className="min-h-screen flex flex-col">
      <Navigation />
      <main className="py-12 flex-1 w-full">
        <TextConverterWrapper />
      </main>
      <Footer />
    </div>
  )
}
