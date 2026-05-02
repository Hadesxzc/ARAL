import { useState, useEffect } from "react";
import { useLocation } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Progress } from "@/components/ui/progress";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import { Spinner } from "@/components/ui/spinner";
import {
  useGetPrograms,
  useGetSkillsByProgram,
  useSubmitAssessment,
  getGetProgramsQueryKey,
  getGetSkillsByProgramQueryKey,
} from "@workspace/api-client-react";
import { Link } from "wouter";

const TASK_CATEGORIES = [
  { id: "task_data_entry", label: "Data Entry / Record Keeping" },
  { id: "task_data_analysis", label: "Analyzing Data / Information" },
  { id: "task_decision_making", label: "Decision Making / Problem Solving" },
  { id: "task_computer_use", label: "Using Computers / Software" },
  { id: "task_client_comms", label: "Communicating with Clients" },
  { id: "task_internal_comms", label: "Communicating with Coworkers" },
  { id: "task_teaching", label: "Teaching / Training / Coaching" },
  { id: "task_managing", label: "Managing / Supervising People" },
  { id: "task_documents", label: "Creating Documents / Reports" },
  { id: "task_physical", label: "Physical / Manual Tasks" },
  { id: "task_creative", label: "Creative / Design Work" },
  { id: "task_caregiving", label: "Caring for / Assisting Others" },
  { id: "task_other", label: "Other Tasks" },
];

const STEPS = ["Degree Program", "Job Title", "Skills Checklist", "Task Distribution"];

type AssessmentResult = {
  vulnerability_score: number;
  risk_level: string;
  risk_label: string;
  risk_color: string;
  program_average: number;
  percentile: number;
  shap_explanation: {
    top_risk_factors: Array<{ skill: string; skill_label: string; contribution: number; direction: string }>;
    top_protective_factors: Array<{ skill: string; skill_label: string; contribution: number; direction: string }>;
  };
  skill_gaps: Array<{ skill_id: string; skill_label: string; in_ched_cmo: boolean; gap_type: string; impact_score: number }>;
  recommendations: Array<{ skill: string; course_title: string; platform: string; url: string; is_free: boolean; reason?: string }>;
  program_comparison: Record<string, number>;
};

export default function Assessment() {
  const [, setLocation] = useLocation();
  const [step, setStep] = useState(0);
  const [selectedProgram, setSelectedProgram] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [skills, setSkills] = useState<Record<string, number>>({});
  const [taskValues, setTaskValues] = useState<Record<string, number>>(() =>
    Object.fromEntries(TASK_CATEGORIES.map((t) => [t.id, 0]))
  );
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [loadingMsg, setLoadingMsg] = useState("Analyzing your automation vulnerability...");

  const { data: programsData } = useGetPrograms({ query: { queryKey: getGetProgramsQueryKey() } });
  const { data: skillsData, isLoading: skillsLoading } = useGetSkillsByProgram(
    encodeURIComponent(selectedProgram),
    { query: { enabled: !!selectedProgram, queryKey: getGetSkillsByProgramQueryKey(selectedProgram) } }
  );
  const { mutate: submitAssessment } = useSubmitAssessment();

  const programs = programsData?.programs ?? [];
  const skillsList = skillsData?.skills ?? [];

  // Loading messages sequence
  useEffect(() => {
    if (!isSubmitting) return;
    const messages = [
      "Analyzing your automation vulnerability...",
      "Running SHAP analysis...",
      "Identifying skill gaps...",
      "Generating course recommendations...",
      "Preparing your results...",
    ];
    let i = 0;
    const interval = setInterval(() => {
      i = (i + 1) % messages.length;
      setLoadingMsg(messages[i]);
    }, 1800);
    return () => clearInterval(interval);
  }, [isSubmitting]);

  const taskTotal = Object.values(taskValues).reduce((a, b) => a + b, 0);

  const normalizeTaskDistribution = () => {
    const total = taskTotal || 100;
    return Object.fromEntries(
      Object.entries(taskValues).map(([k, v]) => [k, v / total])
    );
  };

  const handleSubmit = () => {
    setIsSubmitting(true);
    const taskDist = normalizeTaskDistribution();
    submitAssessment(
      {
        data: {
          degree_program: selectedProgram,
          job_title: jobTitle,
          skills,
          task_distribution: taskDist,
        },
      },
      {
        onSuccess: (result: AssessmentResult) => {
          localStorage.setItem("aral_last_result", JSON.stringify({ ...result, degree_program: selectedProgram, job_title: jobTitle }));
          setLocation("/results");
        },
        onError: () => {
          setIsSubmitting(false);
        },
      }
    );
  };

  const canProceedStep0 = !!selectedProgram;
  const canProceedStep1 = jobTitle.trim().length >= 2;
  const canProceedStep2 = skillsList.length === 0 || Object.keys(skills).length > 0;
  const canProceedStep3 = taskTotal > 0;

  if (isSubmitting) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-6">
        <div className="text-center max-w-sm">
          <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
            <Spinner className="w-8 h-8 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-2">Processing Your Assessment</h2>
          <p className="text-muted-foreground text-sm transition-all duration-500">{loadingMsg}</p>
          <Progress value={66} className="mt-6" />
        </div>
      </div>
    );
  }

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
          <div className="text-sm text-muted-foreground">Step {step + 1} of {STEPS.length}</div>
        </div>
      </header>

      <div className="max-w-2xl mx-auto px-6 py-10">
        {/* Progress */}
        <div className="mb-8">
          <div className="flex items-center justify-between mb-2">
            {STEPS.map((s, i) => (
              <div key={s} className="flex items-center gap-2">
                <div className={`w-7 h-7 rounded-full flex items-center justify-center text-xs font-bold transition-colors ${i < step ? "bg-primary text-primary-foreground" : i === step ? "bg-primary text-primary-foreground ring-2 ring-primary/30" : "bg-muted text-muted-foreground"}`}>
                  {i < step ? "✓" : i + 1}
                </div>
                {i < STEPS.length - 1 && (
                  <div className={`flex-1 h-0.5 w-12 sm:w-20 ${i < step ? "bg-primary" : "bg-muted"}`} />
                )}
              </div>
            ))}
          </div>
          <p className="text-sm text-muted-foreground mt-2">{STEPS[step]}</p>
        </div>

        {/* Step 0: Program */}
        {step === 0 && (
          <Card>
            <CardHeader>
              <CardTitle>Select Your Degree Program</CardTitle>
              <CardDescription>Choose the program you graduated from or are currently enrolled in.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-3">
              {programs.length === 0 ? (
                <div className="flex items-center justify-center py-8">
                  <Spinner className="w-6 h-6 text-primary" />
                </div>
              ) : (
                programs.map((p: string) => (
                  <button
                    key={p}
                    onClick={() => setSelectedProgram(p)}
                    className={`w-full text-left px-4 py-3 rounded-lg border-2 transition-all text-sm font-medium ${selectedProgram === p ? "border-primary bg-primary/5 text-primary" : "border-border hover:border-primary/40 hover:bg-muted/50"}`}
                  >
                    {p}
                  </button>
                ))
              )}
              <div className="pt-4">
                <Button onClick={() => setStep(1)} disabled={!canProceedStep0} className="w-full">
                  Continue
                </Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 1: Job Title */}
        {step === 1 && (
          <Card>
            <CardHeader>
              <CardTitle>What is Your Job Title?</CardTitle>
              <CardDescription>Enter your current or most recent job title. This helps map your role to Philippine Standard Occupational Classification codes.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <Label htmlFor="job-title" className="text-sm font-medium">Job Title</Label>
                <Input
                  id="job-title"
                  value={jobTitle}
                  onChange={(e) => setJobTitle(e.target.value)}
                  placeholder="e.g. Junior Auditor, Software Engineer, Registered Nurse"
                  className="mt-2"
                  autoFocus
                  onKeyDown={(e) => e.key === "Enter" && canProceedStep1 && setStep(2)}
                />
                <p className="text-xs text-muted-foreground mt-2">
                  If you are a fresh graduate or student, enter your target job title or "Fresh Graduate."
                </p>
              </div>
              <div className="flex gap-3 pt-2">
                <Button variant="outline" onClick={() => setStep(0)} className="flex-1">Back</Button>
                <Button onClick={() => setStep(2)} disabled={!canProceedStep1} className="flex-1">Continue</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 2: Skills */}
        {step === 2 && (
          <Card>
            <CardHeader>
              <CardTitle>Skills Assessment</CardTitle>
              <CardDescription>
                Based on your CHED CMO curriculum for <strong>{selectedProgram}</strong>. 
                Toggle on the skills you currently have.
              </CardDescription>
            </CardHeader>
            <CardContent>
              {skillsLoading ? (
                <div className="flex items-center justify-center py-10">
                  <Spinner className="w-6 h-6 text-primary" />
                </div>
              ) : (
                <div className="space-y-1">
                  {skillsList.map((skill: { id: string; label: string; source: string; description?: string }) => {
                    const hasSkill = !!skills[skill.id];
                    return (
                      <div
                        key={skill.id}
                        className={`flex items-center justify-between px-4 py-3 rounded-lg border transition-colors cursor-pointer ${hasSkill ? "border-primary/40 bg-primary/5" : "border-border hover:bg-muted/30"}`}
                        onClick={() => setSkills((prev) => ({ ...prev, [skill.id]: hasSkill ? 0 : 1 }))}
                      >
                        <div className="flex-1 mr-4">
                          <p className="text-sm font-medium text-foreground">{skill.label}</p>
                          {skill.description && (
                            <p className="text-xs text-muted-foreground mt-0.5">{skill.description}</p>
                          )}
                        </div>
                        <Switch
                          checked={hasSkill}
                          onCheckedChange={(checked) => setSkills((prev) => ({ ...prev, [skill.id]: checked ? 1 : 0 }))}
                          onClick={(e) => e.stopPropagation()}
                        />
                      </div>
                    );
                  })}
                  <p className="text-xs text-muted-foreground pt-2">
                    Source: {skillsData?.cmo_reference}
                  </p>
                </div>
              )}
              <div className="flex gap-3 pt-6">
                <Button variant="outline" onClick={() => setStep(1)} className="flex-1">Back</Button>
                <Button onClick={() => setStep(3)} className="flex-1">Continue</Button>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Step 3: Task Distribution */}
        {step === 3 && (
          <Card>
            <CardHeader>
              <CardTitle>How Do You Spend Your Workday?</CardTitle>
              <CardDescription>
                Adjust the sliders to reflect what percentage of your time you spend on each type of task.
                The total should ideally sum to 100%.
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="mb-4 p-3 rounded-lg bg-muted/50 flex items-center justify-between">
                <span className="text-sm text-muted-foreground">Total allocated</span>
                <span className={`text-sm font-bold ${Math.abs(taskTotal - 100) < 5 ? "text-green-600" : taskTotal > 100 ? "text-destructive" : "text-muted-foreground"}`}>
                  {taskTotal}%
                </span>
              </div>
              <div className="space-y-5">
                {TASK_CATEGORIES.map((task) => (
                  <div key={task.id}>
                    <div className="flex items-center justify-between mb-2">
                      <Label className="text-sm">{task.label}</Label>
                      <span className="text-sm font-medium text-primary w-10 text-right">{taskValues[task.id]}%</span>
                    </div>
                    <Slider
                      value={[taskValues[task.id]]}
                      onValueChange={([val]) => setTaskValues((prev) => ({ ...prev, [task.id]: val }))}
                      min={0}
                      max={60}
                      step={1}
                      className="w-full"
                    />
                  </div>
                ))}
              </div>
              <div className="flex gap-3 pt-8">
                <Button variant="outline" onClick={() => setStep(2)} className="flex-1">Back</Button>
                <Button onClick={handleSubmit} disabled={!canProceedStep3} className="flex-1">
                  Analyze My Risk
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>
    </div>
  );
}
