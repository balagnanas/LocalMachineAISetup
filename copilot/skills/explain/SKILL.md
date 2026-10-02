---
name: explain
description: Explain complex topics, code, plans, or language-model outputs with clear controlled prose and, when useful, diagrams, interactive HTML, or custom explainer videos. Use when the user asks to understand how something works or requests an explainer artifact.
---

# Explain

Make the subject easy to understand and inspect. Tailor the explanation to the user's question, background, and desired depth. Use the conversation and relevant source material to establish what needs explaining; inspect referenced code or documents before describing their behavior.

## Choose the medium

Honor an explicitly requested format. Otherwise choose the smallest medium that makes the important idea clear. Combine a visual with brief prose when each adds useful information.

| Medium | Best fit | Deliverable |
| --- | --- | --- |
| Writing | Direct answers, definitions, or a short argument | Concise explanation in chat |
| Diagram | Structure, dependencies, sequence, or state changes | Labeled diagram with a short takeaway |
| Interactive HTML | Cause and effect, adjustable examples, comparisons, or exploration | Working page or an inline interactive visualization |
| Explainer video | Requested narrated walkthroughs or concepts that benefit from motion | Rendered video, with captions or a transcript |

Treat rich artifacts as a way to reduce the user's effort. A request to explain something does not by itself authorize a paid service, publication, or modification of the system being explained.

## Write clearly

Default to prose inspired by ASD-STE100 Simplified Technical English: roughly "80% of the way" to the controlled language, with enough flexibility for natural explanations. This is a writing preference, not a measurable compliance score.

- Lead with the answer or central idea. Build from context to mechanism to consequence.
- Use short sentences, active voice, concrete verbs, and one main idea per sentence.
- Use the same term for the same thing. Preserve domain terms and code identifiers; define unfamiliar terms once.
- Make actors, conditions, units, and cause-and-effect relationships explicit.
- Give one concrete example when it resolves an abstraction. Identify where an analogy stops matching reality.
- Separate observed facts, simplified models, assumptions, and uncertainty. Preserve exceptions that change the conclusion.

If the user requests strict ASD-STE100 compliance, consult the applicable authoritative specification and vocabulary before claiming compliance. State any parts that remain unverified.

## Make diagrams useful

Choose the visual form that matches the relationship: a flow for sequence, a tree for hierarchy, a table for comparison, or a chart for quantities. Prefer Mermaid for simple structures and SVG or available image tools when spatial layout or illustration adds meaning. If a suitable visualization skill is available, follow its rendering instructions.

Label nodes, arrows, and units so the diagram can be understood without guessing. Use consistent labels across prose and visuals. Keep essential meaning available through text as well as color. Verify depicted behavior against the underlying evidence.

## Build interactive explainers

Make the interaction answer a real question: "What changes if this input changes?" or "How does the next step follow?" Use purposeful typography, readable spacing, and a clear visual hierarchy. Keep the initial view useful before interaction.

Use the host's inline visualization tools when available. For a standalone HTML request, prefer a self-contained page with local logic and minimal dependencies. Include responsive layout, keyboard-accessible controls, visible labels, and reduced-motion support. Show model assumptions and meaningful limits alongside the interaction.

Exercise the main interaction, boundary values, and a narrow viewport. Present a usable preview or link to the saved artifact and report what was actually verified.

## Create explainer videos

For requested videos, define a short narrative and storyboard before rendering. Each scene should advance one idea. Use mathematical animation, progressive construction, and synchronized narration when helpful; a request for a "3b1b-style" explainer can guide these techniques without implying affiliation or copying existing footage.

Inspect available rendering and audio tools first. Prefer installed local tools for a feasible local workflow. Use an external narration service such as ElevenLabs only when the user has authorized it and suitable credentials are already provided through a secure mechanism. Keep credentials out of prompts, generated files, logs, and version control. Explain expected costs and data transfer before using a service when those are not already authorized.

When requested, investigate viable free or local narration options against current primary documentation. If rendering or narration is unavailable, provide the best runnable source or storyboard, identify the missing capability, and clearly distinguish it from a finished video.

Check the rendered output for accurate labels, legible text, scene timing, audio synchronization, and caption or transcript accuracy. Deliver the playable result and useful source files when available.

## Check the explanation

Before delivery, confirm that the result answers the user's actual question, traces material claims to relevant evidence, and keeps uncertainty visible. Remove detail that does not help understanding. Verify generated artifacts in proportion to their complexity and state any untested behavior precisely.
