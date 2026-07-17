---
name: canvas-design
description: "Use when designing canvas-based interfaces, diagramming surfaces, visual composition tools, or other spatially rich experiences. Helps with layout choices, hierarchy, interaction states, motion, and iterative refinement without falling back to generic UI patterns."
argument-hint: "What canvas or visual-composition experience should be designed?"
---

# Canvas Design

## Purpose
Use this skill to plan and refine canvas-driven experiences such as whiteboards, drawing surfaces, visual editors, diagram tools, mood boards, and other composition-heavy interfaces.

It helps produce designs that feel intentional by focusing on:
- the core user outcome on the canvas
- the primary objects, tools, and surfaces
- visual hierarchy and spatial structure
- interaction affordances and feedback
- motion, transitions, and selection states
- responsiveness across desktop and mobile

## When To Use It
Use this skill when you need to:
- design a new canvas-based interface
- revise an existing drawing, layout, or editing surface
- evaluate tool placement, overlays, or empty states
- turn rough product intent into a concrete visual workflow
- avoid bland, default-looking composition patterns

## Workflow
1. Identify the job to be done.
   - What is the user trying to create, inspect, compare, or manipulate?
   - What is the primary object on the canvas?
   - What is secondary and can be de-emphasized?

2. Define the interaction model.
   - Is the experience read-only, editable, or mixed?
   - What are the core tools and gestures?
   - What happens on hover, selection, drag, zoom, pan, resize, and keyboard shortcuts?

3. Establish the spatial structure.
   - Choose a layout that supports the task, not a generic shell.
   - Decide where controls live relative to the main surface.
   - Reserve enough space for overlays, inspectors, legends, and status.

4. Set the visual language.
   - Pick typography, color, surface treatment, and emphasis rules.
   - Use contrast and spacing to guide attention.
   - Add background treatment, depth, or texture only where it improves orientation.

5. Check the hard cases.
   - Empty state
   - Dense or cluttered state
   - Selected or focused state
   - Error, loading, or syncing state
   - Small screens and constrained viewports

6. Refine for clarity.
   - Remove controls that do not directly support the main task.
   - Tighten labels and affordances.
   - Ensure the most common action is easiest to find and perform.

## Completion Criteria
A design is ready when:
- the main task is obvious within a few seconds
- the control surface matches the interaction model
- empty, selected, error, and loading states are defined
- the layout works on both large and small screens
- the result feels deliberate rather than template-driven

## Output Shape
When using this skill, produce:
- a concise design direction
- the layout and control placement
- the key interaction states
- motion notes and feedback rules
- open questions that still block implementation

## Reference Checklist
Before finalizing, confirm:
- the primary object and primary action are explicit
- controls are grouped by frequency of use
- the main surface has enough breathing room
- selection and editing feedback is unambiguous
- no unnecessary chrome competes with the canvas

## How To Test
In Claude.ai Projects, Claude Desktop, or a similar assistant setup, test the skill with two prompts:
- a broad canvas-design request, such as designing a whiteboard or diagram editor
- a refinement request, such as improving empty, selected, or loading states

The skill is working if the response follows the workflow, covers interaction states, and produces a deliberate layout instead of a generic UI shell.