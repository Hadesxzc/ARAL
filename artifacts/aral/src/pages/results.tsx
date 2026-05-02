import { useEffect, useState } from "react";
import { Link, useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Progress } from "@/components/ui/progress";
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
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

function VulnerabilityGauge({ score, color }: { score: number; color: string }) {
  const radius = 80;
  const circumference = Math.PI * radius;
  const progress = Math.min(Math.max(score, 0), 1);
  const dashOffset = circumference * (1 - progress);

  return (
    <div className="flex flex-col items-center">
      <svg width="200" height="120" viewBox="0 0 200 120">
        {/* Background arc */}
        <path
          d={`M 20 100 A ${radius} ${radius} 0 0 1 180 100`}
          fill="none"
          stroke="hsl(214 32% 91%)"
          strokeWidth="14"
          strokeLinecap="round"
        />
        {/* Zone colors */}
        <path d={`M 20 100 A ${radius} ${radius} 0 0 1 80 26`} fill="none" stroke="#22c55e" strokeWidth="14" strokeOpacity="0.3" strokeLinecap="round" />
        <path d={`M 80 26 A ${radius} ${radius} 0 0 1 120 26`} fill="none" stroke="#f59e0b" strokeWidth="14" strokeOpacity="0.3" strokeLinecap="round" />
        <path d={`M 120 26 A ${radius} ${radius} 0 0 1 155 45`} fill="none" stroke="#f97316" strokeWidth="14" strokeOpacity="0.3" strokeLinecap="round" />
        <path d={`M 155 45 A ${radius} ${radius} 0 0 1 180 100`} fill="none" stroke="#ef4444" strokeWidth="14" strokeOpacity="0.3" strokeLinecap="round" />
        {/* Progress arc */}
        <path
          d={`M 20 100 A ${radius} ${radius} 0 0 1 180 100`}
          fill="none"
          stroke={color}
          strokeWidth="14"
          strokeLinecap="round"
          strokeDasharray={`${circumference * progress} ${circumference * (1 - progress)}`}
          style={{ transition: "stroke-dasharray 1s ease" }}
        />
        {/* Needle */}
        {(() => {
          const angle = -180 + progress * 180;
          const rad = (angle * Math.PI) / 180;
          const nx = 100 + radius * 0.75 * Math.cos(rad);
          const ny = 100 + radius * 0.75 * Math.sin(rad);
          return <line x1="100" y1="100" x2={nx} y2={ny} stroke={color} strokeWidth="3" strokeLinecap="round" />;
        })()}
        <circle cx="100" cy="100" r="5" fill={color} />
        {/* Labels */}
        <text x="18" y="115" fontSize="10" fill="hsl(215 16% 47%)" textAnchor="middle">0.0</text>
        <text x="100" y="16" fontSize="10" fill="hsl(215 16% 47%)" textAnchor="middle">0.5</text>
        <text x="182" y="115" fontSize="10" fill="hsl(215 16% 47%)" textAnchor="middle">1.0</text>
      </svg>
      <div className="text-4xl font-bold mt-1" style={{ color }}>{score.toFixed(2)}</div>
    </div>
  );
}

const PLATFORM_COLORS: Record<string, string> = {
  Coursera: "#0056D2",
  edX: "#8B44AC",
  "Google Digital Garage": "#4285F4",
  "LinkedIn Learning": "#0A66C2",
  FutureLearn: "#E7005B",
  "TESDA Online Program": "#C0392B",
  "DepEd Commons": "#27AE60",
};

export default function Results() {
  const [result, setResult] = useState<AssessmentResult | null>(null);
  const [, setLocation] = useLocation();

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
          <div className="text-4xl mb-4">📋</div>
          <h2 className="text-xl font-semibold text-foreground mb-2">No Results Found</h2>
          <p className="text-muted-foreground text-sm mb-6">Please complete the ARAL assessment first to see your automation vulnerability results.</p>
          <Link href="/assessment"><Button>Take the Assessment</Button></Link>
        </div>
      </div>
    );
  }

  const { vulnerability_score, risk_level, risk_label, risk_color, program_average, percentile, shap_explanation, skill_gaps, recommendations, program_comparison, degree_program, job_title } = result;

  // SHAP chart data
  const shapData = [
    ...shap_explanation.top_risk_factors.slice(0, 4).map((f) => ({ name: f.skill_label.length > 28 ? f.skill_label.slice(0, 28) + "…" : f.skill_label, value: f.contribution, direction: "risk" })),
    ...shap_explanation.top_protective_factors.slice(0, 4).map((f) => ({ name: f.skill_label.length > 28 ? f.skill_label.slice(0, 28) + "…" : f.skill_label, value: -f.contribution, direction: "protect" })),
  ].sort((a, b) => b.value - a.value);

  // Program comparison
  const compData = Object.entries(program_comparison)
    .map(([prog, score]) => ({ name: prog, score, isUser: prog === degree_program }))
    .sort((a, b) => a.score - b.score);

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
          <Link href="/assessment"><Button variant="outline" size="sm">New Assessment</Button></Link>
        </div>
      </header>

      <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
        {/* Context */}
        <div className="flex flex-wrap items-center gap-2">
          <Badge variant="secondary">{degree_program}</Badge>
          {job_title && <Badge variant="outline">{job_title}</Badge>}
        </div>

        {/* Score Card */}
        <Card className="border-2" style={{ borderColor: risk_color + "40" }}>
          <CardContent className="p-8">
            <div className="text-center mb-6">
              <h1 className="text-lg font-semibold text-muted-foreground mb-4">Your Automation Vulnerability Score</h1>
              <VulnerabilityGauge score={vulnerability_score} color={risk_color} />
              <div className="mt-4">
                <Badge className="text-sm px-4 py-1.5" style={{ backgroundColor: risk_color, color: "#fff" }}>
                  {risk_level} Risk
                </Badge>
              </div>
              <p className="text-muted-foreground text-sm mt-3">{risk_label}</p>
            </div>
            <Separator className="my-6" />
            <div className="grid grid-cols-3 gap-6 text-center">
              <div>
                <div className="text-2xl font-bold text-foreground">{(vulnerability_score * 100).toFixed(0)}%</div>
                <div className="text-xs text-muted-foreground mt-1">Your Score</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{(program_average * 100).toFixed(0)}%</div>
                <div className="text-xs text-muted-foreground mt-1">Program Average</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-foreground">{percentile}th</div>
                <div className="text-xs text-muted-foreground mt-1">Percentile</div>
              </div>
            </div>
            {percentile > 50 && (
              <p className="text-center text-sm text-muted-foreground mt-4">
                You are more vulnerable than <strong>{percentile}%</strong> of {degree_program} graduates in our dataset.
              </p>
            )}
          </CardContent>
        </Card>

        {/* SHAP Explanation */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">Why You Got This Score</CardTitle>
            <p className="text-sm text-muted-foreground">SHAP (SHapley Additive exPlanations) analysis shows what drives your vulnerability</p>
          </CardHeader>
          <CardContent>
            {shapData.length > 0 ? (
              <>
                <ResponsiveContainer width="100%" height={260}>
                  <BarChart data={shapData} layout="vertical" margin={{ left: 4, right: 32, top: 4, bottom: 4 }}>
                    <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                    <XAxis type="number" tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 11 }} />
                    <YAxis type="category" dataKey="name" width={180} tick={{ fontSize: 11 }} />
                    <Tooltip formatter={(v: number) => [`${(Math.abs(v) * 100).toFixed(1)}%`, "SHAP Contribution"]} />
                    <Bar dataKey="value" radius={[0, 4, 4, 0]}>
                      {shapData.map((entry, i) => (
                        <Cell key={i} fill={entry.value > 0 ? "#ef4444" : "#22c55e"} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
                <div className="flex gap-6 mt-4 text-xs text-muted-foreground">
                  <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-sm bg-red-500" /> Increases your risk</div>
                  <div className="flex items-center gap-2"><div className="w-3 h-3 rounded-sm bg-green-500" /> Reduces your risk</div>
                </div>
              </>
            ) : (
              <div className="py-8 text-center text-sm text-muted-foreground">SHAP analysis data not available for this assessment.</div>
            )}
          </CardContent>
        </Card>

        {/* Skill Gaps */}
        {skill_gaps.length > 0 && (
          <Card>
            <CardHeader>
              <CardTitle className="text-base">Your Skill Gaps</CardTitle>
              <p className="text-sm text-muted-foreground">Skills that would reduce your automation vulnerability but are currently missing</p>
            </CardHeader>
            <CardContent className="space-y-3">
              {skill_gaps.map((gap) => (
                <div key={gap.skill_id} className="flex items-start gap-4 p-4 border rounded-lg">
                  <div className={`w-2 h-2 rounded-full mt-2 flex-shrink-0 ${gap.impact_score > 0.07 ? "bg-destructive" : "bg-amber-500"}`} />
                  <div className="flex-1">
                    <div className="flex items-center gap-2 flex-wrap">
                      <span className="font-medium text-sm text-foreground">{gap.skill_label}</span>
                      <Badge variant="outline" className="text-xs">
                        {gap.impact_score > 0.07 ? "High Impact" : "Medium Impact"}
                      </Badge>
                      <Badge variant={gap.in_ched_cmo ? "secondary" : "outline"} className="text-xs">
                        {gap.gap_type === "implementation" ? "In CHED CMO — low proficiency" : "Not in CHED CMO"}
                      </Badge>
                    </div>
                    <p className="text-xs text-muted-foreground mt-1">
                      SHAP contribution: {(gap.impact_score * 100).toFixed(1)}% reduction potential
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
              <CardTitle className="text-base">Recommended Free Courses</CardTitle>
              <p className="text-sm text-muted-foreground">AI-generated course recommendations to address your skill gaps</p>
            </CardHeader>
            <CardContent className="space-y-3">
              {recommendations.map((rec, i) => (
                <div key={i} className="p-4 border rounded-lg hover:bg-muted/30 transition-colors">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-2 mb-1">
                        <span
                          className="text-xs font-semibold px-2 py-0.5 rounded text-white"
                          style={{ backgroundColor: PLATFORM_COLORS[rec.platform] ?? "#666" }}
                        >
                          {rec.platform}
                        </span>
                        {rec.is_free && <Badge variant="secondary" className="text-xs">Free</Badge>}
                      </div>
                      <p className="font-medium text-sm text-foreground">{rec.course_title}</p>
                      {rec.reason && <p className="text-xs text-muted-foreground mt-1">{rec.reason}</p>}
                      <p className="text-xs text-muted-foreground mt-1">For: <em>{rec.skill}</em></p>
                    </div>
                    <a href={rec.url} target="_blank" rel="noopener noreferrer">
                      <Button size="sm" variant="outline" className="flex-shrink-0 text-xs">
                        Take Course
                      </Button>
                    </a>
                  </div>
                </div>
              ))}
            </CardContent>
          </Card>
        )}

        {/* Program Comparison */}
        <Card>
          <CardHeader>
            <CardTitle className="text-base">How You Compare to Other Programs</CardTitle>
            <p className="text-sm text-muted-foreground">Mean automation vulnerability score by degree program (POARD dataset)</p>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={260}>
              <BarChart data={compData} layout="vertical" margin={{ left: 8, right: 48, top: 4, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 11 }} />
                <YAxis type="category" dataKey="name" width={200} tick={{ fontSize: 11 }} />
                <Tooltip formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, "Mean Vulnerability"]} />
                <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                  {compData.map((entry, i) => (
                    <Cell key={i} fill={entry.isUser ? risk_color : "hsl(214 32% 81%)"} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
            <p className="text-xs text-muted-foreground mt-3 text-center">Your program ({degree_program}) is highlighted</p>
          </CardContent>
        </Card>

        <div className="flex flex-col sm:flex-row gap-4">
          <Link href="/assessment" className="flex-1">
            <Button variant="outline" className="w-full">Retake Assessment</Button>
          </Link>
          <Link href="/about" className="flex-1">
            <Button variant="outline" className="w-full">Learn the Methodology</Button>
          </Link>
        </div>
      </div>
    </div>
  );
}
