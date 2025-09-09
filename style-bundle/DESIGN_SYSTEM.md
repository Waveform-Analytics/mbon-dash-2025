# MBON Marine Biodiversity Dashboard - Design System

## Overview

The MBON Dashboard follows a **clean, minimal, scientific** design philosophy with a focus on data clarity and accessibility. The design system emphasizes readability, consistency, and a calming marine-inspired aesthetic that supports the project's research context.

---

## Design Philosophy

### Core Principles
- **Minimal & Clean**: White backgrounds, subtle borders, generous whitespace
- **Scientific Credibility**: Professional typography, structured layouts, clear data hierarchy  
- **Marine-Inspired**: Teal-based color palette reflecting ocean themes
- **Accessibility First**: High contrast, semantic colors, keyboard navigation
- **Data-Focused**: Design serves the data, not the other way around

---

## Color System

### Primary Colors
Based on CSS custom properties defined in `src/app/globals.css`:

```css
:root {
  --primary: #0f766e;           /* Primary teal - main brand color */
  --primary-foreground: #ffffff; /* White text on primary */
  --background: #ffffff;         /* Clean white background */
  --foreground: oklch(0.145 0 0); /* Near-black text */
}
```

### Chart Colors
Consistent data visualization palette:

```css
--chart-1: #14b8a6;  /* Teal - primary data color */
--chart-2: oklch(0.6 0.118 184.704); /* Blue-teal */
--chart-3: #0891b2;  /* Cyan-blue */
--chart-4: oklch(0.828 0.189 84.429); /* Warm accent */
--chart-5: #0f766e;  /* Primary teal variant */
```

### Semantic Colors
```css
--card: #ffffff;                    /* Card backgrounds */
--card-foreground: oklch(0.145 0 0); /* Card text */
--muted: #ececf0;                   /* Subtle backgrounds */
--muted-foreground: #717182;        /* Secondary text */
--accent: #e6fffa;                  /* Light teal accent */
--accent-foreground: #0f766e;       /* Accent text */
--secondary: oklch(0.95 0.0058 264.53); /* Light neutral */
--border: rgba(0, 0, 0, 0.1);       /* Subtle borders */
```

### Color Usage Guidelines

#### Primary Actions
```tsx
// Primary buttons and key actions
className="bg-primary text-primary-foreground hover:bg-primary/90"
```

#### Data Visualization
```tsx
// Use chart colors for icons and data representations
className="text-chart-1" // Primary data
className="text-chart-2" // Secondary data  
className="text-chart-3" // Tertiary data
```

#### Text Hierarchy
```tsx
className="text-foreground"        // Primary headings and body text
className="text-muted-foreground"  // Secondary text, descriptions
className="text-card-foreground"   // Text within cards
```

---

## Typography

### Font System
Using system fonts for performance and reliability:

```css
--font-sans: var(--font-geist-sans);  /* Primary UI font */
--font-mono: var(--font-geist-mono);  /* Code and data font */
```

### Typography Scale
Defined in `globals.css` with consistent hierarchy:

```css
h1 { font-size: var(--text-2xl); font-weight: var(--font-weight-medium); }
h2 { font-size: var(--text-xl); font-weight: var(--font-weight-medium); }
h3 { font-size: var(--text-lg); font-weight: var(--font-weight-medium); }
h4 { font-size: var(--text-base); font-weight: var(--font-weight-medium); }
p { font-size: var(--text-base); font-weight: var(--font-weight-normal); }
```

### Typography Usage Examples
```tsx
// Page titles
<h1 className="text-4xl md:text-6xl font-bold text-foreground">

// Section headings  
<h2 className="text-3xl font-bold text-foreground">

// Card titles
<h3 className="text-lg font-semibold text-card-foreground">

// Body text
<p className="text-muted-foreground leading-relaxed">

// Descriptions
<p className="text-sm text-muted-foreground">
```

---

## Layout System

### Container & Spacing
```tsx
// Page containers
<div className="container mx-auto px-4">
<div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">

// Section spacing
<section className="py-16 px-4 sm:px-6 lg:px-8">

// Card spacing
<div className="space-y-4">        // Vertical stack
<div className="flex gap-6">       // Horizontal flex
```

### Grid Systems
```tsx
// Responsive cards
<div className="grid grid-cols-1 md:grid-cols-3 gap-8">

// Navigation items  
<div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
```

---

## Component Library

### Core UI Components

#### Card System
**Location**: `src/components/ui/card.tsx`

Complete card component system with semantic structure:

```tsx
import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from '@/components/ui/card';

<Card className="shadow-lg border">
  <CardHeader>
    <CardTitle>Chart Title</CardTitle>
    <CardDescription>Description of the visualization</CardDescription>
  </CardHeader>
  <CardContent>
    {/* Chart or content goes here */}
  </CardContent>
</Card>
```

**Default Styling**: 
- `bg-card text-card-foreground`
- `rounded-xl border shadow-sm`
- `flex flex-col gap-6`

#### VisualizationCard
**Location**: `src/components/ui/VisualizationCard.tsx`

Specialized card for data visualizations with loading states:

```tsx
import VisualizationCard from '@/components/ui/VisualizationCard';
import { BarChart3 } from 'lucide-react';

<VisualizationCard
  title="Acoustic Indices Analysis"
  description="Correlation patterns across marine stations"
  icon={BarChart3}
  iconColor="text-chart-1"
  loading={isLoading}
  error={error}
>
  {/* Visualization component */}
</VisualizationCard>
```

**Features**:
- Built-in loading states with spinner
- Error handling with user-friendly messages  
- Consistent icon placement and styling
- Semantic color support

#### NarrativeSection
**Location**: `src/components/ui/NarrativeSection.tsx`

Contextual information blocks with animation:

```tsx
import NarrativeSection from '@/components/ui/NarrativeSection';

<NarrativeSection
  title="Key Insight"
  emoji="🔍"
  variant="insight"
  delay={0.3}
>
  <p>This analysis reveals important patterns in the acoustic data...</p>
</NarrativeSection>
```

**Variants**:
- `info`: Blue theme for general information
- `insight`: Green theme for discoveries  
- `tip`: Purple theme for helpful hints
- `warning`: Yellow theme for important notes

### Layout Components

#### Navigation
**Location**: `src/components/layout/Navigation.tsx`

Sticky navigation with backdrop blur and active states:

```tsx
// Automatic implementation - no import needed
// Features:
// - Animated Waves logo
// - Active tab indicators with layoutId animation
// - Responsive mobile/desktop layouts  
// - Backdrop blur with transparency
```

**Key Features**:
- `bg-background/60 backdrop-blur-md backdrop-saturate-150`
- Framer Motion animations for logo and active states
- Responsive tooltips for mobile
- Semantic navigation structure

---

## Animation System

### Motion Library
Using **Framer Motion** for all animations:

```tsx
import { motion } from 'framer-motion';

// Page entrance animations
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6, delay: 0.1 }}
>

// Hover animations
<motion.div
  whileHover={{ scale: 1.02, y: -2 }}
  transition={{ type: "spring", stiffness: 300, damping: 20 }}
>

// Logo animation
<motion.div
  animate={{ rotateY: [0, 15, 0, -15, 0] }}
  transition={{
    duration: 6,
    repeat: Infinity,
    ease: "easeInOut"
  }}
>
  <Waves className="h-6 w-6 text-primary" />
</motion.div>
```

### Animation Patterns
- **Page Load**: Staggered fade-in with upward motion
- **Card Hover**: Subtle scale and lift effects
- **Navigation**: Layout animations for active states
- **Logo**: Continuous subtle rotation
- **Loading States**: Smooth spinner with accompanying text

---

## Icon System

### Icon Library
Using **Lucide React** for all icons:

```tsx
import { Waves, BarChart3, Map, Beaker } from 'lucide-react';

// Consistent sizing
<Waves className="h-6 w-6 text-primary" />      // Standard
<BarChart3 className="h-4 w-4 text-chart-1" />  // Small  
<Map className="h-8 w-8 text-chart-3" />        // Large
```

### Icon Usage Guidelines
- **Navigation**: 4x4 (`h-4 w-4`)
- **Cards**: 6x6 (`h-6 w-6`) 
- **Hero Sections**: 8x8 (`h-8 w-8`)
- **Large Features**: 12x12 (`h-12 w-12`)

### Common Icons
```tsx
// Brand/Navigation
import { Waves, Home, BarChart3 } from 'lucide-react';

// Data/Analysis  
import { Map, TrendingUp, Activity, FileText } from 'lucide-react';

// UI States
import { Loader2, AlertCircle, CheckCircle } from 'lucide-react';

// Scientific
import { Beaker, MapPin } from 'lucide-react';
```

---

## Responsive Design

### Breakpoint Strategy
Following Tailwind CSS defaults:

```tsx
// Mobile First approach
<div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4">

// Text scaling
<h1 className="text-4xl md:text-5xl lg:text-6xl">

// Spacing adjustments  
<section className="py-12 md:py-16 lg:py-24">
```

### Key Breakpoints
- **sm**: 640px - Small tablets
- **md**: 768px - Tablets  
- **lg**: 1024px - Laptops
- **xl**: 1280px - Desktops

### Mobile Considerations
- Navigation collapses to icons with tooltips
- Cards stack vertically
- Hero text scales down appropriately
- Touch targets are minimum 44px

---

## File Structure

### Style Files
```
dashboard/src/
├── app/
│   └── globals.css           # CSS custom properties, base styles
├── components/
│   ├── ui/                   # Reusable UI components
│   │   ├── card.tsx         # Complete card system
│   │   ├── VisualizationCard.tsx # Data viz wrapper
│   │   └── NarrativeSection.tsx  # Content blocks
│   └── layout/              # Layout components
│       └── Navigation.tsx   # Main navigation
└── lib/
    └── utils.ts             # Utility functions (cn, etc.)
```

### Dependencies
Key design-related packages from `package.json`:

```json
{
  "tailwindcss": "^4",           // Utility-first CSS
  "framer-motion": "^12.23.12",  // Animation library
  "lucide-react": "^0.542.0",    // Icon system
  "class-variance-authority": "^0.7.1", // Component variants
  "tailwind-merge": "^3.3.1",    // Conditional classes
  "clsx": "^2.1.1"               // Class name utility
}
```

---

## Usage Examples

### Creating a New Page
```tsx
import { motion } from 'framer-motion';
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';

export default function NewPage() {
  return (
    <div className="min-h-screen bg-background">
      {/* Hero with ocean background */}
      <section className="relative text-primary-foreground pb-24 pt-8 overflow-hidden">
        <div 
          className="absolute inset-0 bg-cover bg-center bg-no-repeat"
          style={{ backgroundImage: `url('/images/yohan-marion-daufuskie-unsplash.jpg')` }}
        >
          <div className="absolute inset-0 bg-gradient-to-br from-primary/70 via-primary/60 to-chart-3/65" />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 relative">
          <motion.div
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
          >
            <h1 className="text-4xl md:text-6xl font-bold text-primary-foreground mb-6">
              Page Title
            </h1>
          </motion.div>
        </div>
      </section>

      {/* Content Section */}
      <section className="py-16 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
          >
            <Card className="shadow-lg border">
              <CardHeader>
                <div className="flex items-center gap-3">
                  <div className="p-2 bg-primary/10 rounded-lg">
                    <BarChart3 className="h-6 w-6 text-chart-1" />
                  </div>
                  <div>
                    <CardTitle>Section Title</CardTitle>
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                {/* Content goes here */}
              </CardContent>
            </Card>
          </motion.div>
        </div>
      </section>
    </div>
  );
}
```

### Adding a Data Visualization
```tsx
import VisualizationCard from '@/components/ui/VisualizationCard';
import { TrendingUp } from 'lucide-react';

<VisualizationCard
  title="Species Detection Patterns"
  description="Temporal analysis of marine life across stations"  
  icon={TrendingUp}
  iconColor="text-chart-2"
  loading={isLoading}
  error={error}
>
  {/* Your chart component here */}
  <YourChartComponent data={chartData} />
</VisualizationCard>
```

---

## Best Practices

### Color Usage
1. **Stick to the palette** - Use defined CSS custom properties
2. **Semantic naming** - Use `text-foreground`, not specific color values
3. **Chart consistency** - Use chart-1 through chart-5 for data visualization
4. **Accessibility** - Ensure sufficient contrast ratios

### Typography
1. **Hierarchy** - Use consistent heading levels (h1 → h2 → h3)
2. **Responsive sizing** - Include mobile, tablet, desktop sizes
3. **Line height** - Use `leading-relaxed` for body text
4. **Font weights** - Medium for headings, normal for body

### Spacing
1. **Consistent gaps** - Use Tailwind's spacing scale (4, 6, 8, 12, 16, 24)
2. **Section padding** - `py-16` for major sections
3. **Card spacing** - `space-y-4` for internal card content
4. **Container margins** - `max-w-7xl mx-auto` for content width

### Components
1. **Reuse existing** - Check `/components/ui/` before creating new
2. **Props interface** - Always type component props with TypeScript
3. **Default values** - Provide sensible defaults for optional props
4. **Accessibility** - Include proper ARIA labels and keyboard support

### Animation
1. **Subtle motion** - Keep animations purposeful, not distracting
2. **Consistent timing** - Use similar duration/delay patterns
3. **Performance** - Animate transforms and opacity, avoid layout changes
4. **Respect preferences** - Consider `prefers-reduced-motion`

---

## Future Considerations

### Planned Additions
- Button component system
- Form input components  
- Modal/dialog system
- Toast notification system
- Data table components

### Scalability
- Consider CSS-in-JS for complex component variants
- Evaluate design token system for larger teams
- Plan for dark mode support if needed
- Document component composition patterns

---

This design system serves as the foundation for consistent, accessible, and maintainable UI development across the MBON Marine Biodiversity Dashboard. All new components and pages should follow these established patterns and principles.