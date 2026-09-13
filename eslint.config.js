// ESLint flat config. Starts from the recommended rule set and only adds what
// this project needs: browser globals, plus the component functions that the
// templates call by name and the readServerSentEvents helper shared across files.

import eslintRecommended from "@eslint/js";
import globals from "globals";

export default [
  eslintRecommended.configs.recommended,
  {
    files: ["app/static/js/**/*.js"],
    languageOptions: {
      // The static files are classic browser scripts, not modules.
      sourceType: "script",
      globals: Object.assign({}, globals.browser, {
        // Defined in sse_reader.js and used by other files.
        readServerSentEvents: "readonly",
      }),
    },
    rules: {
      // The Alpine component functions are called from the HTML templates,
      // so ESLint cannot see that they are used.
      "no-unused-vars": ["error", { varsIgnorePattern: "^(researchCard|surveyForm|reviewPage|conceptsPage|readServerSentEvents)$" }],
    },
  },
];
