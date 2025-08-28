/**
 * CONTENT HELPER FILE - Safe for non-programmers to edit
 * 
 * EDITING RULES:
 * - Only edit text between quotes: "like this text"
 * - Do NOT change anything outside the quotes
 * - Do NOT delete the commas or brackets
 * - Keep text simple and clear
 * - This content is for the Acoustic Analysis page showing PCA and index categorization
 */

export const PageContent = {
  header: {
    title: "Acoustic Analysis Summary",
    subtitle: "Principal Component Analysis and Index Categorization for Marine Soundscape Research"
  },
  
  loading: {
    message: "Loading acoustic analysis data..."
  },
  
  error: {
    title: "Error Loading Data",
    message: "Unable to load acoustic analysis information",
    suggestion: "Please try refreshing the page"
  },
  
  noData: {
    message: "No acoustic analysis data available"
  },
  
  pca: {
    title: "Principal Component Analysis (PCA)",
    description: "Dimensionality reduction of 61 acoustic indices into key components that explain the most variation in the data",
    components: {
      title: "Principal Components"
    },
    variance: {
      title: "Total Variance Explained", 
      subtitle: "of acoustic variation captured",
      description: "These components capture the most important patterns in the acoustic data, allowing researchers to focus on the most informative aspects of marine soundscapes"
    }
  },
  
  categories: {
    title: "Acoustic Index Categories",
    description: "Research-based groupings of acoustic indices by their measurement domain and biological relevance",
  },
  
  stations: {
    title: "Station Acoustic Summaries",
    description: "Overview of acoustic measurements by monitoring station"
  }
}