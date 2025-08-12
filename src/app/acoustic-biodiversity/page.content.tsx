/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * This file contains only the text content for the Acoustic Biodiversity page.
 * You can safely edit any text between the quotes without breaking the website.
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 */

export const AcousticBiodiversityContent = {
  // Page header
  header: {
    title: "Acoustic Indices and",
    titleHighlight: " Marine Soundscapes", // This part gets special blue/coral styling
    subtitle: "Analysis to identify which acoustic indices best predict marine soundscape biodiversity and environmental patterns."
  },

  // Research focus box
  researchFocus: {
    title: "Research Question",
    description: "Which acoustic indices most accurately predict species presence and and could be used as environmental indicators?"
  },

  // Correlation Analysis section
  correlationAnalysis: {
    title: "Index-Species Correlations",
    status: "(Planned)",
    description: "Statistical analysis of relationships between acoustic indices and species detections to identify the most informative indices for biodiversity assessment."
  },

  // PCA section
  pca: {
    title: "Principal Component Analysis",
    status: "(Planned)",
    description: "Dimensionality reduction to understand relationships among acoustic indices and their combined ability to explain biodiversity patterns."
  },

  // Signal differentiation section
  signalDifferentiation: {
    title: "Signal Source Differentiation",
    status: "(Planned)",
    description: "Analysis of whether acoustic indices can differentiate between biological sounds (species vocalizations) and anthropogenic noise (vessels, human activity).",
    biological: {
      label: "Biological Sources:",
      description: "Fish calls, marine mammal vocalizations, invertebrate sounds"
    },
    anthropogenic: {
      label: "Anthropogenic Sources:",
      description: "Vessel noise, mechanical sounds, human activities"
    }
  },

  // Data note at bottom
  dataNote: {
    label: "Note:",
    text: "Analysis will be conducted once the full suite of 60+ acoustic indices becomes available. Current explorations use manual species annotations from 2018 and 2021."
  }
}