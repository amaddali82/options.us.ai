# Trading Intelligence UI

React-based frontend for viewing trading recommendations with detailed analysis.

## Features

- **Dashboard**: Table view with filters (horizon, confidence, symbol search, sort)
- **Recommendation Drawer**: Detailed view with targets, options, rationale, and quality metrics
- **Performance**: Virtual scrolling for 200+ rows using react-window
- **Data Fetching**: React Query with intelligent caching
- **Styling**: Tailwind CSS with minimal, elegant design

## Tech Stack

- **React 18** + **TypeScript**
- **Vite** - Fast build tool
- **Tailwind CSS** - Utility-first styling
- **React Query** - Server state management
- **react-window** - Virtualized list rendering

## Getting Started

### Prerequisites

- Node.js 18+ 
- npm or yarn

### Installation

```bash
cd services/ui
npm install
```

### Configuration

Create `.env` file:

```bash
VITE_API_BASE_URL=http://localhost:8000
```

### Development

```bash
npm run dev
```

Runs on http://localhost:3000

### Build

```bash
npm run build
```

Outputs to `dist/` directory.

### Preview Production Build

```bash
npm run preview
```

## Project Structure

```
src/
├── App.tsx                    # Main app component
├── main.tsx                   # Entry point with React Query provider
├── index.css                  # Global styles + Tailwind
├── types.ts                   # TypeScript interfaces
├── api.ts                     # API client with typed functions
├── FiltersBar.tsx             # Filters UI (horizon/confidence/symbol/sort)
├── RecommendationsTable.tsx   # Table with virtualization
└── RecommendationDrawer.tsx   # Side drawer with full details
```

## Components

### FiltersBar

Provides filtering controls:
- Horizon dropdown (all/intraday/swing/position)
- Min confidence slider (0-100%)
- Symbol search (debounced)
- Sort dropdown (rank/confidence/time)
- Clear filters button

### RecommendationsTable

Displays recommendations in a table:
- Auto-enables virtualization for 200+ rows
- Shows: symbol, side, horizon, entry, TP1, TP2, move%, confidence, option summary, rank, time
- Click row to open drawer
- Loading and empty states

### RecommendationDrawer

Side panel with full details:
- Key metrics (entry, stop, move%, confidence, rank)
- Price targets with confidence and ETA
- Option strategy (type, strike, expiry, premium, Greeks, IV, option targets)
- Rationale (thesis, catalysts, risks, sentiment, event tags)
- Quality metrics (liquidity, signal strength, data quality, model version)

## API Integration

### Endpoints

- `GET /recommendations` - List view with filters
  - Query params: `horizon`, `min_conf`, `symbol`, `sort`, `limit`, `cursor`
  
- `GET /recommendations/{reco_id}` - Detail view

### Caching

React Query configured with:
- 1-minute stale time
- No refetch on window focus
- Automatic background updates

## Styling

### Design Principles

- **Minimal**: Clean, lots of whitespace
- **Elegant**: Subtle shadows, smooth transitions
- **Compact Pills**: Side/horizon badges using pill components
- **Color Coding**: 
  - BUY = green
  - SELL = red
  - HOLD = gray
  - Intraday = yellow
  - Swing = blue
  - Position = purple

### Custom Classes

```css
.pill              /* Base pill badge */
.pill-buy          /* BUY side */
.pill-sell         /* SELL side */
.pill-hold         /* HOLD side */
.pill-intraday     /* Intraday horizon */
.pill-swing        /* Swing horizon */
.pill-position     /* Position horizon */
```

## Performance Optimizations

1. **Virtualization**: react-window kicks in automatically when rows > 200
2. **Query Caching**: React Query caches responses for 1 minute
3. **Debounced Search**: Symbol search only fires on blur or Enter
4. **Optimistic Updates**: Instant filter changes with background refetch

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `VITE_API_BASE_URL` | API backend URL | `http://localhost:8000` |

## Docker Support

See `docker-compose.yml` in project root for integration with backend services.

## Development Tips

### Hot Module Replacement

Vite provides instant HMR. Changes to components reflect immediately without full page reload.

### TypeScript

All API responses are fully typed. Use IDE autocomplete for confidence.

### Tailwind IntelliSense

Install VS Code extension: `bradlc.vscode-tailwindcss` for class name autocomplete.

## Troubleshooting

### API Connection Error

Check:
1. Backend is running on correct port
2. `.env` has correct `VITE_API_BASE_URL`
3. CORS is enabled in FastAPI

### Build Errors

```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

### TypeScript Errors

```bash
# Check types
npm run build
```

## Future Enhancements

- [ ] Add pagination controls for large datasets
- [ ] Export recommendations to CSV
- [ ] Dark mode toggle
- [ ] Real-time updates via WebSocket
- [ ] Saved filter presets
- [ ] Chart integration for price visualization
- [ ] Mobile responsive improvements

## License

Part of options.usa.ai project.
