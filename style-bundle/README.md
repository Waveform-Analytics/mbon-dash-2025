# MBON Design System Bundle

This bundle contains all the essential files needed to reproduce the MBON Marine Biodiversity Dashboard design system in a new project.

## 📁 Bundle Contents

### Core Design Files
- `DESIGN_SYSTEM.md` - Complete design system documentation
- `globals.css` - CSS custom properties and base styles

### Components
- `components/ui/card.tsx` - Complete card component system
- `components/ui/VisualizationCard.tsx` - Data visualization wrapper
- `components/ui/NarrativeSection.tsx` - Content blocks with variants
- `components/layout/Navigation.tsx` - Animated navigation component

### Configuration
- `config/next.config.ts` - Next.js configuration
- `config/postcss.config.mjs` - PostCSS configuration
- `config/tsconfig.json` - TypeScript configuration
- `config/package-dependencies.json` - Essential NPM dependencies

### Utilities & Assets
- `lib/utils.ts` - Utility functions (cn, etc.)
- `images/yohan-marion-daufuskie-unsplash.jpg` - Hero background image
- `SampleHeroPage.tsx` - Complete hero page template

## 🚀 Quick Setup

### 1. Install Dependencies
```bash
npm install framer-motion lucide-react class-variance-authority clsx tailwind-merge @radix-ui/react-slot
npm install -D @tailwindcss/postcss tailwindcss
```

### 2. Copy Files to New Project
```bash
# Core files
cp globals.css ./src/app/
cp lib/utils.ts ./src/lib/
cp -r components/ ./src/

# Configuration (adjust paths as needed)
cp config/next.config.ts ./
cp config/postcss.config.mjs ./
cp config/tsconfig.json ./

# Assets
mkdir -p public/images
cp images/yohan-marion-daufuskie-unsplash.jpg ./public/images/
```

### 3. Update Your Layout
```tsx
// app/layout.tsx
import './globals.css'

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Navigation />
        {children}
      </body>
    </html>
  )
}
```

### 4. Use the Sample Hero Page
Copy `SampleHeroPage.tsx` to your project and customize:
- Replace hero title and description
- Update background image path if needed
- Modify feature cards content
- Adjust gradient overlay colors

## 🎨 Design System Highlights

### Color Palette
- **Primary**: `#0f766e` (Teal)
- **Chart Colors**: 5-color data visualization palette
- **Semantic Colors**: Background, foreground, muted, accent variations

### Typography
- **Font**: Geist Sans (system fonts)
- **Scale**: Consistent hierarchy with proper line heights
- **Weights**: Medium for headings, normal for body text

### Components
- **Cards**: Flexible card system with header, content, footer
- **VisualizationCard**: Built-in loading states and error handling
- **NarrativeSection**: 4 variants (info, insight, tip, warning)
- **Navigation**: Animated logo and active state indicators

### Animations
- **Library**: Framer Motion for all animations
- **Patterns**: Staggered entrance, hover effects, layout animations
- **Performance**: GPU-accelerated transforms and opacity

## 📋 Customization Checklist

### Hero Section
- [ ] Replace hero background image
- [ ] Update hero title and description
- [ ] Modify gradient overlay colors
- [ ] Adjust call-to-action button text and link

### Brand Colors
- [ ] Update `--primary` color in globals.css
- [ ] Adjust chart color palette if needed
- [ ] Modify gradient overlays to match brand

### Content
- [ ] Replace feature card icons and descriptions
- [ ] Update navigation menu items
- [ ] Customize loading and error messages

### Components
- [ ] Add your own component variants
- [ ] Extend color system for new use cases
- [ ] Create additional layout patterns

## 🎯 Key Features

### Responsive Design
- Mobile-first approach
- Breakpoints: sm (640px), md (768px), lg (1024px), xl (1280px)
- Touch-friendly interactions

### Accessibility
- High contrast color ratios
- Semantic HTML structure
- Keyboard navigation support
- Screen reader friendly

### Performance
- Optimized animations (transforms + opacity)
- Efficient CSS custom properties
- Progressive enhancement

### Developer Experience
- TypeScript support throughout
- Comprehensive component props
- Consistent naming conventions
- Clear documentation

## 🔧 Advanced Usage

### Extending Components
```tsx
// Create new card variants
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'

<Card className="border-chart-1 shadow-lg">
  <CardHeader>
    <CardTitle>Custom Card</CardTitle>
  </CardHeader>
  <CardContent>
    Your content here
  </CardContent>
</Card>
```

### Custom Color Schemes
```css
/* Add to globals.css */
:root {
  --chart-6: #your-color;
  --custom-accent: #your-brand-color;
}
```

### Animation Patterns
```tsx
// Consistent animation timing
<motion.div
  initial={{ opacity: 0, y: 20 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.6, delay: 0.2 }}
>
```

## 📚 Reference

- **Design Documentation**: See `DESIGN_SYSTEM.md` for complete details
- **Component Examples**: Check `SampleHeroPage.tsx` for usage patterns
- **Color System**: All colors defined in `globals.css`
- **Animation Library**: [Framer Motion Documentation](https://www.framer.com/motion/)
- **Icons**: [Lucide React Icons](https://lucide.dev/)

## 🆘 Troubleshooting

### Common Issues
1. **Missing dependencies**: Check `package-dependencies.json` for required packages
2. **CSS not loading**: Ensure `globals.css` is imported in your root layout
3. **TypeScript errors**: Copy the provided `tsconfig.json` configuration
4. **Icons not showing**: Install `lucide-react` package

### Getting Help
- Review the complete `DESIGN_SYSTEM.md` documentation
- Check component prop interfaces in TypeScript files
- Ensure all file paths match your project structure

---

**Happy building!** This design system provides a solid foundation for creating beautiful, accessible, and performant web applications with a marine-inspired aesthetic.