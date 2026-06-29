# 🎬 5-Minute Demo Video — Full Script & Walkthrough

> Use this document as your **exact speaking script** when recording the 5-minute demo video.
> Each section has a timestamp, what to show on screen, and word-for-word narration.

---

## 🎯 Video Title
**"AI Agentic Platform — Automated B2B Lead Discovery & Qualification Demo"**

---

## ⏱️ Section 1: Introduction & Problem Statement (0:00 – 0:40)

### 🖥️ Show on Screen
- Keep the **Dashboard page** (`http://localhost:5173/dashboard`) open in the background
- No actions yet — just the glassy dark-themed UI visible

### 🎙️ Speak This
> *"Traditional B2B sales teams spend hours manually searching directories, cold-calling, and guessing which companies might be a fit. There's no scalability, no intelligence, and no automation.*
>
> *We built the Agentic AI Platform — a fully reusable, multi-agent AI system that automates B2B customer discovery, qualification, and contact enrichment for any business domain.*
>
> *Whether you're selling solar energy systems to hospitals, EHR software to clinics, or equipment to factories — this platform adapts instantly to your domain without a single line of code change.*
>
> *Let me show you how."*

---

## ⏱️ Section 2: Platform Configuration — Defining the Target (0:40 – 1:30)

### 🖥️ Show on Screen
- Click **ICP & Config** in the sidebar
- Live-fill the form fields while speaking:
  - **Target Organization Types**: Select `Hospital`
  - **Target Geographies**: Type `Mumbai, Delhi, Bangalore`
  - **Target Keywords**: Type `Solar energy, Rooftop, Net-metering`
  - **Size Range**: Set `50` to `200`, Unit: `beds`
  - **Business Triggers**: Check `Budget Allocation Q1`, `Expansion Plans`
  - **Target Personas**: `Director of Facilities`, `Head of Operations`
- Click **Save Configuration**

### 🎙️ Speak This
> *"We start by configuring who we're targeting. Under ICP & Config, I'm defining our Ideal Customer Profile.*
>
> *Our business case today: we're a solar energy company targeting mid-sized hospitals in India — specifically those with 50 to 200 beds — that could benefit from rooftop solar installations.*
>
> *Notice the size unit is not restricted to 'employees' like every generic SaaS tool. We're using 'beds' — because hospitals are measured that way. The platform is completely domain-agnostic.*
>
> *I'm also adding the decision-makers we want to reach: the Director of Facilities and the Head of Operations. Saving this configuration now wires these rules into every agent in the system."*

---

## ⏱️ Section 3: Custom Plugin — Business-Specific Rules (1:30 – 2:20)

### 🖥️ Show on Screen
- Click **Plugins** in the sidebar
- Show the existing `B2B Sales Intelligence` plugin is enabled (green badge)
- Click **+ Create Plugin**
- Fill in:
  - **Plugin Name**: `Solar Hospital Sales`
  - **Description**: `Discovers solar-ready hospitals in India`
  - **Qualification Requirements**:
    - `Must have open terrace or rooftop space suitable for solar panels`
    - `Must have monthly electricity bills above 50,000 INR`
    - `Must not already have a solar installation`
- Click **Save Plugin** → the new plugin appears enabled

### 🎙️ Speak This
> *"Our platform supports custom domain plugins — think of these like business rule modules that agents use to qualify leads.*
>
> *You can see the built-in B2B Sales and HR Recruitment plugins already enabled. But we can also create our own.*
>
> *I'm creating a 'Solar Hospital Sales' plugin and writing plain English qualification rules: the hospital must have open rooftop space, high electricity bills, and must not already have solar panels.*
>
> *The AI agents will read and apply these exact rules when evaluating every hospital they find. No SQL, no regex — just plain language business logic."*

---

## ⏱️ Section 4: Running the Workflow (2:20 – 3:20)

### 🖥️ Show on Screen
- Click **Dashboard** in the sidebar
- In the search box, type:
  `"Find hospitals in Mumbai that are ideal candidates for solar energy installation"`
- In the Plugin dropdown — select **Solar Hospital Sales** (or leave Auto-detect)
- Click **⚡ Start Workflow**
- The page transitions to **Results** — the animated pipeline appears immediately
- Show the animated pipeline nodes: Planner → Research → Qualification → Contact Discovery → Validation → Report
- Point to each node lighting up green, the elapsed timer, and the spinning status messages

### 🎙️ Speak This
> *"Now let's run the workflow. On the Dashboard, I enter a natural language request: 'Find hospitals in Mumbai that are ideal candidates for solar energy installation.'*
>
> *I select our custom Solar Hospital Sales plugin and click Start.*
>
> *Instead of a blank loading screen, the platform shows a live pipeline tracker. You can see exactly which agent is running in real time — the Planner has parsed the query and built a step sequence. Research agents are now discovering and scraping hospital data. Qualification agents are scoring each one against our rules. Contact Discovery is finding the right decision-makers.*
>
> *Every stage transitions from pending to active to complete — with a live elapsed timer so you always know the system is working."*

---

## ⏱️ Section 5: Results — Qualified Leads & Report (3:20 – 4:10)

### 🖥️ Show on Screen
- The pipeline finishes — results appear below
- Scroll through the **Summary Report** at the top
- Show 2–3 **Prospect Cards** — each showing:
  - Organization name, type, location
  - Match percentage badge (e.g., 87%)
  - Match reason (e.g., "Open terrace confirmed, high electricity usage pattern detected")
  - Contact person (name, title, email)
- Click **Export CSV** — show the file download dialog
- Click **Download Report** — show the TXT download

### 🎙️ Speak This
> *"The workflow completes. At the top we have an executive summary with total prospects found, average qualification score, and recommended next actions.*
>
> *Each prospect card shows the organization name, its match percentage, and — critically — the exact reason it qualified. 'Open terrace confirmed, high electricity usage pattern detected.' This is not a black-box score. Every number has a transparent justification.*
>
> *Contact details include the decision-maker's name and role. This data maps directly into CRM pipelines like HubSpot or Salesforce.*
>
> *I can export the full list as a CSV or download the narrative report as a text file — all in one click."*

---

## ⏱️ Section 6: AI Assistant — Context-Aware Explanations (4:10 – 4:50)

### 🖥️ Show on Screen
- Click the **floating chat bubble** in the bottom-right corner
- The assistant panel opens
- Click one of the **quick action pills**: `"Why did the top prospect match?"`
- The chatbot fetches the result and displays a detailed paragraph explaining the qualification
- Now click the **microphone icon** 🎤 and speak:
  `"Who are the top 3 hospitals and what makes them suitable?"`
- Show the response appearing
- Click the **speaker icon** 🔊 to hear the response read aloud

### 🎙️ Speak This
> *"The platform also includes a built-in AI Assistant — accessible from anywhere in the app.*
>
> *I can ask it questions about these results. Watch: I'll tap the mic and ask 'Who are the top 3 hospitals and what makes them suitable?'*
>
> *The assistant connects directly to the workflow database, pulls the match data, and generates a natural-language explanation of the qualification logic. It even reads the answer aloud using text-to-speech.*
>
> *This is the power of context-aware AI — not a generic chatbot, but an assistant that knows your exact workflow, your exact results, and your exact business rules."*

---

## ⏱️ Section 7: Closing Summary (4:50 – 5:00)

### 🖥️ Show on Screen
- Return to the **Dashboard** — show the recent workflow in the history list
- Quick pan over: Config → Plugins → Results → Chatbot

### 🎙️ Speak This
> *"In under five minutes, the platform discovered, qualified, enriched, and explained hospital leads for a solar energy campaign — all through natural language, with full transparency, and zero manual research.*
>
> *This is the Agentic AI Platform. Modular. Reusable. Production-ready. Thank you."*

---

## 📋 Recording Checklist

Before hitting record, make sure:

- [ ] Backend running at `http://localhost:8001` ✅
- [ ] Frontend running at `http://localhost:5173` ✅
- [ ] ICP Config filled out (hospitals, Mumbai, solar keywords, beds unit)
- [ ] Custom plugin "Solar Hospital Sales" created and enabled
- [ ] Microphone is working and browser has mic permission
- [ ] Text-to-speech speaker is enabled in the assistant
- [ ] Screen recording software is capturing full screen at 1080p
- [ ] Browser zoom is set to 100% (no zoomed-in view)
- [ ] Dark mode / glassmorphism UI is visible and looks sharp
- [ ] Voice narration is clear — no background noise
