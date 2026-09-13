// Alpine.js component for the "Look up your org" card on the home page.
// It posts the form to the research stream, shows a cycling status message
// while the agent works, and sends the browser to the review page when done.

// How long each status message stays on screen before the next one.
const MESSAGE_CYCLE_INTERVAL_MS = 2000;

// Status messages shown while research runs. The icon is an SVG path string.
const RESEARCH_CYCLE_MESSAGES = [
  { text: "Searching for sustainability reports...", icon: "M21 21l-5.197-5.197m0 0A7.5 7.5 0 1 0 5.196 5.196a7.5 7.5 0 0 0 10.607 10.607Z" },
  { text: "Checking packaging commitments...", icon: "M20.25 7.5l-.625 10.632a2.25 2.25 0 0 1-2.247 2.118H6.622a2.25 2.25 0 0 1-2.247-2.118L3.75 7.5M10 11.25h4M3.375 7.5h17.25c.621 0 1.125-.504 1.125-1.125v-1.5c0-.621-.504-1.125-1.125-1.125H3.375c-.621 0-1.125.504-1.125 1.125v1.5c0 .621.504 1.125 1.125 1.125z" },
  { text: "Looking up regulatory context...", icon: "M12 21v-8.25M15.75 21v-8.25M8.25 21v-8.25M3 9l9-6 9 6m-1.5 12V10.332A48.36 48.36 0 0 0 12 9.75c-2.551 0-5.056.2-7.5.582V21M3 21h18M12 6.75h.008v.008H12V6.75z" },
  { text: "Reviewing supply chain footprint...", icon: "M8.25 18.75a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h6m-9 0H3.375a1.125 1.125 0 0 1-1.125-1.125V14.25m17.25 4.5a1.5 1.5 0 0 1-3 0m3 0a1.5 1.5 0 0 0-3 0m3 0h1.125c.621 0 1.129-.504 1.09-1.124a17.902 17.902 0 0 0-3.213-9.193 2.056 2.056 0 0 0-1.58-.86H14.25M16.5 18.75h-2.25m0-11.177v-.958c0-.568-.422-1.048-.987-1.106a48.554 48.554 0 0 0-10.026 0 1.106 1.106 0 0 0-.987 1.106v7.635m12-6.677v6.677m0 4.5v-4.5m0 0h-12" },
  { text: "Scanning for circular economy initiatives...", icon: "M16.023 9.348h4.992v-.001M2.985 19.644v-4.992m0 0h4.992m-4.993 0 3.181 3.183a8.25 8.25 0 0 0 13.803-3.7M4.031 9.865a8.25 8.25 0 0 1 13.803-3.7l3.181 3.182m0-4.991v4.99" },
  { text: "Checking industry pressures...", icon: "M2.25 18 9 11.25l4.306 4.306a11.95 11.95 0 0 1 5.814-5.518l2.74-1.22m0 0-5.94-2.281m5.94 2.28-2.28 5.941" },
  { text: "Looking up investor ESG disclosures...", icon: "M2.25 18.75a60.07 60.07 0 0 1 15.797 2.101c.727.198 1.453-.342 1.453-1.096V18.75M3.75 4.5v.75A.75.75 0 0 1 3 6h-.75m0 0v-.375c0-.621.504-1.125 1.125-1.125H20.25M2.25 6v9m18-10.5v.75c0 .414.336.75.75.75h.75m-1.5-1.5h.375c.621 0 1.125.504 1.125 1.125v9.75c0 .621-.504 1.125-1.125 1.125h-.375m1.5-1.5H21a.75.75 0 0 0-.75.75v.75m0 0H3.75m0 0h-.375a1.125 1.125 0 0 1-1.125-1.125V15m1.5 1.5v-.75A.75.75 0 0 0 3 15h-.75M15 10.5a3 3 0 1 1-6 0 3 3 0 0 1 6 0Zm3 0h.008v.008H18V10.5Zm-12 0h.008v.008H6V10.5Z" },
  { text: "Reviewing competitor moves...", icon: "M15 19.128a9.38 9.38 0 0 0 2.625.372 9.337 9.337 0 0 0 4.121-.952 4.125 4.125 0 0 0-7.533-2.493M15 19.128v-.003c0-1.113-.285-2.16-.786-3.07M15 19.128v.106A12.318 12.318 0 0 1 8.624 21c-2.331 0-4.512-.645-6.374-1.766l-.001-.109a6.375 6.375 0 0 1 11.964-3.07M12 6.375a3.375 3.375 0 1 1-6.75 0 3.375 3.375 0 0 1 6.75 0Zm8.25 2.25a2.625 2.625 0 1 1-5.25 0 2.625 2.625 0 0 1 5.25 0Z" },
];

// Alpine calls this function to build the component's data and methods.
function researchCard() {
  return {
    loading: false,
    researchingOrg: "",
    errorMessage: null,
    currentMessage: { text: "", icon: "" },
    cycleIndex: 0,
    cycleTimer: null,
    cycleMessages: RESEARCH_CYCLE_MESSAGES,

    startCycle() {
      // setInterval calls our function later, when "this" no longer points at
      // the component, so we save a reference to it first.
      const component = this;
      this.cycleIndex = 0;
      this.currentMessage = this.cycleMessages[0];
      this.cycleTimer = setInterval(function () {
        component.cycleIndex = (component.cycleIndex + 1) % component.cycleMessages.length;
        component.currentMessage = component.cycleMessages[component.cycleIndex];
      }, MESSAGE_CYCLE_INTERVAL_MS);
    },

    stopCycle() {
      if (this.cycleTimer) {
        clearInterval(this.cycleTimer);
        this.cycleTimer = null;
      }
    },

    resetAfterError() {
      this.stopCycle();
      this.loading = false;
      this.errorMessage = null;
    },

    handleResearchEvent(serverEvent) {
      if (serverEvent.type === "done") {
        this.stopCycle();
        window.location.href = "/review";
      } else if (serverEvent.type === "error") {
        this.stopCycle();
        if (serverEvent.message) {
          this.errorMessage = serverEvent.message;
        } else {
          this.errorMessage = "Something went wrong.";
        }
        this.loading = false;
      }
    },

    // "async" lets us use "await" inside, so the code reads top to bottom
    // even though the network requests take time.
    async handleSubmit(event) {
      const component = this;
      const formData = new FormData(event.target);

      let orgName = formData.get("org_name");
      if (!orgName) {
        orgName = "";
      }
      this.researchingOrg = orgName;
      this.loading = true;
      this.errorMessage = null;
      this.startCycle();

      try {
        const response = await fetch("/research-stream", { method: "POST", body: formData });
        await readServerSentEvents(response, function (serverEvent) {
          component.handleResearchEvent(serverEvent);
        });
      } catch (error) {
        this.stopCycle();
        this.errorMessage = "Connection failed. Please try again.";
        this.loading = false;
      }
    },
  };
}
