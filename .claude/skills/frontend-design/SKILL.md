---
name: frontend-design
description: Use this skill during the planning phase of any frontend UI work on Spendly, the Flask/Jinja2 expense tracker — server-rendered templates, hand-written vanilla CSS with a CSS-variable design system, and a sprinkle of vanilla JS, no frameworks. Trigger it whenever the user asks to design, redesign, plan, sketch, or mock up any page, view, component, form, or layout in this app (dashboard, expense list, add/edit expense form, filters, charts, empty states, settings, nav, cards, tables — anything visual), even if they just say "make this page look better" or "can we improve the UI" without using the word "design." Also trigger for requests to make the app "feel more like a real product," "less generic," or "more polished/fintech." This skill produces a plan.md describing the UI changes before any HTML/CSS/JS is written — do not skip straight to code for non-trivial UI requests.
---

# Spendly UI Design Planning

Spendly's UI is server-rendered Jinja2 + hand-written CSS + vanilla JS — deliberately not a React/Tailwind stack. The visual bar, though, is a real fintech product: something like a well-made budgeting or banking app, not a bootstrap-era admin panel. Those two things — plain-HTML implementation, polished fintech feel — are both non-negotiable, and most low-quality UI output fails by picking one and dropping the other (either it looks default-Bootstrap because no one thought about the visual craft, or it looks like a React app got transplanted with divs and shadows that don't belong). This skill exists to hold both at once, and to do it consistently with whatever already exists in the app rather than as a one-off reinvention.

The deliverable at the end of this skill is **`plan.md`** — a design and implementation plan written *before* touching template or CSS files. Planning first matters here specifically because Spendly already has a design system (`:root` custom properties, a specific type pairing, an established visual language) — jumping straight to code risks inventing a second, competing design language instead of extending the one that's there.

## Step 1: Look before you design anything

Never design in a vacuum. Before proposing anything new, ground yourself in what already exists:

- Open `templates/base.html` — this is the shell every page lives in: navbar, footer, and the fonts/meta loaded for the whole app.
- Open the main stylesheet (e.g. `static/css/style.css`) — this holds the actual design system: `--ink*`, `--paper*`, `--accent*`, `--border*`, `--radius-*`, font variables, and how existing sections (buttons, cards, forms) are built. Read enough of it to know what visual vocabulary already exists — don't just skim the top.
- Open one or two existing templates that are visually representative of the app (a finished page if one exists, otherwise whatever's closest to the page you're now designing).

The goal isn't just "don't clash" — it's that a person using the finished app should never be able to tell which screen was designed in which session. If you can see these files (repo access, uploaded files, or you're working inside the codebase), always open them first, even if the user's request sounds simple.

**If you genuinely can't see the existing UI** (no file access, nothing uploaded) and the request is anything beyond a trivial tweak, stop and ask the user for a screenshot of an existing page, or ask them to paste in the base template or stylesheet. One screenshot of the current dashboard up front saves several rounds of "actually that doesn't match" later. Don't guess at a design system that might already exist.

## Step 2: What "polished fintech," not "generic," actually means

This is the checklist that separates the two failure modes described above. Use it while forming the plan — not as boxes to tick mechanically, but as the set of decisions that tend to be the difference between an app that looks considered and one that looks templated:

- **Numbers are the content.** In an expense tracker, currency amounts, dates, and category labels carry the actual information. Give them real typographic weight and alignment — right-align numeric columns, use tabular/monospaced figures where the stylesheet's type system allows it, let amounts be visually heavier than their labels. A list of transactions where every column is left-aligned body text is the single most common tell of an unpolished finance UI.
- **Restrained color, deliberate accent.** Fintech UI earns trust partly by not shouting. Backgrounds stay close to neutral (paper/ink tones already defined), and the accent color is spent on the few things that matter — a positive/negative amount, a primary action, a status pill — not scattered across every heading and icon. If a new color is tempting, it should almost always be a variation of an existing `--accent`/`--danger` token, not a new hue.
- **Whitespace has rhythm, not just padding.** Generic UI pads everything the same amount. Polished UI uses a consistent spacing scale so related things sit close and unrelated things sit apart — the eye should be able to tell groupings without reading labels.
- **Hierarchy comes from type and weight, not boxes.** Reach for font size, weight, and color (all already defined as variables) before reaching for a new border or drop shadow to separate sections. Overuse of card borders/shadows on every element is a classic "admin template" tell.
- **States are designed, not afterthoughts.** Empty states (no expenses yet), loading, and error/validation states are where generic UIs visibly give up (a bare "No data" string). Plan real content for these — what does a first-time user see on an empty dashboard?
- **Motion is subtle and functional.** Any interaction (hover, a value updating, a row appearing) should use quick, restrained transitions consistent with what's already in the CSS (per this codebase's convention, inline transition shorthand on the base rule) — not novel animation patterns that don't exist anywhere else in the app.
- **Forms feel considered.** Label placement, input sizing, inline validation messaging, and button hierarchy (primary vs. secondary action) should read as intentional, matching whatever pattern the existing auth/forms already establish.

Not every point applies to every page — use judgment about which of these actually matter for the specific view being planned, and say so in the plan rather than mechanically restating the whole list.

## Step 3: Write plan.md

Structure the plan with these sections. Keep it in prose within sections — this is a design document a person will read, not a form to fill in.

```markdown
# UI Plan: <page/feature name>

## Design intent
What this page/component needs to communicate and feel like, in a sentence or two.
Which of the fintech-polish considerations (Step 2) matter most here and why.

## Consistency check
What you found in base.html / the stylesheet / existing templates that this design
must match or extend (specific variables, patterns, components already in use).
Note anything genuinely new this page needs (e.g. a chart, a data table) that has
no existing precedent in the codebase, since that's where new variables or patterns
may need to be introduced deliberately rather than invented ad hoc.

## Files touched
List of template/CSS/JS files that will change or be created.

## Section-by-section plan
Walk through the page/component top to bottom (or component by component),
describing the structure and visual treatment of each part in prose — layout,
which existing CSS classes/variables apply, what's new, and why. This is the
part someone should be able to read and picture the finished page from.

## Open questions / assumptions
Anything the plan had to assume in place of information you didn't have
(e.g. "assumed there's no receipt-image feature yet"), and anything worth
the user weighing in on before implementation starts.
```

Save this as `plan.md` (in the project root, or alongside other planning docs if the project has a convention for that). Do not begin writing template/CSS/JS changes in the same pass — the plan is the deliverable; implementation is a separate, later step once the user has reviewed it.

## A note on the stack constraint

Nothing in this skill is license to reach for a CSS framework, a JS framework, or utility classes that don't fit a hand-written stylesheet — the polish has to come from typography, spacing, color restraint, and layout, expressed in plain CSS. If the project's own conventions (e.g. a CLAUDE.md, or patterns visible in the existing stylesheet) specify things like "no raw hex values, only CSS variables" or "class selectors only, no IDs," the plan must work within those, not around them.