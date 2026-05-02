import { useState } from "react";
import { Link } from "wouter";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Progress } from "@/components/ui/progress";
import { Spinner } from "@/components/ui/spinner";
import { Badge } from "@/components/ui/badge";
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
  CommandList,
} from "@/components/ui/command";
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  useGetPrograms,
  useGetJobsByProgram,
  useGetSkillsByProgram,
  useSubmitAssessment,
  getGetProgramsQueryKey,
  getGetJobsByProgramQueryKey,
  getGetSkillsByProgramQueryKey,
} from "@workspace/api-client-react";

const PROGRAMS_FALLBACK = [
  "BS Accountancy",
  "BS Business Administration",
  "BS Information Technology",
  "BS Computer Science",
  "Bachelor of Elementary Education",
  "BS Nursing",
];

const PROFICIENCY_LABELS: Record<number, { label: string; color: string }> = {
  1: { label: "None",         color: "bg-red-100 text-red-700 border-red-300 hover:bg-red-200" },
  2: { label: "Beginner",     color: "bg-orange-100 text-orange-700 border-orange-300 hover:bg-orange-200" },
  3: { label: "Intermediate", color: "bg-yellow-100 text-yellow-700 border-yellow-300 hover:bg-yellow-200" },
  4: { label: "Proficient",   color: "bg-blue-100 text-blue-700 border-blue-300 hover:bg-blue-200" },
  5: { label: "Expert",       color: "bg-green-100 text-green-700 border-green-300 hover:bg-green-200" },
};

const LOADING_MESSAGES = [
  "Analyzing your automation vulnerability...",
  "Running SHAP analysis on your program profile...",
  "Identifying skill gaps from CHED CMO standards...",
  "Generating personalized course recommendations...",
  "Preparing your results dashboard...",
];

export default function Assessment() {
  const [open, setOpen] = useState(false);
  const [selectedProgram, setSelectedProgram] = useState("");
  const [jobTitle, setJobTitle] = useState("");
  const [skillRatings, setSkillRatings] = useState<Record<string, number>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState("");
  const [loadingIdx, setLoadingIdx] = useState(0);

  const { data: programsData } = useGetPrograms({
    query: { queryKey: getGetProgramsQueryKey() },
  });

  const { data: jobsData, isLoading: jobsLoading } = useGetJobsByProgram(
    selectedProgram,
    {
      query: {
        queryKey: getGetJobsByProgramQueryKey(selectedProgram),
        enabled: !!selectedProgram,
      },
    }
  );

  const { data: skillsData, isLoading: skillsLoading } = useGetSkillsByProgram(
    selectedProgram,
    {
      query: {
        queryKey: getGetSkillsByProgramQueryKey(selectedProgram),
        enabled: !!selectedProgram,
      },
    }
  );

  const { mutate: submitAssessment } = useSubmitAssessment();

  const programs: string[] = programsData?.programs ?? PROGRAMS_FALLBACK;
  const jobOptions: string[] = jobsData?.jobs ?? [];
  const skills = skillsData?.skills ?? [];

  const allSkillsRated = skills.length > 0 && skills.every((s) => skillRatings[s.id] !== undefined);
  const canSubmit = !!selectedProgram && !!jobTitle && allSkillsRated;

  const ratedCount = skills.filter((s) => skillRatings[s.id] !== undefined).length;

  const handleProgramSelect = (program: string) => {
    setSelectedProgram(program);
    setJobTitle("");
    setSkillRatings({});
    setOpen(false);
    setError("");
  };

  const handleSkillRate = (skillId: string, rating: number) => {
    setSkillRatings((prev) => ({ ...prev, [skillId]: rating }));
    setError("");
  };

  const handleSubmit = () => {
    if (!canSubmit) return;
    setIsSubmitting(true);
    setError("");

    const interval = setInterval(() => {
      setLoadingIdx((i) => (i + 1) % LOADING_MESSAGES.length);
    }, 1800);

    submitAssessment(
      {
        data: {
          degree_program: selectedProgram,
          job_title: jobTitle,
          skills: skillRatings,
        },
      },
      {
        onSuccess: (result) => {
          clearInterval(interval);
          localStorage.setItem(
            "aral_last_result",
            JSON.stringify({ ...result, degree_program: selectedProgram, job_title: jobTitle })
          );
          window.location.href = "/results";
        },
        onError: (err) => {
          clearInterval(interval);
          setIsSubmitting(false);
          setError(
            err instanceof Error
              ? `Assessment failed: ${err.message}`
              : "Something went wrong. Please try again."
          );
        },
      }
    );
  };

  if (isSubmitting) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center px-6">
        <div className="text-center max-w-sm">
          <div className="w-20 h-20 rounded-full bg-primary/10 flex items-center justify-center mx-auto mb-6">
            <Spinner className="w-10 h-10 text-primary" />
          </div>
          <h2 className="text-xl font-semibold text-foreground mb-3">Analyzing Your Profile</h2>
          <p className="text-muted-foreground text-sm min-h-[20px] transition-all duration-500">
            {LOADING_MESSAGES[loadingIdx]}
          </p>
          <Progress className="mt-6 h-1.5" value={66} />
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
          <Link href="/about" className="text-sm text-muted-foreground hover:text-foreground transition-colors">
            Methodology
          </Link>
        </div>
      </header>

      <div className="max-w-xl mx-auto px-6 py-12">
        {/* Header */}
        <div className="text-center mb-8">
          <Badge className="mb-4 text-xs tracking-wider uppercase">Automation Risk Assessment</Badge>
          <h1 className="text-3xl font-bold text-foreground mb-3">Predict Your Career Risk</h1>
          <p className="text-muted-foreground leading-relaxed text-sm">
            Select your degree program, job title, and rate your proficiency in each CHED CMO skill.
            ARAL uses a Random Forest model trained on Filipino graduate respondents.
          </p>
        </div>

        {/* Progress indicator */}
        {selectedProgram && (
          <div className="flex items-center gap-2 mb-6">
            {[
              { n: 1, done: !!selectedProgram, label: "Program" },
              { n: 2, done: !!jobTitle, label: "Job Title" },
              { n: 3, done: allSkillsRated, label: `Skills (${ratedCount}/${skills.length})` },
            ].map((step, i) => (
              <div key={step.n} className="flex items-center gap-2 flex-1">
                <div className={`w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0 transition-colors ${step.done ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>
                  {step.done ? "✓" : step.n}
                </div>
                <span className={`text-xs truncate ${step.done ? "text-foreground font-medium" : "text-muted-foreground"}`}>{step.label}</span>
                {i < 2 && <div className={`h-0.5 flex-1 rounded transition-colors ${step.done ? "bg-primary" : "bg-border"}`} />}
              </div>
            ))}
          </div>
        )}

        <Card className="shadow-sm">
          <CardHeader className="pb-4">
            <CardTitle className="text-lg">Your Academic Profile</CardTitle>
            <CardDescription>
              Rate your skill proficiency based on your CHED CMO curriculum — this personalizes your vulnerability score.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">

            {/* Error banner */}
            {error && (
              <div className="p-3 rounded-lg border border-destructive/40 bg-destructive/5 text-destructive text-sm">
                {error}
              </div>
            )}

            {/* ── Step 1: Degree Program ── */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <span className="w-5 h-5 rounded-full bg-primary text-primary-foreground text-xs flex items-center justify-center font-bold flex-shrink-0">1</span>
                <Label className="text-sm font-medium">
                  Degree Program <span className="text-destructive">*</span>
                </Label>
              </div>
              <Popover open={open} onOpenChange={setOpen}>
                <PopoverTrigger asChild>
                  <button
                    role="combobox"
                    aria-expanded={open}
                    className={`w-full flex items-center justify-between px-4 py-3 rounded-lg border-2 text-sm transition-all text-left ${
                      selectedProgram
                        ? "border-primary/40 bg-primary/5 text-foreground"
                        : "border-border text-muted-foreground hover:border-primary/30"
                    }`}
                  >
                    <span>{selectedProgram || "Search or select your degree program..."}</span>
                    <svg className={`w-4 h-4 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                    </svg>
                  </button>
                </PopoverTrigger>
                <PopoverContent className="w-full p-0" align="start" style={{ width: "var(--radix-popover-trigger-width)" }}>
                  <Command>
                    <CommandInput placeholder="Search degree program..." className="h-10" />
                    <CommandList>
                      <CommandEmpty>No program found.</CommandEmpty>
                      <CommandGroup heading="Available Programs">
                        {programs.map((program) => (
                          <CommandItem
                            key={program}
                            value={program}
                            onSelect={() => handleProgramSelect(program)}
                            className="py-3 cursor-pointer"
                          >
                            <div className={`mr-3 w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${selectedProgram === program ? "border-primary bg-primary" : "border-muted-foreground/40"}`}>
                              {selectedProgram === program && <div className="w-2 h-2 rounded-full bg-white" />}
                            </div>
                            {program}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
            </div>

            {/* ── Step 2: Job Title ── */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <span className={`w-5 h-5 rounded-full text-xs flex items-center justify-center font-bold flex-shrink-0 transition-colors ${selectedProgram ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>2</span>
                <Label className={`text-sm font-medium ${!selectedProgram ? "text-muted-foreground" : ""}`}>
                  Current or Target Job Title <span className="text-destructive">*</span>
                </Label>
              </div>

              {!selectedProgram ? (
                <div className="h-11 w-full rounded-lg border-2 border-dashed border-border bg-muted/30 flex items-center px-4">
                  <span className="text-sm text-muted-foreground">Select a degree program first</span>
                </div>
              ) : jobsLoading ? (
                <div className="h-11 w-full rounded-lg border-2 border-border bg-muted/30 flex items-center px-4 gap-3">
                  <Spinner className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Loading job titles...</span>
                </div>
              ) : (
                <Select value={jobTitle} onValueChange={(v) => { setJobTitle(v); setError(""); }}>
                  <SelectTrigger className={`h-11 text-sm border-2 transition-all ${jobTitle ? "border-primary/40 bg-primary/5" : "border-border hover:border-primary/30"}`}>
                    <SelectValue placeholder="Select a job title..." />
                  </SelectTrigger>
                  <SelectContent>
                    {jobOptions.map((job) => (
                      <SelectItem key={job} value={job} className="py-2.5 cursor-pointer">
                        {job}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              )}
            </div>

            {/* ── Step 3: Skills Proficiency ── */}
            <div className="space-y-3">
              <div className="flex items-center gap-2 mb-1">
                <span className={`w-5 h-5 rounded-full text-xs flex items-center justify-center font-bold flex-shrink-0 transition-colors ${jobTitle ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>3</span>
                <Label className={`text-sm font-medium ${!jobTitle ? "text-muted-foreground" : ""}`}>
                  Skill Proficiency — CHED CMO Standards <span className="text-destructive">*</span>
                </Label>
                {jobTitle && skills.length > 0 && (
                  <span className="ml-auto text-xs text-muted-foreground">{ratedCount}/{skills.length} rated</span>
                )}
              </div>

              {!jobTitle ? (
                <div className="p-4 rounded-lg border-2 border-dashed border-border bg-muted/30 text-center">
                  <span className="text-sm text-muted-foreground">Select your job title to unlock skill rating</span>
                </div>
              ) : skillsLoading ? (
                <div className="p-4 rounded-lg border border-border bg-muted/30 flex items-center gap-3">
                  <Spinner className="w-4 h-4 text-muted-foreground" />
                  <span className="text-sm text-muted-foreground">Loading CHED CMO skills...</span>
                </div>
              ) : (
                <>
                  {/* Proficiency legend */}
                  <div className="flex flex-wrap gap-1.5 mb-3 p-3 bg-muted/30 rounded-lg">
                    {[1,2,3,4,5].map((n) => (
                      <div key={n} className={`text-xs px-2 py-0.5 rounded border ${PROFICIENCY_LABELS[n].color}`}>
                        {n} — {PROFICIENCY_LABELS[n].label}
                      </div>
                    ))}
                  </div>

                  {/* Skill rows */}
                  <div className="space-y-3">
                    {skills.map((skill) => {
                      const rated = skillRatings[skill.id];
                      return (
                        <div
                          key={skill.id}
                          className={`p-3 rounded-lg border transition-colors ${rated !== undefined ? "border-primary/30 bg-primary/[0.02]" : "border-border"}`}
                        >
                          <div className="flex items-start justify-between gap-3 mb-2">
                            <div className="flex-1 min-w-0">
                              <p className="text-sm font-medium text-foreground leading-snug">{skill.label}</p>
                              {skill.description && (
                                <p className="text-xs text-muted-foreground mt-0.5 leading-relaxed">{skill.description}</p>
                              )}
                            </div>
                            {rated !== undefined && (
                              <span className={`text-xs px-2 py-0.5 rounded border whitespace-nowrap flex-shrink-0 ${PROFICIENCY_LABELS[rated].color}`}>
                                {rated} — {PROFICIENCY_LABELS[rated].label}
                              </span>
                            )}
                          </div>
                          <div className="flex gap-1.5">
                            {[1,2,3,4,5].map((n) => (
                              <button
                                key={n}
                                onClick={() => handleSkillRate(skill.id, n)}
                                className={`flex-1 h-9 text-sm font-semibold rounded-md border-2 transition-all ${
                                  rated === n
                                    ? `${PROFICIENCY_LABELS[n].color} border-current scale-95 shadow-sm`
                                    : "border-border text-muted-foreground hover:border-primary/40 hover:text-foreground"
                                }`}
                              >
                                {n}
                              </button>
                            ))}
                          </div>
                        </div>
                      );
                    })}
                  </div>
                </>
              )}
            </div>

            {/* Submit */}
            <div className="pt-2">
              <Button
                onClick={handleSubmit}
                disabled={!canSubmit}
                className="w-full h-12 text-base font-semibold"
                size="lg"
              >
                {!selectedProgram
                  ? "Select a Degree Program to Start"
                  : !jobTitle
                  ? "Select a Job Title to Continue"
                  : !allSkillsRated
                  ? `Rate All Skills to Continue (${ratedCount}/${skills.length})`
                  : "Analyze My Automation Risk →"}
              </Button>
            </div>

            <div className="pt-2 border-t">
              <div className="grid grid-cols-3 gap-4 text-center">
                {[
                  { value: "~30s", label: "Takes only" },
                  { value: "Free", label: "100%" },
                  { value: "Private", label: "Completely" },
                ].map((item) => (
                  <div key={item.label}>
                    <div className="font-semibold text-sm text-primary">{item.value}</div>
                    <div className="text-xs text-muted-foreground">{item.label}</div>
                  </div>
                ))}
              </div>
            </div>
          </CardContent>
        </Card>

        {/* What we analyze */}
        <div className="mt-8 grid grid-cols-2 gap-4">
          {[
            { title: "CHED CMO Curriculum", desc: "Your program's official skill competencies" },
            { title: "Occupational Profile", desc: "Task distribution from PSOC 2022 mapping" },
            { title: "POARD Dataset", desc: "1,000+ Filipino graduate respondents" },
            { title: "SHAP Explanation", desc: "Why you got your score — not a black box" },
          ].map((item) => (
            <div key={item.title} className="p-4 rounded-lg border bg-white">
              <p className="text-sm font-medium text-foreground">{item.title}</p>
              <p className="text-xs text-muted-foreground mt-1">{item.desc}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
