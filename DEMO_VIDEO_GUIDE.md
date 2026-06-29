# 🎥 5-Minute Demo Video Script & Script Outline

This guide provides a professional, section-by-section script and walkthrough outline for recording a **5-minute demo video** of the Agentic AI Platform.

---

## ⏱️ Video Timestamp & Script Outline

| Time | Section | Screen Focus | Speaking Points & Narrative |
| :--- | :--- | :--- | :--- |
| **0:00 - 0:45** | **1. Hook & Introduction** | Dashboard Page (Dark Mode / Glassmorphism UI) | Introduce the platform as a domain-agnostic Multi-Agent AI system. Explain the core problem it solves: decoupling sales/qualification requirements from fixed SaaS schemas to support any domain (e.g., solar energy, clinical medical equipment). |
| **0:45 - 1:45** | **2. Defining target parameters** | **ICP & Config** Page | Show how easy it is to define a custom search. Configure a target sector (e.g., Hospital), specify a custom size unit (`beds` range: 50–200), set target keywords (e.g., *Solar, Rooftop*), and add target personas (*Director of Facilities*). Save configuration. |
| **1:45 - 2:45** | **3. Creating a Custom Plugin** | **Plugins** Page | Show how to build a custom domain. Click **+ Create Plugin**, call it `Solar Hospital Discovery`, and write a natural language qualification requirement: *"Must have open terrace space for panel installation and utilize more than 50kW electricity."* Enable the plugin. |
| **2:45 - 3:45** | **4. Running the Multi-Agent Pipeline** | **Dashboard** & **Results** Page | Go to the Dashboard, type in: *"Find hospitals in Mumbai for solar installation."* Click **Start Workflow**. Immediately show the **Animated Pipeline Loader**. Point out the active stage nodes (Planner -> Research -> Qualification) and how the badges transition to green in real-time. |
| **3:45 - 4:30** | **5. The Context-Aware Assistant** | **Results** Page (Active Chatbot) | Once results load, open the floating **Assistant Bot** in the bottom-right. Speak into the mic button: *"Why did the top company match?"* The chatbot fetches the results from MongoDB and outputs the detailed match reason. Toggle the speaker to show text-to-speech reading the reply out loud. |
| **4:30 - 5:00** | **6. Outro & Key Takeaways** | Results Page & CRM CSV Export | Click **Export CSV** to show how matches export directly to HubSpot/Salesforce formats. Summarize the benefits: full domain reusability, modular capability-based agents, and interactive speech capabilities. |

---

## 🎙️ Sample Script & Voiceover Guide

### Section 1: Introduction (0:00 - 0:45)
> *"Hello and welcome. Today we are demonstrating the Agentic AI Platform, a highly extensible multi-agent system designed for automated B2B customer discovery and lead qualification. Traditional discovery tools are locked into fixed SaaS profiles, but this platform is entirely domain-agnostic. Whether you're looking for clinical labs, solar-ready factories, or academic research departments, you can build and run targeted discovery workflows using natural language."*

### Section 2: Configuration & Plugins (0:45 - 2:45)
> *"Let's set up a custom business use case. We want to find mid-sized hospitals in Mumbai suitable for solar energy installations. Under our Settings configuration, we define target organization types as 'Hospital' and set our target keywords. We've introduced a dynamic size unit: instead of employees, we choose 'beds' as our unit and set a range of 50 to 200. Next, we define target personas: we want to reach Directors of Facilities.*
>
> *To tailor the qualifying rules, we go to Plugins and register a new Custom Domain Plugin called 'Solar Hospital Sales'. We input a specific qualification requirement: 'Must have open roof space and high electricity usage'. Saving this instantly binds these custom rules to the orchestration engine."*

### Section 3: Live Workflow & Animated Pipeline (2:45 - 3:45)
> *"Now we go to our Dashboard and type our search request: 'Find hospitals in Mumbai for solar installation.' When we hit 'Start Workflow', the system navigates to the Results page. Notice this loading screen. Instead of a blank page, we see a live execution pipeline. The Planner Agent evaluates the query and routes it to our custom plugin. Research, Qualification, and Validation agents execute in sequence. You can see the active status badges and elapsed timer update in real-time."*

### Section 4: Conversational Assistant & Voice Integration (3:45 - 4:30)
> *"The workflow is complete, producing a structured advisory report and a qualified prospect list. To explain these recommendations, we've built a persistent, context-aware Voice Assistant in the bottom-right. I'll click the microphone to speak: 'Why was the top hospital qualified?'*
>
> *The backend fetches the matched prospects from MongoDB, parses their profiles against our custom qualification rules, and Gemini explains the logic. I can also toggle the speaker to listen to the audio output: [Demonstrate Audio Synthesis]."*

### Section 5: Outro & Export (4:30 - 5:00)
> *"Finally, we can download our final report as a text file or export the qualified leads as a CRM-ready CSV mapping all contact emails, titles, and match scores. In just five minutes, the platform dynamically planned, qualified, enriched, and validated targets using custom enterprise rules. Thank you."*
