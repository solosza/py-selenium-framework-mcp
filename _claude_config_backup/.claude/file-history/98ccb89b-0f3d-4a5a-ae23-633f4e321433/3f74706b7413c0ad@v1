# CLAUDE.md - Embutido-King Landing Page

## Project Overview

Simple, single-page landing site for Embutido-King, a Filipino catering business based in Las Vegas (Southern Highlands area).

**Purpose:** Provide a shareable landing page for Facebook group marketing with clear menu and pricing.

**Status:** Initial Version - Ready for deployment

## Business Context

**Business Name:** Embutido-King
**Contact:** 702.900.1348 (Call or Text)
**Location:** Southern Highlands Area, Las Vegas
**Service:** Filipino catering for events and gatherings
**Target Platform:** Facebook groups (mobile-first audience)

**Delivery:**
- Pickup preferred (Southern Highlands)
- Delivery available with location-dependent fee

## Menu & Pricing

### Specialty
- **Embutido:** $12 each (or $10 each when ordering 4+)

### Noodles
- **Pancit Palabok:** $40 half / $75 full

### Pork
- **Dinuguan:** $50 half / $95 full
- **Pork Adobo:** $45 half / $85 full

### Chicken
- **Chicken Adobo:** $45 half / $85 full
- **Chicken Afritada:** $45 half / $85 full
- **Chicken Curry:** $45 half / $85 full

### Beef
- **Beef Kare Kare:** $60 half / $115 full
- **Beef Mechado:** $60 half / $115 full

### Goat
- **Kalderetang Kambing:** $65 half / $130 full

### Vegetables
- **Pinakbet:** $45 half / $85 full

## Technology Stack

**Frontend:** Pure HTML/CSS (single file)
**Deployment:** GitHub Pages
**Domain:** embutido-king.com (available, not yet registered)

**No frameworks, no build process, no dependencies.**

## Design System

**Color Scheme (Warm & Appetizing):**
- Primary: Deep Red/Maroon (#8B0000, #A52A2A)
- Secondary: Warm Gold/Amber (#DAA520)
- Background: Cream/Light Beige (#FAF3E0)
- Text: Dark Brown (#3E2723)
- Accents: White for cards

**Typography:**
- Font: 'Segoe UI' (system font, cross-platform)
- Mobile-responsive sizing

**Layout:**
- Header: Gradient red background, white text
- CTA: Gold background with large phone number
- Menu: White cards with category grouping and emojis
- Footer: Dark brown with delivery info

## Development Commands

### Local Preview
```bash
python -m http.server 8000
```
Open: http://localhost:8000

### Git Workflow
```bash
git init
git add .
git commit -m "Initial landing page"
git remote add origin <repo-url>
git push -u origin main
```

### GitHub Pages Deployment
1. Push to GitHub
2. Settings > Pages
3. Source: main branch, root folder
4. Site live at: `https://yourusername.github.io/embutido-king/`

## Project Structure

```
embutido-king/
├── index.html          # Single-page landing site (HTML + inline CSS)
├── README.md           # Project documentation
├── CLAUDE.md           # This file (AI assistant guidelines)
└── SESSION.md          # Session state tracking
```

## Code Style & Conventions

**HTML:**
- Semantic HTML5 elements
- Comments for each menu category
- Accessibility: proper heading hierarchy, alt text (when images added)

**CSS:**
- Inline styles in `<style>` tag (single-file approach)
- Mobile-first responsive design
- Flexbox for layout
- Media queries at 768px breakpoint

**Naming:**
- BEM-inspired class names (`.category`, `.menu-item`, `.item-prices`)
- Descriptive, semantic names

## Future Enhancements

**Planned additions:**
- Food images (will be added later)
- Special offerings/seasonal menu
- Order form (optional)
- Gallery section
- Customer testimonials
- Social media links

**When adding images:**
- Create `/images` folder
- Optimize for web (compress, WebP format)
- Use lazy loading
- Add proper alt text

## Design Decisions

### Why Single HTML File?
- Fastest deployment (no build process)
- Easy to maintain (one file to edit)
- Optimal for GitHub Pages
- No dependencies = no version conflicts

### Why Inline CSS?
- Single file = fewer requests = faster load
- No need for CSS file management
- Easier for non-technical edits

### Why No JavaScript?
- Static menu doesn't need interactivity
- Faster page load
- Better SEO
- Works with JS disabled

### Why These Colors?
- Red/gold evoke Filipino flag (subtle cultural connection)
- Warm colors stimulate appetite
- High contrast for mobile readability
- Professional but approachable

## Key Design Patterns

**Mobile-First Responsive Design:**
- Base styles for mobile
- Media queries enhance for desktop
- Touch-friendly tap targets (phone number)

**Progressive Enhancement:**
- Works without images (text-only menu)
- `tel:` link works on mobile, harmless on desktop
- Graceful fallback for older browsers

**Accessibility:**
- Semantic HTML structure
- Color contrast ratio meets WCAG AA
- Scalable text (em/rem units)
- Clickable phone number (mobile)

## Common Tasks

### Update Menu Item
1. Find the category in `index.html`
2. Edit the `.menu-item` section
3. Update prices in `.item-prices`
4. Test locally, then push

### Add New Category
1. Copy a `.category` block
2. Update heading and emoji
3. Add menu items
4. Place in logical order

### Change Colors
1. Search for color hex codes
2. Replace consistently throughout
3. Test contrast (text legibility)

### Add Images
1. Create `images/` folder
2. Optimize images (compress, resize)
3. Add `<img>` tags in appropriate sections
4. Update CSS for image layouts

## Deployment Checklist

- [ ] Test on mobile device (or Chrome DevTools mobile view)
- [ ] Test phone number click-to-call
- [ ] Verify all prices are accurate
- [ ] Check spelling/grammar
- [ ] Test on multiple browsers (Chrome, Safari, Firefox)
- [ ] Push to GitHub
- [ ] Enable GitHub Pages
- [ ] Verify live site works
- [ ] Share link in Facebook group

## Troubleshooting

**Site not loading locally?**
- Check Python server is running: `python -m http.server 8000`
- Try different port: `python -m http.server 3000`
- Check firewall settings

**Phone number not clickable?**
- Works on mobile only (native behavior)
- Desktop shows number but doesn't dial

**GitHub Pages not updating?**
- Clear browser cache
- Wait 5-10 minutes (GitHub Pages rebuild delay)
- Check Settings > Pages for errors

**Colors look different on mobile?**
- Check device color settings (Night Shift, Dark Mode)
- Test on multiple devices
- Adjust hex codes if needed

## Contact & Support

**Business Contact:** 702.900.1348
**Technical Issues:** Check SESSION.md for current work state

---

**Last Updated:** 2025-11-10
**Current Status:** Initial build complete, ready for local preview and deployment
