// Alpine.js component for the review page. It lets the user edit answers,
// choose how many concepts to generate, and shows per-concept progress while
// the server streams the model's reply.

// Text for the confidence badge tooltip on research-filled answers.
const CONFIDENCE_TOOLTIPS = {
  high: "Direct evidence from company sources: annual reports, press releases, or sustainability filings.",
  medium: "Inferred from trade press, industry news, or indirect sources. Worth verifying.",
  low: "Limited direct evidence found. Based on general industry patterns. Review and edit this answer.",
};

const QUESTIONS = {
  q1: { label: "Organization", title: "What does the organization make or do?" },
  q2: { label: "Waste & Inefficiency", title: "Where does waste, inefficiency, or end-of-life live in their value chain?" },
  q3: { label: "Pressure to Change", title: "What pressure is driving the need to change?" },
  q4: { label: "Exclusion Filter", title: "What circular territory have they already explored?" },
  q5: { label: "Success Criteria", title: "What does a successful outcome look like for them?" },
};

// Progress states for each concept while generation runs.
const PROGRESS_WAITING = "waiting";
const PROGRESS_GENERATING = "generating";
const PROGRESS_COMPLETE = "complete";

// conceptLimits comes from the server: { min, max, default }.
function reviewPage(initialAnswers, initialConfidences, orgName, conceptLimits) {
  return {
    // Copies, so edits on the page do not change the original objects.
    answers: Object.assign({}, initialAnswers),
    confidences: Object.assign({}, initialConfidences),
    orgName: orgName,
    editing: { q1: false, q2: false, q3: false, q4: false, q5: false },
    n_concepts: conceptLimits.default,
    minConcepts: conceptLimits.min,
    maxConcepts: conceptLimits.max,
    loading: false,
    conceptProgress: [],
    errorMessage: null,
    questions: QUESTIONS,

    init() {
      // Research-filled answers that are empty or low confidence open in edit
      // mode right away so the user notices them.
      if (this.orgName) {
        for (const answerKey of Object.keys(this.questions)) {
          const answerIsEmpty = !this.answers[answerKey];
          const confidenceIsLow = this.confidences[answerKey] === "low";
          if (answerIsEmpty || confidenceIsLow) {
            this.editing[answerKey] = true;
          }
        }
      }
    },

    isAnyEditing() {
      for (const answerKey of Object.keys(this.editing)) {
        if (this.editing[answerKey]) {
          return true;
        }
      }
      return false;
    },

    toggleEditing(answerKey) {
      this.editing[answerKey] = !this.editing[answerKey];
    },

    displayAnswer(answerKey) {
      if (this.answers[answerKey]) {
        return this.answers[answerKey];
      }
      return "No answer yet";
    },

    confidenceTooltip(level) {
      if (CONFIDENCE_TOOLTIPS[level]) {
        return CONFIDENCE_TOOLTIPS[level];
      }
      return "";
    },

    decreaseConceptCount() {
      if (this.n_concepts > this.minConcepts) {
        this.n_concepts -= 1;
      }
    },

    increaseConceptCount() {
      if (this.n_concepts < this.maxConcepts) {
        this.n_concepts += 1;
      }
    },

    // One row per concept for the progress list in the loading overlay.
    progressItems() {
      const items = [];
      for (let index = 0; index < this.n_concepts; index += 1) {
        let state = this.conceptProgress[index];
        if (!state) {
          state = PROGRESS_WAITING;
        }
        items.push({ number: index + 1, state: state });
      }
      return items;
    },

    progressLabel(state) {
      if (state === PROGRESS_GENERATING) {
        return "Generating...";
      }
      if (state === PROGRESS_COMPLETE) {
        return "Done";
      }
      return "Waiting";
    },

    handleGenerationEvent(serverEvent) {
      // Concept numbers start at 1; array positions start at 0.
      const index = serverEvent.number - 1;
      if (serverEvent.type === "concept_start") {
        this.conceptProgress[index] = PROGRESS_GENERATING;
      } else if (serverEvent.type === "concept_end") {
        this.conceptProgress[index] = PROGRESS_COMPLETE;
      } else if (serverEvent.type === "done") {
        window.location.href = "/concepts";
      } else if (serverEvent.type === "error") {
        if (serverEvent.message) {
          this.errorMessage = serverEvent.message;
        } else {
          this.errorMessage = "Something went wrong.";
        }
        this.loading = false;
      }
    },

    // "async" lets us use "await" inside, so the code reads top to bottom
    // even though the network request takes minutes.
    async handleSubmit(event) {
      const component = this;
      this.loading = true;
      this.errorMessage = null;

      this.conceptProgress = [];
      for (let index = 0; index < this.n_concepts; index += 1) {
        this.conceptProgress.push(PROGRESS_WAITING);
      }

      const formData = new FormData(event.target);

      try {
        const response = await fetch("/generate-stream", { method: "POST", body: formData });
        await readServerSentEvents(response, function (serverEvent) {
          component.handleGenerationEvent(serverEvent);
        });
      } catch (error) {
        this.errorMessage = "Connection failed. Please try again.";
        this.loading = false;
      }
    },
  };
}
