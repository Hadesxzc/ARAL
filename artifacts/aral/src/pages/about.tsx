import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";

const TEAM = [
  { role: "Lead Researcher", name: "Gasmen, Kenneth R." },
  { role: "Developer", name: "Ignacio, John Jomer R." },
  { role: "Data Analysis", name: "Maddara, Darren Bjorn P." },
  { role: "Developer", name: "Tarayao, Mark Daniel B." },
];

const TECH_STACK = [
  { layer: "Frontend", tech: "React + TypeScript + Vite" },
  { layer: "Backend", tech: "Python (FastAPI)" },
  { layer: "ML Model", tech: "scikit-learn (Random Forest Regressor)" },
  { layer: "Explainability", tech: "SHAP Python library" },
  { layer: "AI Recommendations", tech: "Google Gemini 2.5 Flash API" },
  { layer: "Database", tech: "PostgreSQL" },
  { layer: "Dataset", tech: "POARD (Philippine Occupation-Automation Reference Dataset)" },
];

export default function About() {
  return (
    <div className="min-h-screen bg-background">
      {/* Nav */}
      <header className="border-b bg-white/80 backdrop-blur-sm sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-6 h-16 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="w-8 h-8 rounded bg-primary flex items-center justify-center">
              <span className="text-primary-foreground font-bold text-sm">A</span>
            </div>
            <span className="font-bold text-primary">ARAL</span>
          </Link>
          <nav className="flex items-center gap-6">
            <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">Home</Link>
            <Link href="/admin" className="text-sm text-muted-foreground hover:text-foreground">Research</Link>
            <Link href="/assessment">
              <Button size="sm">Start Assessment</Button>
            </Link>
          </nav>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-12">
        {/* Hero */}
        <div className="mb-12">
          <Badge className="mb-4">Research Documentation</Badge>
          <h1 className="text-3xl font-bold text-foreground mb-4">About ARAL</h1>
          <p className="text-lg text-muted-foreground leading-relaxed">
            ARAL (<em>Automation Risk Assessment for Lokalized graduates</em>) is a full-stack academic research system developed at 
            the University of Saint Louis Tuguegarao. It predicts how vulnerable a Filipino college graduate's career is to 
            AI and automation, explains the prediction using SHAP, identifies skill gaps against CHED CMO standards, and 
            recommends free online courses for upskilling.
          </p>
        </div>

        <Separator className="mb-12" />

        {/* Problem */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">The Problem</h2>
          <div className="grid sm:grid-cols-2 gap-4">
            {[
              { stat: "1 in 3", desc: "Filipino workers are highly exposed to automation (IMF, 2025)" },
              { stat: "800,000+", desc: "Graduates enter the workforce annually without personalized risk signals" },
              { stat: "11 years", desc: "Average CHED curriculum update cycle (EDCOM II, 2026)" },
              { stat: "0", desc: "Existing tools providing localized, data-driven career risk assessment for PH graduates" },
            ].map((item) => (
              <Card key={item.stat} className="border">
                <CardContent className="p-5">
                  <div className="text-2xl font-bold text-primary mb-1">{item.stat}</div>
                  <p className="text-sm text-muted-foreground">{item.desc}</p>
                </CardContent>
              </Card>
            ))}
          </div>
        </section>

        {/* Dataset */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">POARD — The Dataset</h2>
          <Card className="border mb-4">
            <CardContent className="p-6">
              <p className="font-semibold text-foreground mb-2">Philippine Occupation-Automation Reference Dataset</p>
              <p className="text-sm text-muted-foreground leading-relaxed mb-4">
                POARD is an original research contribution — it does not exist publicly. It was constructed by the research 
                team in four steps: (1) extracting O*NET 29.0 task data and Frey & Osborne automation probability scores, 
                (2) applying a SOC → ISCO-08 → PSOC 2022 crosswalk for Philippine occupation codes, (3) integrating survey 
                data from 1,000 Filipino graduate respondents, and (4) computing a localized vulnerability score per respondent.
              </p>
              <div className="bg-muted rounded-lg p-4 font-mono text-xs text-foreground">
                <p className="text-muted-foreground mb-2">// Vulnerability score formula:</p>
                <p>vulnerability_score = &Sigma; (task_weight_filipino[i] &times; automation_probability_onet[i])</p>
              </div>
            </CardContent>
          </Card>
          <p className="text-sm text-muted-foreground">
            Each respondent provided their degree program, job title (mapped to PSOC 2022), task time distribution across 
            13 O*NET task categories (summing to 100%), and binary skill proficiency ratings for all CHED CMO competencies 
            relevant to their program.
          </p>
        </section>

        {/* ML Model */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">Machine Learning Model</h2>
          <div className="grid sm:grid-cols-3 gap-4 mb-6">
            {[
              { metric: "RMSE", value: "< 0.10", desc: "Root Mean Squared Error" },
              { metric: "MAE", value: "< 0.08", desc: "Mean Absolute Error" },
              { metric: "R\u00B2", value: "> 0.75", desc: "Coefficient of Determination" },
            ].map((m) => (
              <Card key={m.metric} className="border text-center">
                <CardContent className="p-5">
                  <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">{m.metric}</div>
                  <div className="text-2xl font-bold text-primary mb-1">{m.value}</div>
                  <div className="text-xs text-muted-foreground">{m.desc}</div>
                </CardContent>
              </Card>
            ))}
          </div>
          <p className="text-sm text-muted-foreground leading-relaxed">
            The model is a Random Forest Regressor (200 estimators, stratified 80/20 train-test split by degree program) 
            trained to predict a continuous vulnerability score between 0.0 and 1.0. Input features include degree program 
            (one-hot encoded), task time distributions across 13 categories, and approximately 60 binary skill indicators 
            derived from CHED CMO competencies.
          </p>
        </section>

        {/* SHAP */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">SHAP Explainability</h2>
          <p className="text-sm text-muted-foreground leading-relaxed mb-4">
            ARAL uses SHapley Additive exPlanations (SHAP) to provide interpretable, individualized explanations for 
            each prediction. A TreeExplainer is applied to the trained Random Forest model to compute per-feature SHAP 
            values that reveal which skills and tasks push the vulnerability score up or down.
          </p>
          <div className="grid sm:grid-cols-2 gap-4">
            {[
              { title: "Per-user explanation", desc: "Individual SHAP waterfall showing the top risk and protective factors for each respondent." },
              { title: "Global feature importance", desc: "Aggregated SHAP summary identifying the most impactful features across all 1,000 respondents." },
              { title: "Per-program analysis", desc: "Degree-program-specific SHAP aggregation for curriculum gap analysis." },
              { title: "Curriculum gap detection", desc: "Protective skills with negative SHAP are cross-referenced against CHED CMOs to identify design vs. implementation gaps." },
            ].map((item) => (
              <div key={item.title} className="p-4 bg-muted/40 rounded-lg border">
                <p className="font-medium text-sm text-foreground mb-1">{item.title}</p>
                <p className="text-xs text-muted-foreground">{item.desc}</p>
              </div>
            ))}
          </div>
        </section>

        {/* Risk levels */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">Risk Level Classification</h2>
          <div className="space-y-3">
            {[
              { level: "Low", range: "0.00 – 0.29", color: "#22c55e", desc: "Career has low exposure to automation based on current skills and tasks." },
              { level: "Moderate", range: "0.30 – 0.49", color: "#f59e0b", desc: "Some tasks are automatable; targeted upskilling can reduce risk." },
              { level: "High", range: "0.50 – 0.69", color: "#f97316", desc: "Significant automation exposure; key protective skills may be missing." },
              { level: "Very High", range: "0.70 – 1.00", color: "#ef4444", desc: "High vulnerability; immediate upskilling in protective skills is recommended." },
            ].map((r) => (
              <div key={r.level} className="flex items-start gap-4 p-4 border rounded-lg">
                <div className="w-3 h-3 rounded-full mt-1 flex-shrink-0" style={{ backgroundColor: r.color }} />
                <div>
                  <span className="font-semibold text-sm text-foreground">{r.level}</span>
                  <span className="text-muted-foreground text-sm ml-2">{r.range}</span>
                  <p className="text-xs text-muted-foreground mt-1">{r.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Tech Stack */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">Technical Stack</h2>
          <div className="border rounded-lg overflow-hidden">
            {TECH_STACK.map((t, i) => (
              <div key={t.layer} className={`flex items-center px-5 py-3 ${i !== TECH_STACK.length - 1 ? "border-b" : ""}`}>
                <div className="w-40 text-sm font-medium text-muted-foreground">{t.layer}</div>
                <div className="text-sm text-foreground">{t.tech}</div>
              </div>
            ))}
          </div>
        </section>

        {/* CHED CMO */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">CHED CMO References</h2>
          <div className="space-y-2 text-sm">
            {[
              { program: "BS Accountancy", cmo: "CMO No. 3 s. 2007 as amended" },
              { program: "BS Business Administration", cmo: "CMO No. 17 s. 2017" },
              { program: "BS Information Technology", cmo: "CMO No. 25 s. 2015" },
              { program: "BS Computer Science", cmo: "CMO No. 25 s. 2015" },
              { program: "Bachelor of Elementary Education", cmo: "CMO No. 74 s. 2017" },
              { program: "BS Nursing", cmo: "CMO No. 14 s. 2009" },
            ].map((item) => (
              <div key={item.program} className="flex items-center justify-between py-2 border-b last:border-0">
                <span className="font-medium text-foreground">{item.program}</span>
                <span className="text-muted-foreground text-xs">{item.cmo}</span>
              </div>
            ))}
          </div>
        </section>

        {/* Team */}
        <section className="mb-12">
          <h2 className="text-xl font-bold text-foreground mb-4">Research Team</h2>
          <div className="border rounded-lg overflow-hidden">
            {TEAM.map((member, i) => (
              <div key={member.name} className={`flex items-center px-5 py-4 ${i !== TEAM.length - 1 ? "border-b" : ""}`}>
                <div className="w-44 text-sm text-muted-foreground">{member.role}</div>
                <div className="text-sm font-medium text-foreground">{member.name}</div>
              </div>
            ))}
          </div>
          <p className="text-xs text-muted-foreground mt-3">University of Saint Louis Tuguegarao — College Research</p>
        </section>

        <div className="text-center">
          <Link href="/assessment">
            <Button size="lg">Take the ARAL Assessment</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
