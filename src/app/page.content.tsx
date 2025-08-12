/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * This file contains only the text content for the homepage.
 * You can safely edit any text between the quotes without breaking the website.
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 */

export const HomepageContent = {
  // Main hero section at the top of the page
  hero: {
    title: "Marine Biodiversity",
    titleHighlight: " Observatory", // This part gets special blue/coral styling
    subtitle: "Exploring relationships between computed acoustic indices and species presence using data collected at three stations in May River, South Carolina."
  },

  // The four metric cards showing key numbers
  metrics: {
    detections: "Total Detections",
    species: "Species Tracked", 
    stations: "Monitoring Stations",
    studyPeriod: "Study Period"
  },

  // The heatmap chart section
  speciesChart: {
    title: "Species Activity Timeline",
    loadingText: "Loading species detection data...",
    noDataText: "No detection data available"
  },

  // The map section
  stationMap: {
    title: "Station Distribution Map",
    loadingText: "Loading station locations...",
    noDataText: "No station data available"
  },

  // Quick navigation cards at the bottom
  quickNavigation: {
    acousticAnalysis: {
      title: "Acoustic Analysis",
      description: "Which acoustic indices best predict marine biodiversity?"
    },
    environmentalFactors: {
      title: "Environmental Factors", 
      description: "How do temperature, depth, and seasonality affect indices?"
    },
    indexGuide: {
      title: "Index Guide",
      description: "Understanding acoustic indices and their biological meaning"
    },
    stationProfiles: {
      title: "Station Profiles",
      description: "Spatial context and deployment details for 9M, 14M, 37M"
    },
    dataExplorer: {
      title: "Data Explorer",
      description: "Filter and explore the full dataset"
    }
  },

  // Status messages
  statusMessages: {
    connectionError: "Unable to connect to data source",
    connectionSuccess: "Data connection successful",
    lastUpdated: "Last updated: "
  }
}