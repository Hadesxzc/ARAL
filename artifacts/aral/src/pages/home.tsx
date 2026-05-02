import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const STATS = [
  { value: "1 in 3", label: "Filipino workers exposed to automation", source: "IMF, 2025" },
  { value: "800K+", label: "Graduates enter the workforce annually", source: "PSA, 2024" },
  { value: "11 years", label: "Average CHED curriculum update cycle", source: "EDCOM II, 2026" },
  { value: "0", label: "Existing localized career risk tools for PH graduates", source: "Research gap" },
];

const TEAM = [
  { role: "Lead Researcher", name: "Gasmen, Kenneth R." },
  { role: "Developer", name: "Ignacio, John Jomer R." },
  { role: "Data Analysis", name: "Maddara, Darren Bjorn P." },
  { role: "Developer", name: "Tarayao, Mark Daniel B." },
];

const STEPS = [
  { number: "01", title: "Select Your Degree", description: "Choose from 6 covered degree programs aligned with CHED CMO standards." },
  { number: "02", title: "Enter Job Title", description: "Tell us your current or target job role — we map it to PSOC 2022." },
  { number: "03", title: "Skills Assessment", description: "Rate your competencies against your program's CHED CMO curriculum." },
  { number: "04", title: "Task Distribution", description: "Describe how you spend your workday across 13 task categories." },
];

const FEATURES = [
  {
    title: "Random Forest Prediction",
    description: "Trained on 1,000 Filipino graduate respondents from the Philippine Occupation-Automation Reference Dataset (POARD).",
  },
  {
    title: "SHAP Explainability",
    description: "SHapley Additive exPlanations reveal exactly which skills and tasks drive your automation vulnerability score.",
  },
  {
    title: "CHED CMO Curriculum Gap Analysis",
    description: "Cross-references your skill profile against official Commission on Higher Education memorandum orders.",
  },
  {
    title: "AI Course Recommendations",
    description: "Powered by Gemini 2.5 Flash — personalized free courses from Coursera, edX, TESDA Online, and more.",
  },
];

export default function Home() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">A</span>
            </div>
            <div>
              <span className="font-bold text-primary">ARAL</span>
              <span className="text-muted-foreground text-sm ml-2 hidden sm:inline">Automation Risk Assessment</span>
            </div>
          </div>
          <nav className="flex items-center gap-6">
            <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground transition-colors">About</Link>
            <Link href="/admin" className="text-sm text-muted-foreground hover:text-foreground transition-colors">Research</Link>
            <Link href="/assessment">
              <Button size="sm">Start Assessment</Button>
            </Link>
          </nav>
        </div>
      </header>

      {/* Hero */}
      <section className="bg-primary text-primary-foreground py-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <Badge className="bg-secondary text-secondary-foreground mb-6 text-xs font-semibold tracking-wider uppercase">
            University of Saint Louis Tuguegarao
          </Badge>
          <h1 className="text-4xl sm:text-5xl font-bold leading-tight mb-6">
            Is Your Career Ready<br />for Automation?
          </h1>
          <p className="text-lg text-primary-foreground/80 max-w-2xl mx-auto mb-10 leading-relaxed">
            ARAL predicts your automation vulnerability using a localized machine learning model trained on Filipino graduate data — 
            then explains why, identifies your skill gaps, and recommends free courses to future-proof your career.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/assessment">
              <Button size="lg" className="bg-secondary text-secondary-foreground hover:bg-secondary/90 font-semibold px-8">
                Take the Assessment
              </Button>
            </Link>
            <Link href="/about">
              <Button size="lg" variant="outline" className="border-primary-foreground/30 text-primary-foreground hover:bg-primary-foreground/10">
                Learn the Methodology
              </Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Stats */}
      <section className="py-14 px-6 bg-white border-b">
        <div className="max-w-5xl mx-auto">
          <p className="text-center text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-10">The Problem in Numbers</p>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
            {STATS.map((stat) => (
              <div key={stat.value} className="text-center">
                <div className="text-3xl font-bold text-primary mb-1">{stat.value}</div>
                <div className="text-sm text-foreground mb-1">{stat.label}</div>
                <div className="text-xs text-muted-foreground">{stat.source}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="py-16 px-6">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-foreground mb-3">How ARAL Works</h2>
            <p className="text-muted-foreground">A four-step process that takes under 5 minutes</p>
          </div>
          <div className="grid sm:grid-cols-2 lg:grid-cols-4 gap-8">
            {STEPS.map((step) => (
              <div key={step.number} className="relative">
                <div className="text-4xl font-bold text-primary/10 mb-3">{step.number}</div>
                <h3 className="font-semibold text-foreground mb-2">{step.title}</h3>
                <p className="text-sm text-muted-foreground leading-relaxed">{step.description}</p>
              </div>
            ))}
          </div>
          <div className="text-center mt-12">
            <Link href="/assessment">
              <Button size="lg" className="px-10">Begin Assessment</Button>
            </Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-6 bg-muted/30 border-y">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-2xl font-bold text-foreground mb-3">What Powers ARAL</h2>
            <p className="text-muted-foreground">State-of-the-art techniques applied to the Philippine context</p>
          </div>
          <div className="grid sm:grid-cols-2 gap-6">
            {FEATURES.map((f) => (
              <Card key={f.title} className="border-border">
                <CardContent className="p-6">
                  <h3 className="font-semibold text-foreground mb-2">{f.title}</h3>
                  <p className="text-sm text-muted-foreground leading-relaxed">{f.description}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* Programs covered */}
      <section className="py-16 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-2xl font-bold text-foreground mb-3">Programs Covered</h2>
          <p className="text-muted-foreground mb-8">ARAL currently supports six degree programs from University of Saint Louis Tuguegarao</p>
          <div className="flex flex-wrap justify-center gap-3">
            {["BS Accountancy","BS Business Administration","BS Information Technology","BS Computer Science","Bachelor of Elementary Education","BS Nursing"].map((p) => (
              <Badge key={p} variant="secondary" className="text-sm px-4 py-2">{p}</Badge>
            ))}
          </div>
        </div>
      </section>

      {/* Research team */}
      <section className="py-16 px-6 bg-primary text-primary-foreground">
        <div className="max-w-4xl mx-auto">
          <div className="text-center mb-10">
            <h2 className="text-2xl font-bold mb-2">Research Team</h2>
            <p className="text-primary-foreground/70">University of Saint Louis Tuguegarao</p>
          </div>
          <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-6">
            {TEAM.map((member) => (
              <div key={member.name} className="text-center">
                <div className="w-14 h-14 rounded-full bg-secondary mx-auto mb-3 flex items-center justify-center">
                  <span className="text-secondary-foreground font-bold text-lg">
                    {member.name.split(",")[0][0]}
                  </span>
                </div>
                <div className="font-medium text-sm">{member.name}</div>
                <div className="text-primary-foreground/60 text-xs mt-1">{member.role}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t py-8 px-6">
        <div className="max-w-5xl mx-auto flex flex-col sm:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <div className="w-6 h-6 rounded bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-xs">A</span>
            </div>
            <span className="font-semibold text-primary">ARAL</span>
            <span className="text-muted-foreground text-sm">— University of Saint Louis Tuguegarao</span>
          </div>
          <div className="flex gap-6 text-sm text-muted-foreground">
            <Link href="/about" className="hover:text-foreground transition-colors">Methodology</Link>
            <Link href="/admin" className="hover:text-foreground transition-colors">Research Dashboard</Link>
          </div>
        </div>
      </footer>
    </div>
  );
}
