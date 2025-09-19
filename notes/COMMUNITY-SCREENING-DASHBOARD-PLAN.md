# Community Screening Dashboard - Redesign Plan

*Planning notes for making the community screening page more intuitive and educational for intelligent non-experts*

## **Target Audience**
- Intelligent non-experts (marine biologists without ML background, policy makers, researchers from other fields)
- Assume basic understanding of acoustic monitoring concept from earlier pages
- Focus: educational/explanatory with guided exploration approach

## **Overall Approach**
- **Tone**: Educational/explanatory (with light narrative elements, not overwrought)
- **Interactivity**: Basic interactivity unless more complexity adds real value
- **Technical Depth**: Stick with highlights, avoid jargon
- **Purpose**: Inform and possibly interest people in using the approach
- **Scope**: Keep examples general, don't overreach on conclusions
- **Style**: Be a guide, point out interesting things, avoid verbosity

## **Key Educational Goals**

### **1. Core Concepts to Communicate**
- **Screening concept**: Not identifying species, just "something biological happening" vs "ocean noise"
- **Threshold meaning**: "How sensitive should our detector be?" - concrete trade-offs
- **Performance metrics**: Translate to practical meaning (time saved, accuracy when flagged, etc.)
- **Timeline evidence**: Shows real biological rhythms, works across stations

### **2. Language Translations**
| Technical Term | Plain English |
|---|---|
| Threshold | "Detector sensitivity" |
| Precision | "When flagged, correct X% of the time" |
| Detection Rate/Recall | "Catches X% of real fish activity" |
| F1 Score | "Overall performance: X/1.0" |
| Effort Reduction | "Review only X% of recordings" |
| False Positives | "False alarms" |
| False Negatives | "Missed opportunities" |

## **Interface Improvements Plan**

### **Controls Section**
- **"Screening Target"** → **"What to look for:"** [Any fish activity / High activity periods / Multiple species events]
- **"Threshold"** → **"Detector sensitivity:"** with explanation "Higher = more sensitive but more false alarms"
- Add brief explanatory text under each control

### **Metrics Cards**
- **"Detection Rate"** → **"Catches X% of real fish activity"**
- **"Precision"** → **"When flagged, correct Y% of the time"**
- **"Effort Reduction"** → **"Review only Z% of recordings"**
- **"F1 Score"** → **"Overall performance: X/1.0"**

## **Major Visualization Change: Timeline Three-View System**

### **Current Problem**
- Timeline is just another heatmap (similar to data page)
- Doesn't clearly show the screening concept in action
- Missing the "false positive/false negative" educational opportunity

### **Proposed Solution: Toggle Between Three Views**

#### **View 1: "Activity View" (Default)**
- Shows actual fish activity intensity (current heatmap)
- Color scale from low to high biological activity
- Title: "When fish were actually active"
- This is the ground truth baseline

#### **View 2: "AI Predictions View"**
- Shows what AI would flag at current threshold
- Binary color scheme:
  - Blue/teal: "AI flagged this period for review"
  - Gray/light: "AI said skip this period"
- Title: "What the AI would flag for manual review"
- Updates dynamically with threshold slider

#### **View 3: "Accuracy View"**
- Shows prediction accuracy
- Color scheme:
  - **Green**: Correct predictions
  - **Red**: False positives (AI flagged but no activity)
  - **Orange**: False negatives (AI missed real activity)
- Title: "How accurate were the AI predictions"
- Main educational component

### **User Experience Flow**
1. Start with Activity View (understand ground truth)
2. Switch to AI Predictions (see what screening would do)
3. Switch to Accuracy (evaluate how well it worked)
4. Adjust threshold → Views 2 & 3 update in real-time
5. Cycle between views to understand relationships

### **Educational Value**
- Makes screening concept concrete and visual
- Users can discover threshold trade-offs themselves
- Shows where/when AI works well vs poorly
- Demonstrates practical implications of different settings

## **Other Chart Improvements**

### **Threshold Chart**
- Title: "Sensitivity vs. Performance Trade-offs"
- Clear axis labels and current setting annotation
- Explain what each line means briefly

### **Model Comparison**
- Title: "Which detection method works best"
- Brief explanation of what each method means

### **Feature Importance**
- Title: "What the AI pays attention to"
- Brief explanation of why these features matter (month = seasonal patterns, temperature = fish behavior driver, etc.)

## **Content Structure Plan**

### **1. Brief Intro**
"This page shows how well AI can screen underwater recordings for biological activity"

### **2. Interactive Demo Section**
"Try adjusting the settings to see trade-offs"
- Guided experience with the three-view timeline
- Point out specific things to notice

### **3. Results Context**
"Here's how it performed with real data from 3 monitoring stations"
- Highlight interesting patterns without overstating

### **4. Key Insights**
- 2-3 main takeaways
- Integrated caveats about single study system
- Brief "possible implications" without overreaching

## **Technical Implementation Notes**

### **Data Requirements**
- Need actual vs predicted classifications for each timeline cell
- Requires model predictions at cell-level (not just aggregate stats)
- May need to regenerate view data with per-sample predictions

### **UI Components**
- Toggle buttons for three timeline views
- Dynamic titles that update with view selection
- Real-time updates when threshold changes
- Clear legends for each view's color scheme

## **Next Steps**
1. Implement three-view timeline visualization system
2. Update data generation to include per-sample predictions
3. Revise interface language and explanations
4. Test educational flow with the new visualizations
5. Finalize text content around the improved visualizations

---

*Created: 2025-01-19*
*Status: Planning phase - ready for implementation*