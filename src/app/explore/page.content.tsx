/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * This file contains only the text content for the main Explore page.
 * You can safely edit any text between the quotes without breaking the website.
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 */

export const ExploreContent = {
  // Page header
  header: {
    title: "Data",
    titleHighlight: " Explorer", // This part gets special blue/coral styling
    subtitle: "Interactive exploration of marine biodiversity data across multiple perspectives and scales."
  },

  // Navigation cards
  sections: {
    annotations: {
      title: "Species Detection Annotations",
      description: "Explore manual species annotations and detection patterns across stations and time periods.",
      features: ["Monthly detection timelines", "Species activity patterns", "Station comparisons", "Temporal trends"]
    },
    
    indices: {
      title: "Acoustic Indices Overview", 
      description: "Discover patterns in 60+ acoustic indices across different environmental conditions and frequency ranges.",
      features: ["Temporal heatmaps", "Bandwidth comparisons", "Statistical distributions", "Index correlations"]
    }
  }
}