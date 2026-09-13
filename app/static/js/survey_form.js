// Alpine.js component for the five-step survey. It tracks which question is
// showing, holds the answers, and decides when the Next button is allowed.

const TOTAL_STEPS = 5;

// An answer must be at least this many characters before moving on.
const MIN_ANSWER_LENGTH = 10;

const ANSWER_KEYS = ["q1", "q2", "q3", "q4", "q5"];

// Example answers a user can drop in with the "Fill sample response" button.
const SAMPLE_ANSWERS = {
  q1: "Yum is a snack food company that manufactures and sells packaged snack products to consumers, with single-use packaging as a core part of every unit sold.",
  q2: "Single-use snack packaging is discarded after every purchase, with virtually no recovery or reuse loop in place at the consumer end.",
  q3: "Expanding plastic packaging regulations, EPR fee structures, and growing consumer preference for low-waste brands are collectively pushing Yum to act on packaging.",
  q4: "Yum has not yet piloted circular models; all consumer packaging currently follows a single-use, linear disposal path.",
  q5: "Regulatory compliance ahead of mandates, reduced per-unit packaging costs through reuse, and brand differentiation as a credible low-waste snack option.",
};

// Alpine calls this with any answers already saved in the session, so a user
// who comes back to the survey sees what they typed before.
function surveyForm(existingAnswers) {
  const answers = {};
  for (const answerKey of ANSWER_KEYS) {
    if (existingAnswers[answerKey]) {
      answers[answerKey] = existingAnswers[answerKey];
    } else {
      answers[answerKey] = "";
    }
  }

  return {
    step: 1,
    total: TOTAL_STEPS,
    answers: answers,
    samples: SAMPLE_ANSWERS,

    fillSample(answerKey) {
      this.answers[answerKey] = this.samples[answerKey];
    },

    currentAnswerKey() {
      return "q" + this.step;
    },

    canProceed() {
      const currentAnswer = this.answers[this.currentAnswerKey()];
      return currentAnswer.trim().length >= MIN_ANSWER_LENGTH;
    },

    next() {
      if (this.step < this.total && this.canProceed()) {
        this.step += 1;
      }
    },

    previous() {
      if (this.step > 1) {
        this.step -= 1;
      }
    },
  };
}
