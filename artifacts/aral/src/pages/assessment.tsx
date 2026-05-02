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
  useSubmitAssessment,
  getGetProgramsQueryKey,
  getGetJobsByProgramQueryKey,
} from "@workspace/api-client-react";

const PROGRAMS_FALLBACK = [
  "BS Accountancy",
  "BS Business Administration",
  "BS Information Technology",
  "BS Computer Science",
  "Bachelor of Elementary Education",
  "BS Nursing",
];

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

  const { mutate: submitAssessment } = useSubmitAssessment();

  const programs: string[] = programsData?.programs ?? PROGRAMS_FALLBACK;
  const jobOptions: string[] = jobsData?.jobs ?? [];

  const handleProgramSelect = (program: string) => {
    setSelectedProgram(program);
    setJobTitle("");
    setOpen(false);
    setError("");
  };

  const handleSubmit = () => {
    if (!selectedProgram || !jobTitle) return;
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
          skills: {},
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

      <div className="max-w-xl mx-auto px-6 py-16">
        {/* Header */}
        <div className="text-center mb-10">
          <Badge className="mb-4 text-xs tracking-wider uppercase">Automation Risk Assessment</Badge>
          <h1 className="text-3xl font-bold text-foreground mb-3">Predict Your Career Risk</h1>
          <p className="text-muted-foreground leading-relaxed">
            Select your degree program and current or target job title. ARAL will predict your automation
            vulnerability using a Random Forest model trained on Filipino graduate respondents.
          </p>
        </div>

        <Card className="shadow-sm">
          <CardHeader>
            <CardTitle className="text-lg">Your Academic Profile</CardTitle>
            <CardDescription>
              Skills and task data are derived from your program's CHED CMO curriculum standards and
              typical occupational profiles — no additional input required.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">

            {/* Error banner */}
            {error && (
              <div className="p-3 rounded-lg border border-destructive/40 bg-destructive/5 text-destructive text-sm">
                {error}
              </div>
            )}

            {/* Step 1 — Program */}
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
                    <svg
                      className={`w-4 h-4 text-muted-foreground transition-transform ${open ? "rotate-180" : ""}`}
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
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
                            <div
                              className={`mr-3 w-4 h-4 rounded-full border-2 flex items-center justify-center flex-shrink-0 ${
                                selectedProgram === program
                                  ? "border-primary bg-primary"
                                  : "border-muted-foreground/40"
                              }`}
                            >
                              {selectedProgram === program && (
                                <div className="w-2 h-2 rounded-full bg-white" />
                              )}
                            </div>
                            {program}
                          </CommandItem>
                        ))}
                      </CommandGroup>
                    </CommandList>
                  </Command>
                </PopoverContent>
              </Popover>
              {selectedProgram && (
                <p className="text-xs text-muted-foreground">
                  Skills profile sourced from CHED CMO for {selectedProgram}.
                </p>
              )}
            </div>

            {/* Step 2 — Job Title Dropdown */}
            <div className="space-y-2">
              <div className="flex items-center gap-2 mb-1">
                <span className={`w-5 h-5 rounded-full text-xs flex items-center justify-center font-bold flex-shrink-0 ${selectedProgram ? "bg-primary text-primary-foreground" : "bg-muted text-muted-foreground"}`}>2</span>
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
                  <SelectTrigger
                    className={`h-11 text-sm border-2 transition-all ${
                      jobTitle
                        ? "border-primary/40 bg-primary/5"
                        : "border-border hover:border-primary/30"
                    }`}
                  >
                    <SelectValue placeholder="Select a job title..." />
                  </SelectTrigger>
                  <SelectContent>
                    {jobOptions.length === 0 ? (
                      <div className="py-3 px-4 text-sm text-muted-foreground">No job titles found.</div>
                    ) : (
                      jobOptions.map((job) => (
                        <SelectItem key={job} value={job} className="py-2.5 cursor-pointer">
                          {job}
                        </SelectItem>
                      ))
                    )}
                  </SelectContent>
                </Select>
              )}

              {jobTitle && (
                <p className="text-xs text-muted-foreground">
                  Task distribution for <span className="font-medium text-foreground">{jobTitle}</span> will be used in the assessment.
                </p>
              )}
            </div>

            <div className="pt-2">
              <Button
                onClick={handleSubmit}
                disabled={!selectedProgram || !jobTitle}
                className="w-full h-12 text-base font-semibold"
                size="lg"
              >
                Analyze My Automation Risk
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
