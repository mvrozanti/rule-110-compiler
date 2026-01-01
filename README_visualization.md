# Rule 110 Universal Computation Visualization

## File Structure

### `rule110_universality_demo.html`
Main HTML file containing:
- UI layout and controls
- CSS styling
- External JavaScript reference

### `rule110_visualization.js`
Separated JavaScript file containing:
- Canvas rendering logic
- Event handling (pan, zoom, controls)
- Data fetching and processing
- Visualization state management

## Benefits of Separation

1. **Maintainability**: Smaller, focused files are easier to debug
2. **Readability**: HTML focuses on structure, JS focuses on logic
3. **Reusability**: JS can be reused in other demos
4. **Debugging**: Syntax errors are isolated to specific files
5. **Development**: Can work on UI and logic separately

## Key Components

### Canvas Visualization
- **Input regions**: Green highlighting (step 0)
- **Output regions**: Orange highlighting (final step)
- **Gliders**: Yellow highlighting for those reaching output
- **Pan & zoom**: Mouse controls for navigation

### Interactive Controls
- **Program input**: Auto-compiles on typing
- **Visibility toggles**: Checkboxes for input/output regions
- **Compile button**: Manual compilation trigger

### Data Flow
1. User enters Brainfuck program
2. Auto-compilation sends to `/compile` endpoint
3. Server returns evolution history, regions, and glider tracks
4. JavaScript renders visualization with proper coloring

## Development Workflow

1. **HTML changes**: Edit `rule110_universality_demo.html`
2. **Logic changes**: Edit `rule110_visualization.js`
3. **Test**: Open HTML file in browser, check console for errors
4. **Debug**: Use browser dev tools to inspect specific functions

## Current Features

- ✅ Modular file structure
- ✅ Auto-compilation on input
- ✅ Pan and zoom controls
- ✅ Region highlighting with toggles
- ✅ Glider visualization
- ✅ Error handling and status display

## Future Improvements

- Add more visualization options
- Implement different coloring schemes
- Add animation controls
- Create additional demo variations




