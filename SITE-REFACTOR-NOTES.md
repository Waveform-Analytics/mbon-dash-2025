# Site Refactor: Narrative-Driven Science Communication

## 🎯 **Overall Goal**
Transform the dashboard from scattered technical demonstrations into a compelling narrative about scaling marine biodiversity monitoring using acoustic indices.

## 📖 **New Narrative Structure**

### **Current**: Home | Data | Explore | Notebooks | Background
### **Target**: Home | The Challenge | Our Approach | Key Findings | Deep Dive

---

## ✅ **Progress Tracking**

### **Phase 1: Content & Structure Planning**
- [x] Analyzed current site structure and content
- [x] Developed narrative framework 
- [x] Clarified project context and attribution
- [ ] Create detailed content outlines for each page
- [ ] Plan component reuse and migration

### **Phase 2: Implementation**
- [x] Update navigation structure
- [ ] Refactor landing page (Home)
- [ ] Create "The Challenge" page (replaces Background)
- [ ] Merge Data + Explore into "Our Approach"  
- [ ] Elevate Community Screening to "Key Findings"
- [ ] Enhance "Deep Dive" (Notebooks + technical details)

### **Phase 3: Content Enhancement**
- [ ] Add contextual introductions to existing visualizations
- [ ] Create educational callouts (like Community Screening intro)
- [ ] Add clear navigation flow between sections
- [ ] Polish messaging and calls-to-action

---

## 🔑 **Key Messages (Finalized)**

### **Project Context**
- **What**: MBON-funded proof-of-concept using ESONS data
- **Innovation**: Acoustic indices (not ML) for community-level activity detection
- **Scope**: 1 year, 3 stations, May River - testing scalability potential
- **Validation**: Expert manual detections as ground truth
- **Attribution**: Building on Montie Lab (Eric Montie, Alyssa Marian) decade+ ESONS work

### **Impact Statement**
"This proof-of-concept demonstrates that acoustic indices can identify periods of marine community activity, offering a potential pathway for scalable marine biodiversity monitoring that could support diverse research and management goals."

---

## 📄 **Page-by-Page Plan**

### **1. Landing Page (Home)**
- **Hero**: "Can underwater sound patterns reveal marine ecosystem health?"
- **Key stats**: 1 year ESONS data, community-level detection, MBON-funded
- **Hook**: Focus on broader marine monitoring potential
- **CTA**: Clear path to "The Challenge"

### **2. The Challenge** (replaces Background)
- **Context**: ESONS foundation (Eric Montie Lab), MBON goals
- **Problem**: Scalable marine monitoring challenge  
- **Innovation**: Acoustic indices approach
- **Validation**: Ground truth methodology

### **3. Our Approach** (merges Data + Explore)
- **Study design**: Proof-of-concept scope
- **Data collection**: Existing station map/stats
- **Methodology**: Acoustic indices vs traditional approaches
- **Visualizations**: Existing heatmaps with narrative context

### **4. Key Findings** (elevates Community Screening)
- **Lead result**: 85% detection, 40-60% effort reduction
- **Interactive demo**: Community Screening dashboard with intro
- **Broader implications**: MBON/management applications

### **5. Deep Dive** (enhanced Notebooks)
- **Technical methods**: Existing notebook analysis
- **Validation details**: Statistical approaches
- **Future directions**: Multi-year, multi-site expansion
- **Reproducibility**: Code/data access

---

## 🔧 **Technical Implementation Notes**

### **Navigation Changes Needed**
- [x] Update `components/Navigation.tsx` with new structure
- [x] Update route structure in `app/` directory
- [x] Create placeholder pages for new routes
- [ ] Create redirects for old URLs if needed

### **Component Reuse Strategy**
- [ ] StationsMap: Move to "Our Approach" 
- [ ] All heatmaps: Keep but add narrative context
- [ ] CommunityScreeningDashboard: Promote to main "Key Findings"
- [ ] Stats cards: Enhance and reuse across sections

### **Content Migration Plan**
- [ ] Data page → Our Approach (sections 3A-3C)
- [ ] Explore subpages → Key Findings integration
- [ ] Background → The Challenge (complete rewrite)
- [ ] Notebooks → Deep Dive (enhanced context)

---

## 📝 **Content Writing Guidelines**

### **Tone & Approach**
- Lead with impact, follow with methods
- Progressive disclosure (overview → details)
- Multiple audience paths (managers → scientists → implementers)
- Respectful attribution to prior work

### **Section Intros Pattern**
Each major section should answer:
- **Why should I care?** (Stakes/importance)
- **What's the innovation?** (Unique approach)  
- **How well does it work?** (Evidence/validation)
- **What can I do with this?** (Applications/next steps)

---

## 🐛 **Issues & Decisions Log**

### **Decisions Made**
- Focus on acoustic indices, not ML as primary innovation
- Community-level detection messaging (not species-specific)
- MBON impact framing (broader than just ESONS)
- Proof-of-concept scope clarity (1 year, 3 stations)

### **Issues to Watch**
- [ ] Ensure all attribution is correct (Eric Montie, Alyssa Marian)
- [ ] Balance technical depth with accessibility
- [ ] Maintain visual design quality during restructure
- [ ] Test navigation flow with different user types

---

## 🎨 **Design Consistency Notes**

### **Visual Elements to Maintain**
- Current color scheme and component styling
- Motion/animation patterns
- Card-based layouts
- Existing chart/visualization designs

### **New Elements Needed**
- Section flow indicators
- Educational callout components (like Community Screening intro)
- Cross-references between sections
- Clear CTAs for different user paths

---

## 📋 **Next Session Prep**

### **Questions for Michelle**
- [x] Any specific messaging concerns for particular audiences? MW: not at this time
- [x] Preference for implementation order (navigation first vs content first)? MW: whatever you recommend
- [x] Any existing visualizations we should modify vs keep as-is? MW: If you think that any graphic could be improved, pause to discuss with me.

### **Phase 1 Complete - Navigation Structure**
- [x] Navigation structure updated with new narrative flow
- [x] New route pages created with placeholder content
- [x] Landing page cards updated to match new structure
- [x] Foundation set for content migration

### **Next: Landing Page Content Refactor**
- Update hero section with narrative hook
- Revise messaging to focus on acoustic indices innovation
- Add context about MBON funding and broader impact

---

*Last updated: 2025-09-19 - Phase 1 (Navigation) Complete*
