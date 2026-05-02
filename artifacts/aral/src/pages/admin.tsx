import { useState } from "react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Tabs, TabsList, TabsTrigger, TabsContent } from "@/components/ui/tabs";
import { Separator } from "@/components/ui/separator";
import { Slider } from "@/components/ui/slider";
import { Spinner } from "@/components/ui/spinner";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";
import {
  useGetProgramSummary,
  useGetGlobalStats,
  useGetSusResults,
  useSubmitSus,
  getGetProgramSummaryQueryKey,
  getGetGlobalStatsQueryKey,
  getGetSusResultsQueryKey,
} from "@workspace/api-client-react";

const SUS_QUESTIONS = [
  "I think that I would like to use this system frequently.",
  "I found the system unnecessarily complex.",
  "I thought the system was easy to use.",
  "I think that I would need the support of a technical person to use this system.",
  "I found the various functions in this system were well integrated.",
  "I thought there was too much inconsistency in this system.",
  "I would imagine that most people would learn to use this system very quickly.",
  "I found the system very cumbersome to use.",
  "I felt very confident using the system.",
  "I needed to learn a lot of things before I could get going with this system.",
];

const RISK_COLORS: Record<string, string> = {
  "BS Accountancy": "#ef4444",
  "BS Business Administration": "#f97316",
  "BS Information Technology": "#f59e0b",
  "BS Computer Science": "#22c55e",
  "Bachelor of Elementary Education": "#3b82f6",
  "BS Nursing": "#22c55e",
};

export default function Admin() {
  const [susResponses, setSusResponses] = useState<number[]>(Array(10).fill(3));
  const [susSubmitted, setSusSubmitted] = useState(false);
  const [susResult, setSusResult] = useState<{ sus_score: number; interpretation: string; grade: string } | null>(null);

  const { data: summaryData, isLoading: summaryLoading } = useGetProgramSummary({
    query: { queryKey: getGetProgramSummaryQueryKey() },
  });
  const { data: globalData, isLoading: globalLoading } = useGetGlobalStats({
    query: { queryKey: getGetGlobalStatsQueryKey() },
  });
  const { data: susData, isLoading: susLoading, refetch: refetchSus } = useGetSusResults({
    query: { queryKey: getGetSusResultsQueryKey() },
  });
  const { mutate: submitSus, isPending: susSubmitting } = useSubmitSus();

  const programs = summaryData?.programs ?? [];
  const globalStats = globalData;

  // Program averages chart
  const programAvgData = programs.map((p: { program: string; mean_vulnerability: number; respondent_count: number }) => ({
    name: p.program.replace("Bachelor of ", "B. of ").replace("BS ", ""),
    score: p.mean_vulnerability,
    full: p.program,
  })).sort((a: { score: number }, b: { score: number }) => a.score - b.score);

  const scoreDistData = globalStats?.score_distribution ?? [];

  const handleSusSubmit = () => {
    submitSus(
      { data: { responses: susResponses } },
      {
        onSuccess: (result: { sus_score: number; interpretation: string; grade: string }) => {
          setSusResult(result);
          setSusSubmitted(true);
          refetchSus();
        },
      }
    );
  };

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
          <div className="flex items-center gap-4">
            <Badge variant="outline" className="text-xs">Research Dashboard</Badge>
            <Link href="/assessment"><Button size="sm">Take Assessment</Button></Link>
          </div>
        </div>
      </header>

      <div className="max-w-5xl mx-auto px-6 py-10">
        <div className="mb-8">
          <h1 className="text-2xl font-bold text-foreground">Research Dashboard</h1>
          <p className="text-muted-foreground text-sm mt-1">Aggregated SHAP findings and statistics from the POARD dataset</p>
        </div>

        <Tabs defaultValue="overview">
          <TabsList className="mb-6">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="shap">SHAP Analysis</TabsTrigger>
            <TabsTrigger value="programs">Per-Program</TabsTrigger>
            <TabsTrigger value="curriculum">Curriculum Gaps</TabsTrigger>
            <TabsTrigger value="sus">SUS Evaluation</TabsTrigger>
          </TabsList>

          {/* Overview Tab */}
          <TabsContent value="overview" className="space-y-6">
            {globalLoading ? (
              <div className="flex justify-center py-16"><Spinner className="w-8 h-8 text-primary" /></div>
            ) : (
              <>
                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
                  {[
                    { label: "Total Respondents", value: globalStats?.total_respondents ?? 0 },
                    { label: "Mean Vulnerability", value: globalStats ? `${(globalStats.overall_mean_vulnerability * 100).toFixed(1)}%` : "—" },
                    { label: "Programs Covered", value: programs.length },
                    { label: "SUS Responses", value: susData?.total_responses ?? 0 },
                  ].map((stat) => (
                    <Card key={stat.label}>
                      <CardContent className="p-5 text-center">
                        <div className="text-2xl font-bold text-primary">{stat.value}</div>
                        <div className="text-xs text-muted-foreground mt-1">{stat.label}</div>
                      </CardContent>
                    </Card>
                  ))}
                </div>

                <Card>
                  <CardHeader><CardTitle className="text-base">Mean Vulnerability by Program</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={260}>
                      <BarChart data={programAvgData} layout="vertical" margin={{ left: 8, right: 48, top: 4, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="3 3" horizontal={false} />
                        <XAxis type="number" domain={[0, 1]} tickFormatter={(v) => `${(v * 100).toFixed(0)}%`} tick={{ fontSize: 11 }} />
                        <YAxis type="category" dataKey="name" width={160} tick={{ fontSize: 11 }} />
                        <Tooltip formatter={(v: number) => [`${(v * 100).toFixed(1)}%`, "Mean Vulnerability"]} labelFormatter={(label: string) => {
                          const item = programAvgData.find((p: { name: string }) => p.name === label);
                          return item?.full ?? label;
                        }} />
                        <Bar dataKey="score" radius={[0, 4, 4, 0]}>
                          {programAvgData.map((entry: { full: string }, i: number) => (
                            <Cell key={i} fill={RISK_COLORS[entry.full] ?? "hsl(220 80% 20%)"} />
                          ))}
                        </Bar>
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader><CardTitle className="text-base">Score Distribution (All Programs)</CardTitle></CardHeader>
                  <CardContent>
                    <ResponsiveContainer width="100%" height={200}>
                      <BarChart data={scoreDistData} margin={{ left: 0, right: 16, top: 4, bottom: 4 }}>
                        <CartesianGrid strokeDasharray="3 3" vertical={false} />
                        <XAxis dataKey="range" tick={{ fontSize: 11 }} />
                        <YAxis tick={{ fontSize: 11 }} />
                        <Tooltip />
                        <Bar dataKey="count" fill="hsl(220 80% 20%)" radius={[4, 4, 0, 0]} />
                      </BarChart>
                    </ResponsiveContainer>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* SHAP Global Analysis Tab */}
          <TabsContent value="shap" className="space-y-6">
            {globalLoading ? (
              <div className="flex justify-center py-16"><Spinner className="w-8 h-8 text-primary" /></div>
            ) : (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Top Global Risk Skills</CardTitle>
                    <p className="text-sm text-muted-foreground">Features that increase automation vulnerability across all respondents</p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(globalStats?.top_global_risk_skills ?? []).map((f: { skill: string; skill_label: string; contribution: number }, i: number) => (
                        <div key={f.skill} className="flex items-center gap-3">
                          <div className="w-6 text-xs text-muted-foreground text-right">{i + 1}</div>
                          <div className="flex-1 text-sm text-foreground">{f.skill_label}</div>
                          <div className="w-32">
                            <div className="h-2 rounded-full bg-red-100">
                              <div className="h-2 rounded-full bg-red-500" style={{ width: `${(f.contribution / 0.15) * 100}%` }} />
                            </div>
                          </div>
                          <div className="w-12 text-xs text-right text-muted-foreground">{(f.contribution * 100).toFixed(1)}%</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>

                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Top Global Protective Skills</CardTitle>
                    <p className="text-sm text-muted-foreground">Features that reduce automation vulnerability across all respondents</p>
                  </CardHeader>
                  <CardContent>
                    <div className="space-y-3">
                      {(globalStats?.top_global_protective_skills ?? []).map((f: { skill: string; skill_label: string; contribution: number }, i: number) => (
                        <div key={f.skill} className="flex items-center gap-3">
                          <div className="w-6 text-xs text-muted-foreground text-right">{i + 1}</div>
                          <div className="flex-1 text-sm text-foreground">{f.skill_label}</div>
                          <div className="w-32">
                            <div className="h-2 rounded-full bg-green-100">
                              <div className="h-2 rounded-full bg-green-500" style={{ width: `${(f.contribution / 0.15) * 100}%` }} />
                            </div>
                          </div>
                          <div className="w-12 text-xs text-right text-muted-foreground">{(f.contribution * 100).toFixed(1)}%</div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* Per-Program SHAP Tab */}
          <TabsContent value="programs" className="space-y-4">
            {summaryLoading ? (
              <div className="flex justify-center py-16"><Spinner className="w-8 h-8 text-primary" /></div>
            ) : (
              programs.map((prog: { program: string; mean_vulnerability: number; respondent_count: number; top_risk_skills: Array<{ skill: string; skill_label: string; contribution: number }>; top_protective_skills: Array<{ skill: string; skill_label: string; contribution: number }> }) => (
                <Card key={prog.program}>
                  <CardHeader>
                    <div className="flex items-center justify-between">
                      <CardTitle className="text-base">{prog.program}</CardTitle>
                      <div className="flex items-center gap-2">
                        <Badge variant="outline" className="text-xs">{prog.respondent_count} respondents</Badge>
                        <Badge className="text-xs" style={{ backgroundColor: RISK_COLORS[prog.program] ?? "#666", color: "#fff" }}>
                          {(prog.mean_vulnerability * 100).toFixed(1)}%
                        </Badge>
                      </div>
                    </div>
                  </CardHeader>
                  <CardContent>
                    <div className="grid sm:grid-cols-2 gap-6">
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Top Risk Factors</p>
                        <div className="space-y-2">
                          {prog.top_risk_skills.slice(0, 3).map((f: { skill: string; skill_label: string; contribution: number }) => (
                            <div key={f.skill} className="flex items-center gap-2 text-sm">
                              <div className="w-2 h-2 rounded-full bg-red-500 flex-shrink-0" />
                              <span className="text-foreground flex-1">{f.skill_label}</span>
                              <span className="text-xs text-muted-foreground">{(f.contribution * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                      <div>
                        <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">Top Protective Skills</p>
                        <div className="space-y-2">
                          {prog.top_protective_skills.slice(0, 3).map((f: { skill: string; skill_label: string; contribution: number }) => (
                            <div key={f.skill} className="flex items-center gap-2 text-sm">
                              <div className="w-2 h-2 rounded-full bg-green-500 flex-shrink-0" />
                              <span className="text-foreground flex-1">{f.skill_label}</span>
                              <span className="text-xs text-muted-foreground">{(f.contribution * 100).toFixed(1)}%</span>
                            </div>
                          ))}
                        </div>
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )}
          </TabsContent>

          {/* Curriculum Gap Report */}
          <TabsContent value="curriculum" className="space-y-4">
            {summaryLoading ? (
              <div className="flex justify-center py-16"><Spinner className="w-8 h-8 text-primary" /></div>
            ) : (
              <>
                <Card>
                  <CardHeader>
                    <CardTitle className="text-base">Curriculum Gap Report</CardTitle>
                    <p className="text-sm text-muted-foreground">
                      Protective skills identified by SHAP — cross-referenced against CHED CMO standards.
                      <strong> Implementation gaps</strong>: skill is in CMO but underperformed.
                      <strong> Design gaps</strong>: skill is missing from CMO entirely.
                    </p>
                  </CardHeader>
                  <CardContent>
                    <div className="overflow-x-auto">
                      <table className="w-full text-sm">
                        <thead>
                          <tr className="border-b text-left">
                            <th className="pb-2 font-medium text-muted-foreground">Program</th>
                            <th className="pb-2 font-medium text-muted-foreground">Skill</th>
                            <th className="pb-2 font-medium text-muted-foreground">In CHED CMO</th>
                            <th className="pb-2 font-medium text-muted-foreground">Gap Type</th>
                            <th className="pb-2 font-medium text-muted-foreground text-right">Impact</th>
                          </tr>
                        </thead>
                        <tbody>
                          {programs.flatMap((p: { program: string; curriculum_gaps: Array<{ skill_id: string; skill_label: string; in_ched_cmo: boolean; gap_type: string; impact_score: number }> }) =>
                            p.curriculum_gaps.map((gap: { skill_id: string; skill_label: string; in_ched_cmo: boolean; gap_type: string; impact_score: number }) => (
                              <tr key={`${p.program}-${gap.skill_id}`} className="border-b last:border-0">
                                <td className="py-2 pr-4 text-xs text-muted-foreground whitespace-nowrap">{p.program.replace("Bachelor of ", "B. of ").replace("BS ", "")}</td>
                                <td className="py-2 pr-4 font-medium text-foreground">{gap.skill_label}</td>
                                <td className="py-2 pr-4">
                                  <Badge variant={gap.in_ched_cmo ? "secondary" : "outline"} className="text-xs">
                                    {gap.in_ched_cmo ? "Yes" : "No"}
                                  </Badge>
                                </td>
                                <td className="py-2 pr-4">
                                  <Badge variant={gap.gap_type === "design" ? "destructive" : "outline"} className="text-xs capitalize">
                                    {gap.gap_type}
                                  </Badge>
                                </td>
                                <td className="py-2 text-right text-xs text-muted-foreground">{(gap.impact_score * 100).toFixed(1)}%</td>
                              </tr>
                            ))
                          )}
                        </tbody>
                      </table>
                    </div>
                  </CardContent>
                </Card>
              </>
            )}
          </TabsContent>

          {/* SUS Evaluation */}
          <TabsContent value="sus" className="space-y-6">
            {/* Aggregate results */}
            {!susLoading && susData && susData.total_responses > 0 && (
              <Card>
                <CardHeader>
                  <CardTitle className="text-base">Aggregated SUS Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-3 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-primary">{susData.mean_sus_score.toFixed(1)}</div>
                      <div className="text-xs text-muted-foreground mt-1">Mean SUS Score</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-primary">{susData.interpretation}</div>
                      <div className="text-xs text-muted-foreground mt-1">Usability Rating</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-primary">{susData.total_responses}</div>
                      <div className="text-xs text-muted-foreground mt-1">Responses</div>
                    </div>
                  </div>
                  {Object.keys(susData.score_by_program).length > 0 && (
                    <div className="mt-4 pt-4 border-t">
                      <p className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-3">By Program</p>
                      <div className="space-y-2">
                        {Object.entries(susData.score_by_program).map(([prog, score]: [string, number]) => (
                          <div key={prog} className="flex items-center justify-between text-sm">
                            <span className="text-foreground">{prog}</span>
                            <span className="font-medium">{score.toFixed(1)}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </CardContent>
              </Card>
            )}

            {/* SUS Form */}
            <Card>
              <CardHeader>
                <CardTitle className="text-base">System Usability Scale Questionnaire</CardTitle>
                <p className="text-sm text-muted-foreground">Rate each statement from 1 (Strongly Disagree) to 5 (Strongly Agree)</p>
              </CardHeader>
              <CardContent>
                {susSubmitted && susResult ? (
                  <div className="text-center py-8">
                    <div className="text-5xl font-bold text-primary mb-2">{susResult.sus_score.toFixed(1)}</div>
                    <Badge className="text-sm px-4 py-1.5 mb-4">{susResult.interpretation} (Grade {susResult.grade})</Badge>
                    <p className="text-sm text-muted-foreground mb-6">
                      {susResult.sus_score >= 68 ? "ARAL meets acceptable usability standards." : "Further usability improvements are recommended."}
                    </p>
                    <Button onClick={() => { setSusSubmitted(false); setSusResponses(Array(10).fill(3)); }}>
                      Submit Another Response
                    </Button>
                  </div>
                ) : (
                  <div className="space-y-6">
                    {SUS_QUESTIONS.map((q, i) => (
                      <div key={i}>
                        <div className="flex items-start gap-3 mb-3">
                          <span className="text-xs font-bold text-muted-foreground w-5 mt-1">{i + 1}.</span>
                          <p className="text-sm text-foreground">{q}</p>
                        </div>
                        <div className="flex items-center gap-3 pl-8">
                          <span className="text-xs text-muted-foreground w-20">Strongly<br/>Disagree</span>
                          <div className="flex gap-2">
                            {[1, 2, 3, 4, 5].map((v) => (
                              <button
                                key={v}
                                onClick={() => {
                                  const newResponses = [...susResponses];
                                  newResponses[i] = v;
                                  setSusResponses(newResponses);
                                }}
                                className={`w-9 h-9 rounded-full text-sm font-medium border-2 transition-all ${susResponses[i] === v ? "bg-primary border-primary text-primary-foreground" : "border-border hover:border-primary/60 text-foreground"}`}
                              >
                                {v}
                              </button>
                            ))}
                          </div>
                          <span className="text-xs text-muted-foreground w-20">Strongly<br/>Agree</span>
                        </div>
                        {i < SUS_QUESTIONS.length - 1 && <Separator className="mt-4" />}
                      </div>
                    ))}
                    <Button onClick={handleSusSubmit} disabled={susSubmitting} className="w-full mt-4">
                      {susSubmitting ? "Calculating..." : "Submit SUS Questionnaire"}
                    </Button>
                  </div>
                )}
              </CardContent>
            </Card>
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
