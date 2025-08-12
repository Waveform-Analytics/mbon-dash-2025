/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * This file contains only the text content for the Environmental Factors page.
 * You can safely edit any text between the quotes without breaking the website.
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 */

export const EnvironmentalFactorsContent = {
  // Page header
  header: {
    title: "Environmental",
    titleHighlight: " Confounders", // This part gets special blue/coral styling
    subtitle: "Analysis of how environmental factors influence acoustic indices and their effectiveness as biodiversity indicators."
  },

  // Research focus box
  researchFocus: {
    title: "Research Questions",
    questions: [
      "Do temperature and depth significantly affect acoustic indices?",
      "Should indices be environmentally corrected for biodiversity assessment?",
      "Are index patterns driven by environmental conditions or biological activity?"
    ]
  },

  // Temperature section
  temperature: {
    title: "Temperature Effects",
    status: "(Planned)",
    description: "Analysis of temperature correlations with acoustic indices to identify potential confounding effects on biodiversity predictions."
  },

  // Depth section
  depth: {
    title: "Depth Effects",
    status: "(Planned)",
    description: "Evaluation of water depth influences on acoustic measurements and the need for depth-based corrections."
  },

  // Temporal patterns section
  temporal: {
    title: "Temporal Patterns",
    status: "(Planned)",
    description: "Investigation of seasonal and diel patterns in acoustic indices to separate environmental from biological drivers."
  },

  // Data note at bottom
  dataNote: {
    label: "Note:",
    text: "Environmental analysis will utilize temperature and depth data collected during deployments, combined with the full suite of acoustic indices when available."
  }
}