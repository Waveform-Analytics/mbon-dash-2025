/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"  
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 * - Keep text simple and clear
 * - No HTML formatting needed
 */

export const SpeciesV2PageContent = {
  header: {
    title: "Species Timeline (Optimized View)",
    subtitle: "Monthly aggregated species detection patterns with high-performance data loading"
  },
  
  sections: {
    performance: {
      title: "Performance Optimization",
      description: "This page loads optimized view data (~1.6KB) instead of raw detection data (potentially MB+)"
    },
    
    timeline: {
      title: "Species Detection Timeline", 
      description: "Monthly detection patterns for biological species across all monitoring stations"
    },
    
    methodology: {
      title: "Data Processing",
      description: "Detection data is aggregated monthly and filtered to biological species only, excluding anthropogenic sounds"
    }
  },

  loading: {
    message: "Loading species timeline data..."
  },
  
  error: {
    title: "Error Loading Data", 
    message: "Unable to load species timeline information",
    details: "Please try refreshing the page"
  },

  noData: {
    title: "No Species Data",
    message: "No species timeline data is currently available"
  }
};