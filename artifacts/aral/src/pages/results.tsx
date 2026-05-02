import { useEffect, useState } from "react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

type ShapFactor = { skill: string; skill_label: string; contribution: number; direction: string };
type SkillGap = { skill_id: string; skill_label: string; in_ched_cmo: boolean; gap_type: string; impact_score: number };
type CourseRec = { skill: string; course_title: string; platform: string; url: string; is_free: boolean; reason?: string };
type AssessmentResult = {
  vulnerability_score: number;
  risk_level: string;
  risk_label: string;
  risk_color: string;
  program_average: number;
  percentile: number;
  shap_explanation: { top_risk_factors: ShapFactor[]; top_protective_factors: ShapFactor[] };
  skill_gaps: SkillGap[];
  recommendations: CourseRec[];
  program_comparison: Record<string, number>;
  degree_program?: string;
  job_title?: string;
};

const PLATFORM_COLORS: Record<string, string> = {
  "Coursera": "#0056D2",
  "edX": "#8B44AC",
  "Google Digital Garage": "#4285F4",
  "LinkedIn Learning": "#0A66C2",
  "FutureLearn": "#E7005B",
  "TESDA Online Program": "#C0392B",
  "DepEd Commons": "#27AE60",
  "Udemy": "#A435F0",
  "Pluralsight": "#F15B2A",
  "Skillshare": "#00CC76",
  "DataCamp": "#03EF62",
  "Y Combinator": "#FF6600",
  "The Odin Project": "#CBD5E1",
  "freeCodeCamp": "#0A0A23",
  "IBM via Coursera": "#0F62FE",
  "WHO OpenWHO": "#0093D5",
};

function VulnerabilityGauge({ score, color }: { score: number; color: string }) {
  const radius = 80;
  const circumference = Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 1);

  const angleToXY = (progress: number) => {
    const angle = -180 + progress * 180;
    const rad = (angle * Math.PI) / 180;
    return { x: 100 + radius * Math.cos(rad), y: 100 + radius * Math.sin(rad) };
  };
  const needle = angleToXY(progress * 0.75 + 0.125);

  return (
    <div className="flex flex-col items-center">
      <svg width="220" height="130" viewBox="0 0 220 130">
        {/* Track */}
        <path d={`M 20 110 A ${radius} ${radius} 0 0 1 200 110`} fill="none" stroke="hsl(214 32% 91%)" strokeWidth="16" strokeLinecap="round" />
        {/* Zone bands */}
        {[
          { from: 0, to: 0.29, color: "#22c55e" },
          { from: 0.30, to: 0.49, color: "#f59e0b" },
          { from: 0.50, to: 0.69, color: "#f97316" },
          { from: 0.70, to: 1.0, color: "#ef4444" },
        ].map(({ from, to, color: zc }) => {
          const p1 = angleToXY(from);
          const p2 = angleToXY(to);
          const largeArc = to - from > 0.5 ? 1 : 0;
          return (
            <path
              key={from}
              d={`M ${p1.x + 20} ${p1.y + 10} A ${radius} ${radius} 0 ${largeArc} 1 ${p2.x + 20} ${p2.y + 10}`}
              fill="none"
              stroke={zc}
              strokeWidth="16"
              strokeOpacity="0.25"
              strokeLinecap="butt"
            />
          );
        })}
        {/* Progress arc */}
        <path
          d={`M 20 110 A ${radius} ${radius} 0 0 1 200 110`}
          fill="none"
          stroke={color}
          strokeWidth="16"
          strokeLinecap="round"
          strokeDasharray={`${circumference * progress} ${circumference}`}
          style={{ transition: "stroke-dasharray 1.2s cubic-bezier(0.4,0,0.2,1)" }}
        />
        {/* Needle */}
        {(() => {
          const angle = -180 + progress * 180;
          const rad = (angle * Math.PI) / 180;
          const nx = 110 + radius * 0.72 * Math.cos(rad);
          const ny = 110 + radius * 0.72 * Math.sin(rad);
          return (
            <>
              <line x1="110" y1="110" x2={nx} y2={ny} stroke={color} strokeWidth="3" strokeLinecap="round" />
              <circle cx="110" cy="110" r="6" fill={color} />
              <circle cx="110" cy="110" r="3" fill="white" />
            </>
          );
        })()}
        {/* Scale labels */}
        <text x="18" y="125" fontSize="10" fill="hsl(215 16% 47%)" textAnchor="middle">0.0</text>
        <text x="110" y="22" fontSize="10" fill="hsl(215 16% 47%)" textAnchor="middle">0.5</text>
        <text x="202" y="125" fontSize="10" fill="hsl(215 16% 47%)" textAnchor="middle">1.0</text>
      </svg>
      <div className="text-5xl font-bold mt-1" style={{ color }}>{score.toFixed(2)}</div>
      <div className="text-sm text-muted-foreground mt-1">out of 1.00</div>
    </div>
  );
}

function CourseBadge({ course }: { course: CourseRec }) {
  const color = PLATFORM_COLORS[course.platform] ?? "#666";
  return (
    <div className="flex items-start gap-4 p-4 border rounded-lg hover:bg-muted/20 transition-colors group">
      <div className="flex-1 min-w-0">
        <div className="flex flex-wrap items-center gap-2 mb-1.5">
          <span
            className="text-[11px] font-bold px-2 py-0.5 rounded text-white whitespace-nowrap"
            style={{ backgroundColor: color }}
          >
            {course.platform}
          </span>
          <Badge
            variant={course.is_free ? "secondary" : "outline"}
            className={`text-[11px] ${course.is_free ? "bg-green-50 text-green-700 border-green-200" : "text-amber-700 border-amber-300 bg-amber-50"}`}
          >
            {course.is_free ? "Free" : "Paid"}
          </Badge>
        </div>
        <p className="font-semibold text-sm text-foreground leading-snug">{course.course_title}</p>
        {course.reason && (
          <p className="text-xs text-muted-foreground mt-1 leading-relaxed">{course.reason}</p>
        )}
        <p className="text-xs text-muted-foreground/60 mt-1 italic">Addresses: {course.skill}</p>
      </div>
      <a
        href={course.url}
        target="_blank"
        rel="noopener noreferrer"
        className="flex-shrink-0"
      >
        <Button size="sm" variant="outline" className="text-xs whitespace-nowrap">
          Enroll →
        </Button>
      </a>
    </div>
  );
}

export default function Results() {
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [courseFilter, setCourseFilter] = useState<"all" | "free" | "paid">("all");

  useEffect(() => {
    const stored = localStorage.getItem("aral_last_result");
    if (stored) {
      try { setResult(JSON.parse(stored)); } catch {}
    }
  }, []);

  if (!result) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center max-w-sm px-6">
          <div className="text-5xl mb-5">📋</div>
          <h2 className="text-xl font-semibold text-foreground mb-2">No Results Yet</h2>
          <p className="text-muted-foreground text-sm mb-6">
            Complete the ARAL assessment first to see your automation vulnerability report.
          </p>
          <Link href="/assessment">
            <Button size="lg">Take the Assessment</Button>
          </Link>
        </div>
      </div>
    );
  }

  const {
    vulnerability_score, risk_level, risk_label, risk_color,
    program_average, percentile, shap_explanation, skill_gaps,
    recommendations, program_comparison, degree_program, job_title,
  } = result;

  const shapData = [
    ...shap_explanation.top_risk_factors.slice(0, 5).map((f) => ({
      name: f.skill_label.length > 30 ? f.skill_label.slice(0, 30) + "…" : f.skill_label,
      value: Math.abs(f.contribution),
      direction: "risk",
    })),
    ...shap_explanation.top_protective_factors.slice(0, 5).map((f) => ({
      name: f.skill_label.length > 30 ? f.skill_label.slice(0, 30) + "…" : f.skill_label,
      value: -Math.abs(f.contribution),
      direction: "protect",
    })),
  ].sort((a, b) => b.value - a.value);

  const compData = Object.entries(program_comparison)
    .map(([prog, score]) => ({
      name: prog.replace("Bachelor of ", "B. of ").replace("BS ", ""),
      full: prog,
      score,
      isUser: prog === degree_program,
    }))
    .sort((a, b) => a.score - b.score);

  const freeCourses = recommendations.filter((r) => r.is_free);
  const paidCourses = recommendations.filter((r) => !r.is_free);
  const displayedCourses =
    courseFilter === "free" ? freeCourses
    : courseFilter === "paid" ? paidCourses
    : recommendations;

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
          <Link href="/assessment">
            <Button variant="outline" size="sm">New Assessment</Button>
          </Link>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
        {/* Context badges */}
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary" className="text-sm">{degree_program}</Badge>
          {job_title && <Badge variant="outline" className="text-sm">{job_title}</Badge>}
          <Badge variant="outline" className="text-xs text-muted-foreground">POARD Dataset — 2,000 Respondents</Badge>
        </div>

        {/* Score card */}
        <Card className="border-2" style={{ borderColor: risk_color + "50" }}>
          <CardContent className="p-8">
            <p className="text-center text-sm font-semibold text-muted-foreground uppercase tracking-wider mb-6">
              Automation Vulnerability Score
            </p>
            <VulnerabilityGauge score={vulnerability_score} color={risk_color} />
            <div className="flex justify-center mt-5">
              <Badge className="text-sm px-5 py-2 font-semibold" style={{ backgroundColor: risk_color, color: "#fff" }}>
                {risk_level} Risk
              </Badge>
            </div>
            <p className="text-center text-muted-foreground text-sm mt-3 max-w-md mx-auto">{risk_label}</p>

            <Separator className="my-6" />

            <div className="grid grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-3xl font-bold text-foreground">{(vulnerability_score * 100).toFixed(0)}%</div>
                <div className="text-xs text-muted-foreground mt-1">Your Score</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">{(program_average * 100).toFixed(0)}%</div>
                <div className="text-xs text-muted-foreground mt-1">Program Average</div>
              </div>
              <div>
                <div className="text-3xl font-bold text-foreground">{percentile}th</div>
                <div className="text-xs text-muted-foreground mt-1">Percentile</div>
              </div>
            </div>

            {/* Risk level legend */}
            <div className="flex justify-center gap-4 mt-6 flex-wrap">
              {[
                { level: "Low", color: "#22c55e", range: "0–29%" },
                { level: "Moderate", color: "#f59e0b", range: "30–49%" },
                { level: "High", color: "#f97316", range: "50–69%" },
                { level: "Very High", color: "#ef4444", range: "70–100%" },
              ].map((r) => (
                <div key={r.level} className={`flex items-center gap-1.5 text-xs ${risk_level === r.level ? "font-bold" : "text-muted-foreground"}`}>
                  <div className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: r.color }} />
                  {r.level} ({r.range})
                </div>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* SHAP Explanation */}
        {shapData.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Why You Got This Score</CardTitle>
              <p className="text-sm text-muted-foreground">
                SHAP (SHapley Additive exPlanations) — positive bars increase risk, negative bars protect you
              </p>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={280}>
                <BarChart data={shapData} layout="vertical" margin={{ left: 4, right: 48, top: 4, bottom: 4 }}>
                  <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                  <XAxis
                    type="number"
                    tickFormatter={(v) => `${(v * 100).toFixed(0)}%`}
                    tick={{ fontSize: 11 }}
                    domain={["auto", "auto"]}
                  />
                  <YAxis type="category" dataKey="name" width={196} tick={{ fontSize: 11 }} />
                  <Tooltip
                    formatter={(v: number) => [
                      `${(Math.abs(v) * 100).toFixed(1)}% ${v > 0 ? "↑ Risk" : "↓ Protective"}`,
                      "SHAP Contribution",
                    ]}
                  />
                  <Bar dataKey="value" radius={[0, 4, 4, 0]} maxBarSize={22}>
                    {shapData.map((entry, i) => (
                      <Cell key={i} fill={entry.value > 0 ? "#ef4444" : "#22c55e"} />
                    ))}
                  </Bar>
                </BarChart>
              </ResponsiveContainer>
              <div className="flex gap-6 mt-3 text-xs text-muted-foreground">
                <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-sm bg-red-500" /> Increases your risk</div>
                <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-sm bg-green-500" /> Reduces your risk</div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Skill Gaps */}
        {skill_gaps.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Identified Skill Gaps</CardTitle>
              <p className="text-sm text-muted-foreground">
                Skills that would most reduce your vulnerability — cross-referenced with your CHED CMO curriculum
              </p>
            </CardHeader>
            <CardContent className="space-y-3">
              {skill_gaps.map((gap) => (
                <div key={gap.skill_id} className="flex items-start gap-4 p-4 border rounded-lg">
                  <div
                    className="w-2.5 h-2.5 rounded-full mt-1.5 flex-shrink-0"
                    style={{ backgroundColor: gap.impact_score > 0.06 ? "#ef4444" : "#f59e0b" }}
                  />
                  <div className="flex-1 min-w-0">
                    <div className="flex flex-wrap items-center gap-2 mb-1">
                      <span className="font-semibold text-sm text-foreground">{gap.skill_label}</span>
                      <Badge
                        variant={gap.impact_score > 0.06 ? "destructive" : "secondary"}
                        className="text-[11px]"
                      >
                        {gap.impact_score > 0.06 ? "High Impact" : "Medium Impact"}
                      </Badge>
                      <Badge variant="outline" className="text-[11px]">
                        {gap.in_ched_cmo
                          ? "In CHED CMO — underperformed"
                          : "Not in CHED CMO — design gap"}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground">
                      Protective SHAP value: <strong>{(gap.impact_score * 100).toFixed(1)}%</strong> reduction potential
                    </p>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Course Recommendations */}
        {recommendations.length > 0 && (
          <Card>
            <CardHeader>
              <div className="flex flex-col sm:flex-row sm:items-start sm:justify-between gap-4">
                <div>
                  <CardTitle className="text-base">Upskilling Recommendations</CardTitle>
                  <p className="text-sm text-muted-foreground mt-1">
                    {freeCourses.length} free · {paidCourses.length} paid · {recommendations.length} total courses
                  </p>
                </div>
                <div className="flex gap-2">
                  {(["all", "free", "paid"] as const).map((f) => (
                    <button
                      key={f}
                      onClick={() => setCourseFilter(f)}
                      className={`px-3 py-1.5 rounded-lg text-xs font-medium capitalize border transition-colors ${
                        courseFilter === f
                          ? "bg-primary text-primary-foreground border-primary"
                          : "border-border text-muted-foreground hover:border-primary/40"
                      }`}
                    >
                      {f === "all" ? `All (${recommendations.length})` : f === "free" ? `Free (${freeCourses.length})` : `Paid (${paidCourses.length})`}
                    </button>
                  ))}
                </div>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              {displayedCourses.length === 0 ? (
                <p className="text-sm text-muted-foreground text-center py-6">No {courseFilter} courses available for the identified gaps.</p>
              ) : (
                displayedCourses.map((rec, i) => <CourseBadge key={i} course={rec} />)
              )}
            </CardContent>
          </Card>
        )}

        {/* Program Comparison */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Cross-Program Comparison</CardTitle>
            <p className="text-sm text-muted-foreground">Mean automation vulnerability by degree (POARD — 2,000 respondents)</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={compData} layout="vertical" margin={{ left: 8, right: 56, top: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={196} tick={{ fontSize: 11 }} />
                <Tooltip
                  formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, "Mean Vulnerability"]}
                  labelFormatter={(label: string) => {
                    const item = compData.find((p) => p.name === label);
                    return item?.full ?? label;
                  }}
                />
                <Bar dataKey="score" radius={[0, 4, 4, 0]} maxBarSize={26}>
                  {compData.map((entry, i) => (
                    <Cell key={i} fill={entry.isUser ? risk_color : "hsl(214 32% 80%)"} fillOpacity={entry.isUser ? 1 : 0.7} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-muted-foreground mt-3 text-center">
              <span style={{ color: risk_color }}>■</span> Your program ({degree_program})
            </p>
          </CardContent>
        </Card>

        <div className="flex flex-col sm:flex-row gap-4 pb-8">
          <Link href="/assessment" className="flex-1">
            <Button variant="outline" className="w-full">Retake Assessment</Button>
          </Link>
          <Link href="/about" className="flex-1">
            <Button variant="outline" className="w-full">Learn the Methodology</Button>
          </Link>
          <Link href="/admin" className="flex-1">
            <Button variant="outline" className="w-full">Research Dashboard</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
