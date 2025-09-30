# Chango x Aurora-X: Design Guidelines

## Design Approach
**Reference-Based Approach**: Drawing inspiration from high-tech AI interfaces - Linear's precision, Vercel's developer focus, and cinematic UI from Iron Man's JARVIS system. Creating a futuristic, technical aesthetic for an elite autonomous coding platform.

## Core Design Principles
- **Cinematic Tech**: JARVIS-inspired interface with holographic-style elements and precision engineering aesthetics
- **Real-time Intelligence**: Live visualization of Aurora's synthesis process, system health, and code generation
- **Professional Power**: Developer-first design with clear information hierarchy and minimal distractions
- **Resilient Architecture**: Visual indicators for isolated component health and self-healing status

## Color Palette

### Dark Mode (Primary)
- **Background Base**: 220 15% 8% (deep charcoal with subtle blue undertone)
- **Surface Elevated**: 220 15% 12% (slightly lighter panels)
- **Surface Interactive**: 220 15% 15% (hover/active states)

### Accent Colors
- **Primary (Cyan/Tech Blue)**: 195 85% 55% (JARVIS-inspired cyan for AI activity, code synthesis)
- **Success (Emerald)**: 160 75% 50% (Aurora health, passed tests, successful synthesis)
- **Warning (Amber)**: 38 90% 60% (synthesis in progress, optimization alerts)
- **Error (Red)**: 0 75% 58% (failures, critical issues)
- **Secondary (Purple)**: 270 70% 60% (corpus learning, advanced features)

### Text & Borders
- **Text Primary**: 220 15% 95%
- **Text Secondary**: 220 10% 65%
- **Text Muted**: 220 10% 45%
- **Border Subtle**: 220 15% 20%
- **Border Interactive**: 195 60% 40%

## Typography
- **Primary Font**: 'Inter' - clean, technical, excellent for data-dense interfaces
- **Mono Font**: 'JetBrains Mono' - for code snippets, terminal output, technical metrics
- **Display Weight**: 600-700 for headers (strong, authoritative)
- **Body Weight**: 400-500 for content (readable, professional)
- **Code Weight**: 400 (optimal for syntax highlighting)

## Layout System
**Tailwind Spacing Primitives**: 2, 4, 6, 8, 12, 16, 24 units
- Micro spacing: 2 (8px) - tight element grouping
- Standard spacing: 4-6 (16-24px) - component padding, gaps
- Section spacing: 12-16 (48-64px) - major layout divisions
- Hero/Dashboard spacing: 24 (96px) - dramatic visual breaks

## Component Library

### Navigation
- **Top Bar**: Fixed header with Chango logo, system status indicators (Aurora health, active synthesis count), user avatar
- **Sidebar**: Collapsible navigation with icon + text for Chat, Code Library, Aurora Dashboard, Corpus Explorer, Settings
- **Breadcrumbs**: For deep navigation in code library and corpus data

### Chat Interface (JARVIS-style)
- **Message Container**: Full-height chat with gradient overlay at top/bottom for depth
- **User Messages**: Right-aligned, subtle surface elevation with cyan accent border
- **AI Responses**: Left-aligned, animated typing indicator, syntax-highlighted code blocks
- **Input Area**: Fixed bottom bar with Monaco editor integration for code-aware input, send button with loading state
- **Quick Actions**: Floating chips for "Generate function", "Analyze code", "Run Aurora synthesis"

### Code Generation Visualization
- **Synthesis Timeline**: Horizontal progress bar showing beam search stages with real-time node expansion
- **Candidate Cards**: Grid of top synthesis candidates with score, AST size, test pass rate
- **Live Metrics**: Real-time counters for iterations, novelty cache hits, cost budget remaining
- **Code Diff Viewer**: Side-by-side comparison of synthesis iterations with syntax highlighting

### Aurora Dashboard
- **System Health Grid**: 2x2 cards showing Aurora status, sandbox security, novelty cache stats, corpus size
- **Activity Graph**: Line chart of synthesis success rate over time
- **Function Library**: Searchable table of synthesized functions with filters for pass rate, complexity
- **Corpus Insights**: Top performing snippets, most common patterns, learning trends

### Data Displays
- **Metric Cards**: Large number displays with sparkline trends, color-coded status indicators
- **Tables**: Sticky headers, row hover highlights, inline actions, sortable columns
- **Code Blocks**: Dark syntax highlighting with copy button, line numbers, language badge
- **JSON Trees**: Collapsible structure for spec files, test results, corpus records

### Overlays & Modals
- **Code Preview Modal**: Full-screen code viewer with tabs for source, tests, execution output
- **Spec Builder**: Multi-step form for creating Aurora specs with live preview
- **Error Inspector**: Detailed failure analysis with stack traces, symbolic debugging hints
- **Corpus Query**: Advanced search interface for historical synthesis data

## Unique Visual Elements

### JARVIS-Inspired Effects
- **Scanning Lines**: Subtle animated horizontal lines on active synthesis panels
- **Glow Effects**: Cyan glow on active AI responses and running synthesis processes
- **Data Streams**: Animated code/text streams in background of dashboard (low opacity)
- **Holographic Borders**: Gradient borders with subtle animation on critical components

### Status Indicators
- **Pulsing Dots**: For active Aurora processes (cyan pulse for synthesis, green for healthy)
- **Progress Rings**: Circular progress for test execution, synthesis iterations
- **Health Bars**: Color-coded bars for component isolation status, budget consumption
- **Badge Notifications**: Unread corpus insights, completed syntheses, system alerts

## Interaction Patterns
- **Hover**: Subtle scale (1.02) and glow on interactive cards, border color transition on inputs
- **Click/Active**: Brief scale down (0.98) with increased glow intensity
- **Loading**: Skeleton screens with shimmer effect, progress indicators for long operations
- **Transitions**: 200ms ease-in-out for most interactions, 300ms for complex animations
- **Focus**: Prominent cyan ring (2px solid) for keyboard navigation

## Images & Visual Assets
**Hero Section**: Large cinematic background showing abstract neural network/code visualization with holographic overlay (cyan/purple gradient) - communicates AI intelligence and code synthesis
**Dashboard Background**: Subtle grid pattern with glowing nodes, representing Aurora's knowledge graph
**Empty States**: Illustrations of code synthesis process, friendly but technical style

## Accessibility
- High contrast text (WCAG AAA where possible)
- Focus indicators on all interactive elements
- Screen reader labels for complex visualizations
- Keyboard shortcuts overlay (press '?' to show)
- Reduced motion support for users with vestibular disorders

## Responsive Strategy
- **Desktop (1280px+)**: Full dashboard with sidebar, multi-column layouts, side-by-side code comparisons
- **Tablet (768-1279px)**: Collapsible sidebar, stacked code views, scrollable metric grids
- **Mobile (320-767px)**: Bottom navigation, full-width chat, swipeable synthesis candidates

## Key Design Differentiators
- Real-time synthesis visualization (unique to Aurora integration)
- JARVIS-inspired AI conversation interface (cinematic, powerful)
- Isolated component health monitoring (visual system architecture)
- Persistent corpus learning visualization (shows AI improvement over time)
- Developer-centric code-first interactions throughout