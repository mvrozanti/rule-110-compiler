/**
 * Rule 110 Universal Computation Visualization
 * Separated JavaScript for better maintainability
 */

console.log('Rule 110 visualization script loaded');

// Global state
let currentHistory = null;
let currentRegions = {};
let currentGliderTracks = [];
let panX = -150;  // Start panned to show encoding section (cells 100-200)
let panY = 0;
let zoom = 0.8;   // Slightly zoomed out to see more

// Cache for compiled programs
const compilationCache = {};

// WebGL rendering context
let gl = null;
let program = null;
let positionBuffer = null;
let texture = null;
let textureWidth = 0;
let textureHeight = 0;

// Helper function
function sum(arr) {
    return arr.reduce((a, b) => a + b, 0);
}
let isDragging = false;
let dragStartX = 0;
let dragStartY = 0;

// WebGL shader sources
const vertexShaderSource = `
    attribute vec2 a_position;
    uniform vec2 u_resolution;
    uniform vec2 u_pan;
    uniform float u_zoom;
    uniform vec2 u_textureSize;

    varying vec2 v_texCoord;

    void main() {
        // Convert from pixels to 0.0 to 1.0
        vec2 zeroToOne = a_position / u_resolution;

        // Convert from 0->1 to 0->2
        vec2 zeroToTwo = zeroToOne * 2.0;

        // Convert from 0->2 to -1->+1 (clipspace)
        vec2 clipSpace = zeroToTwo - 1.0;

        gl_Position = vec4(clipSpace * vec2(1, -1), 0, 1);

        // Calculate texture coordinates with pan and zoom
        v_texCoord = (a_position - u_pan) / (u_textureSize * u_zoom);
    }
`;

const fragmentShaderSource = `
    precision mediump float;

    uniform sampler2D u_texture;
    uniform vec2 u_textureSize;
    uniform vec2 u_inputRegionStart;
    uniform vec2 u_inputRegionEnd;
    uniform vec2 u_outputRegionStart;
    uniform vec2 u_outputRegionEnd;
    uniform float u_step;

    varying vec2 v_texCoord;

    void main() {
        vec2 texCoord = v_texCoord;

        // Outside texture bounds = transparent
        if (texCoord.x < 0.0 || texCoord.x > 1.0 || texCoord.y < 0.0 || texCoord.y > 1.0) {
            gl_FragColor = vec4(0.0, 0.0, 0.0, 0.0);
            return;
        }

        // Sample the texture
        vec4 texColor = texture2D(u_texture, texCoord);

        // Determine cell type based on texture value
        float cellValue = texColor.r; // Red channel contains cell state
        float cellType = texColor.g;  // Green channel contains cell type info

        vec3 color;

        // Input region (step 0, special highlighting)
        if (u_step < 0.5 && texCoord.x >= u_inputRegionStart.x && texCoord.x < u_inputRegionEnd.x) {
            color = vec3(0.0, 1.0, 0.0); // Bright green
        }
        // Output region (last step, special highlighting)
        else if (u_step > u_textureSize.y - 1.5 && texCoord.x >= u_outputRegionStart.x && texCoord.x < u_outputRegionEnd.x) {
            color = vec3(1.0, 0.6, 0.0); // Orange
        }
        // Regular cells
        else {
            color = cellValue > 0.5 ? vec3(1.0, 1.0, 1.0) : vec3(0.067, 0.067, 0.067); // White or dark gray
        }

        gl_FragColor = vec4(color, 1.0);
    }
`;

// WebGL utility functions
function createShader(gl, type, source) {
    const shader = gl.createShader(type);
    gl.shaderSource(shader, source);
    gl.compileShader(shader);
    if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error('Shader compile error:', gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
    }
    return shader;
}

function createProgram(gl, vertexShader, fragmentShader) {
    const program = gl.createProgram();
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);
    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
        console.error('Program link error:', gl.getProgramInfoLog(program));
        gl.deleteProgram(program);
        return null;
    }
    return program;
}

function initWebGL() {
    const canvas = document.getElementById('matrix-canvas');
    gl = canvas.getContext('webgl') || canvas.getContext('experimental-webgl');

    if (!gl) {
        console.error('WebGL not supported, falling back to Canvas 2D');
        return false;
    }

    // Create shaders
    const vertexShader = createShader(gl, gl.VERTEX_SHADER, vertexShaderSource);
    const fragmentShader = createShader(gl, gl.FRAGMENT_SHADER, fragmentShaderSource);

    if (!vertexShader || !fragmentShader) {
        console.error('Failed to create shaders');
        return false;
    }

    // Create program
    program = createProgram(gl, vertexShader, fragmentShader);
    if (!program) {
        console.error('Failed to create program');
        return false;
    }
    gl.useProgram(program);

    // Create position buffer for full-screen quad
    positionBuffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
    const positions = [
        0, 0,
        canvas.width, 0,
        0, canvas.height,
        0, canvas.height,
        canvas.width, 0,
        canvas.width, canvas.height,
    ];
    gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);

    // Set up attributes and uniforms
    const positionAttributeLocation = gl.getAttribLocation(program, 'a_position');
    gl.enableVertexAttribArray(positionAttributeLocation);
    gl.vertexAttribPointer(positionAttributeLocation, 2, gl.FLOAT, false, 0, 0);

    // Set resolution uniform
    const resolutionUniformLocation = gl.getUniformLocation(program, 'u_resolution');
    gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);

    console.log('WebGL initialized successfully');
    // Update debug info to show WebGL status
    const debugInfo = document.getElementById('debug-info');
    if (debugInfo) {
        const existingText = debugInfo.textContent;
        const webglText = existingText ? existingText + ' | WebGL: ✓' : 'WebGL: ✓';
        debugInfo.textContent = webglText;
    }
    return true;
}

// Performance optimization: throttle drawing during interactions
let drawRequested = false;
function requestDraw() {
    if (!drawRequested) {
        drawRequested = true;
        requestAnimationFrame(() => {
            drawMatrix();
            drawRequested = false;
        });
    }
}

// Visibility toggles
let showInputRegions = true;
let showOutputRegions = true;

// Canvas and context
let canvas, ctx, container;

// Example programs loader
function loadExample() {
    const select = document.getElementById('examples');
    const program = select.value;
    if (program) {
        document.getElementById('program-input').value = program;
        compile();
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    canvas = document.getElementById('matrix-canvas');
    container = document.getElementById('matrix-container');

    // Try WebGL first, fallback to Canvas 2D
    const webglSuccess = initWebGL();
    if (!webglSuccess) {
        // Fallback to Canvas 2D
        ctx = canvas.getContext('2d');
        if (!ctx) {
            console.error('Canvas 2D context not available');
            return;
        }
        console.log('Using Canvas 2D fallback');
        // Update debug info to show fallback status
        const debugInfo = document.getElementById('debug-info');
        if (debugInfo) {
            const existingText = debugInfo.textContent;
            const canvasText = existingText ? existingText + ' | Canvas 2D: ✓' : 'Canvas 2D: ✓';
            debugInfo.textContent = canvasText;
        }
    }

    // Initialize button state
    const compileBtn = document.getElementById('compile-btn');
    compileBtn.disabled = false;
    compileBtn.classList.remove('loading');

    // Initialize cache info
    updateCacheInfo();

    // Resize canvas
    function resizeCanvas() {
        const newWidth = container.clientWidth;
        const newHeight = container.clientHeight;

        if (canvas.width !== newWidth || canvas.height !== newHeight) {
            canvas.width = newWidth;
            canvas.height = newHeight;

            // Update WebGL viewport if using WebGL
            if (gl) {
                gl.viewport(0, 0, canvas.width, canvas.height);

                // Update resolution uniform
                const resolutionUniformLocation = gl.getUniformLocation(program, 'u_resolution');
                gl.uniform2f(resolutionUniformLocation, canvas.width, canvas.height);

                // Recreate position buffer with new canvas size
                const positions = [
                    0, 0,
                    canvas.width, 0,
                    0, canvas.height,
                    0, canvas.height,
                    canvas.width, 0,
                    canvas.width, canvas.height,
                ];
                gl.bindBuffer(gl.ARRAY_BUFFER, positionBuffer);
                gl.bufferData(gl.ARRAY_BUFFER, new Float32Array(positions), gl.STATIC_DRAW);
            }
        }
    }

    // Initial setup
    resizeCanvas();
    requestDraw();

    // Event listeners
    container.addEventListener('mousedown', (e) => {
        isDragging = true;
        container.classList.add('dragging');
        dragStartX = e.clientX - panX;
        dragStartY = e.clientY - panY;
    });

    container.addEventListener('mousemove', (e) => {
        if (isDragging) {
            panX = e.clientX - dragStartX;
            panY = e.clientY - dragStartY;
            requestDraw();
        }
    });

    container.addEventListener('mouseup', () => {
        isDragging = false;
        container.classList.remove('dragging');
    });

    container.addEventListener('mouseleave', () => {
        isDragging = false;
        container.classList.remove('dragging');
    });

    container.addEventListener('wheel', (e) => {
        e.preventDefault();
        const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
        zoom = Math.max(0.1, Math.min(5, zoom * zoomFactor));
        drawMatrix();
    });

    // Window resize
    window.addEventListener('resize', () => {
        resizeCanvas();
        requestDraw();
    });

    // Auto-compile on page load
    const program = document.getElementById('program-input').value.trim();
    if (program) {
        compile();
    }

    // Auto-compile on input change
    document.getElementById('program-input').addEventListener('input', () => {
        const program = document.getElementById('program-input').value.trim();
        if (program) {
            compile();
        }
    });

    // Also compile on Enter (backup)
    document.getElementById('program-input').addEventListener('keypress', (e) => {
        if (e.key === 'Enter') compile();
    });

    // Visibility toggles
    document.getElementById('show-input').addEventListener('change', updateVisibility);
    document.getElementById('show-output').addEventListener('change', updateVisibility);
});

// Compile function
// Cache management functions
function getCachedResult(program) {
    try {
        const cached = localStorage.getItem(`rule110_${program}`);
        return cached ? JSON.parse(cached) : null;
    } catch (error) {
        console.warn('Failed to load from cache:', error);
        return null;
    }
}

function setCachedResult(program, result) {
    try {
        localStorage.setItem(`rule110_${program}`, JSON.stringify(result));
    } catch (error) {
        console.warn('Failed to save to cache:', error);
    }
}

function clearCache() {
    try {
        const keys = Object.keys(localStorage).filter(key => key.startsWith('rule110_'));
        keys.forEach(key => localStorage.removeItem(key));
        console.log(`Cleared ${keys.length} cached compilations`);

        // Update cache info in debug section
        updateCacheInfo();
    } catch (error) {
        console.warn('Failed to clear cache:', error);
    }
}

function getCacheInfo() {
    try {
        const keys = Object.keys(localStorage).filter(key => key.startsWith('rule110_'));
        return {
            count: keys.length,
            programs: keys.map(key => key.replace('rule110_', ''))
        };
    } catch (error) {
        return { count: 0, programs: [] };
    }
}

function updateCacheInfo() {
    const cacheInfo = getCacheInfo();
    const debugInfo = document.getElementById('debug-info');
    if (debugInfo && cacheInfo.count > 0) {
        debugInfo.textContent = `Cache: ${cacheInfo.count} programs (${cacheInfo.programs.join(', ')})`;
    } else if (debugInfo) {
        debugInfo.textContent = '';
    }
}

async function compile() {
    let program = document.getElementById('program-input').value.trim();
    // Default to multiply program to show B-gliders (matches HTML default)
    if (!program) {
        program = '++[>++++++<-]>';
        document.getElementById('program-input').value = program;
    }

    // Check cache first
    const cachedResult = getCachedResult(program);
    if (cachedResult) {
        console.log('Using cached result for program:', program);

        // Disable button and show loading state
        const compileBtn = document.getElementById('compile-btn');
        const status = document.getElementById('status');
        compileBtn.disabled = true;
        compileBtn.classList.add('loading');
        status.textContent = 'Loading from cache...';
        status.className = 'status';

        // Simulate brief loading for UX
        await new Promise(resolve => setTimeout(resolve, 100));

        // Use cached result
        currentHistory = cachedResult.history || [cachedResult.rule110_initial];
        currentRegions = cachedResult.regions || {};
        currentGliderTracks = cachedResult.glider_tracks || [];

        // Display INPUT
        document.getElementById('input-display').textContent = program;

        // Display OUTPUT
        const tmTape = cachedResult.verification?.tm_tape || '?';
        const tmOutput = cachedResult.verification?.tm_output || '';

        let outputDisplay = `Tape: ${tmTape}`;
        if (tmOutput) {
            outputDisplay += ` | Changes tracked: ${tmOutput}`;
        } else {
            outputDisplay += ` | (No output command - result in tape)`;
        }

        document.getElementById('output-display').textContent = outputDisplay;

        // Update decoding section
        updateDecodingSection(cachedResult);

        requestDraw();

        // Show success status
        const encodingActive = sum(currentHistory[0].slice(100, 200));
        status.textContent = `Loaded from cache (${encodingActive} active cells)`;
        status.className = 'status success';

        // Re-enable button
        compileBtn.disabled = false;
        compileBtn.classList.remove('loading');

        // Update cache info
        updateCacheInfo();

        console.log('Loaded from cache successfully');
        return;
    }

    // Disable button and show loading state
    const compileBtn = document.getElementById('compile-btn');
    const status = document.getElementById('status');
    compileBtn.disabled = true;
    compileBtn.classList.add('loading');
    status.textContent = 'Compiling... (may take several seconds)';
    status.className = 'status';

    try {
        console.log('Starting fetch to /compile with program:', program);
        const response = await fetch('/compile', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ program })
        });

        console.log('Fetch response received:', response.status, response.statusText);

        if (!response.ok) throw new Error(`HTTP ${response.status}`);

        const result = await response.json();
        console.log('JSON parsed successfully:', result.program);

        // Display INPUT
        document.getElementById('input-display').textContent = program;

        // Set history, regions, and gliders for matrix
        currentHistory = result.history || [result.rule110_initial];
        currentRegions = result.regions || {};
        currentGliderTracks = result.glider_tracks || [];

        // Display OUTPUT
        const tmTape = result.verification?.tm_tape || '?';
        const tmOutput = result.verification?.tm_output || '';

        // For programs without . command, the result is in the tape
        // Tape "11" might represent cell values, but interpretation depends on encoding
        let outputDisplay = `Tape: ${tmTape}`;
        if (tmOutput) {
            outputDisplay += ` | Changes tracked: ${tmOutput}`;
        } else {
            outputDisplay += ` | (No output command - result in tape)`;
        }

        document.getElementById('output-display').textContent = outputDisplay;

        // Update decoding section
        updateDecodingSection(result);

        // Cache the result for future use
        setCachedResult(program, result);
        updateCacheInfo();

        console.log('About to call drawMatrix()');
        console.log('currentHistory length:', currentHistory ? currentHistory.length : 'null');
        console.log('currentHistory[0] length:', currentHistory && currentHistory[0] ? currentHistory[0].length : 'null');

        requestDraw();

        console.log('drawMatrix() completed');

        // Show encoding section info
        const encodingActive = sum(currentHistory[0].slice(100, 200));
        const statusText = `Ready (encoding: ${encodingActive} active cells)`;
        status.textContent = statusText;
        status.className = 'status success';

        // Re-enable button
        compileBtn.disabled = false;
        compileBtn.classList.remove('loading');

        console.log('Compilation completed successfully');

    } catch (error) {
        console.error('Compilation error:', error);
        status.textContent = `Error: ${error.message}`;
        status.className = 'status error';

        // Re-enable button even on error
        compileBtn.disabled = false;
        compileBtn.classList.remove('loading');
    }
}

// Expose functions globally for HTML onclick/onchange
window.compile = compile;
window.clearCache = clearCache;
window.loadExample = loadExample;
window.updateVisibility = updateVisibility;

// Visibility toggle function
function updateVisibility() {
    showInputRegions = document.getElementById('show-input').checked;
    showOutputRegions = document.getElementById('show-output').checked;
    drawMatrix();
}

// Update decoding section (placeholder)
function updateDecodingSection(result) {
    // This would update the decoding section with result information
    // For now, it's a placeholder
}

// Main drawing function
function drawMatrix() {
    console.log('drawMatrix called');

    if (!currentHistory || currentHistory.length === 0) {
        console.log('No history data, showing placeholder');
        if (gl) {
            // WebGL placeholder
            gl.clearColor(0.4, 0.4, 0.4, 1.0);
            gl.clear(gl.COLOR_BUFFER_BIT);
        } else if (ctx) {
            // Canvas 2D placeholder
            ctx.fillStyle = '#666';
            ctx.font = '16px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('No data. Compile a program to see evolution.', canvas.width / 2, canvas.height / 2);
        }
        return;
    }

    if (gl && program) {
        drawMatrixWebGL();
    } else if (ctx) {
        drawMatrixCanvas2D();
    }
}

// WebGL drawing function
function drawMatrixWebGL() {
    const width = currentHistory[0].length;
    const height = currentHistory.length;

    // Create or update texture
    if (!texture || textureWidth !== width || textureHeight !== height) {
        if (texture) {
            gl.deleteTexture(texture);
        }

        texture = gl.createTexture();
        gl.bindTexture(gl.TEXTURE_2D, texture);

        // Set texture parameters
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_S, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_WRAP_T, gl.CLAMP_TO_EDGE);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MIN_FILTER, gl.NEAREST);
        gl.texParameteri(gl.TEXTURE_2D, gl.TEXTURE_MAG_FILTER, gl.NEAREST);

        textureWidth = width;
        textureHeight = height;
    }

    // Prepare texture data (RGBA format)
    const textureData = new Uint8Array(width * height * 4);

    // Pre-compute input/output region sets for fast lookup
    const inputRegionSet = new Set();
    if (showInputRegions) {
        (currentRegions['input-tape'] || []).forEach(range => {
            for (let x = range.start; x < range.end; x++) {
                inputRegionSet.add(x);
            }
        });
    }

    const outputRegionSet = new Set();
    if (showOutputRegions) {
        (currentRegions['output-tape'] || []).forEach(range => {
            for (let x = range.start; x < range.end; x++) {
                outputRegionSet.add(x);
            }
        });
    }

    // Fill texture data
    for (let y = 0; y < height; y++) {
        const state = currentHistory[y];
        for (let x = 0; x < width; x++) {
            const index = (y * width + x) * 4;
            const cellValue = state[x] ? 255 : 0;

            // Red channel: cell state (0 or 255)
            textureData[index] = cellValue;

            // Green channel: cell type info (for special highlighting)
            let cellType = 0;
            if (y === 0 && inputRegionSet.has(x)) cellType = 1;      // Input region
            else if (y === height - 1 && outputRegionSet.has(x)) cellType = 2; // Output region

            textureData[index + 1] = cellType * 85; // 0, 85, or 170

            // Blue and Alpha channels (unused)
            textureData[index + 2] = 0;
            textureData[index + 3] = 255;
        }
    }

    // Upload texture data
    gl.bindTexture(gl.TEXTURE_2D, texture);
    gl.texImage2D(gl.TEXTURE_2D, 0, gl.RGBA, width, height, 0, gl.RGBA, gl.UNSIGNED_BYTE, textureData);

    // Set uniforms
    const panUniform = gl.getUniformLocation(program, 'u_pan');
    const zoomUniform = gl.getUniformLocation(program, 'u_zoom');
    const textureSizeUniform = gl.getUniformLocation(program, 'u_textureSize');
    const inputRegionStartUniform = gl.getUniformLocation(program, 'u_inputRegionStart');
    const inputRegionEndUniform = gl.getUniformLocation(program, 'u_inputRegionEnd');
    const outputRegionStartUniform = gl.getUniformLocation(program, 'u_outputRegionStart');
    const outputRegionEndUniform = gl.getUniformLocation(program, 'u_outputRegionEnd');

    gl.uniform2f(panUniform, panX, panY);
    gl.uniform1f(zoomUniform, zoom);
    gl.uniform2f(textureSizeUniform, width, height);

    // Set region uniforms (normalized coordinates)
    const inputRange = currentRegions['input-tape']?.[0] || {start: 0, end: 0};
    const outputRange = currentRegions['output-tape']?.[0] || {start: 0, end: 0};

    gl.uniform2f(inputRegionStartUniform, inputRange.start / width, 0);
    gl.uniform2f(inputRegionEndUniform, inputRange.end / width, 1);
    gl.uniform2f(outputRegionStartUniform, outputRange.start / width, 0);
    gl.uniform2f(outputRegionEndUniform, outputRange.end / width, 1);

    // Draw
    gl.viewport(0, 0, canvas.width, canvas.height);
    gl.clearColor(0, 0, 0, 1);
    gl.clear(gl.COLOR_BUFFER_BIT);
    gl.drawArrays(gl.TRIANGLES, 0, 6);

    console.log('WebGL draw completed');
}

// Canvas 2D fallback drawing function
function drawMatrixCanvas2D() {
    console.log('drawMatrix called with canvas 2D fallback');

    // Check if canvas/context are still valid
    if (!canvas || !ctx) {
        console.warn('Canvas or context not available, skipping drawMatrix');
        return;
    }

    try {
        if (!currentHistory || currentHistory.length === 0) {
            ctx.fillStyle = '#666';
            ctx.font = '16px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('No data. Compile a program to see evolution.', canvas.width / 2, canvas.height / 2);
            return;
        }
    } catch (error) {
        console.error('Error in drawMatrix placeholder:', error);
        return;
    }

    console.log('Drawing matrix with history length:', currentHistory.length, 'width:', currentHistory[0].length);

    const cellSize = 3 * zoom;
    const width = currentHistory[0].length;
    const height = currentHistory.length;

    try {
        // Clear canvas
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    } catch (error) {
        console.error('Error clearing canvas:', error);
        return;
    }

    // Apply pan transform
    try {
        ctx.save();
        ctx.translate(panX, panY);

        // Prepare region data
        const inputRegionRanges = [];
        const outputRegionRanges = [];

        if (currentRegions['input-tape']) {
            currentRegions['input-tape'].forEach(range => {
                inputRegionRanges.push({start: range.start, end: range.end});
            });
        }

        if (currentRegions['output-tape']) {
            currentRegions['output-tape'].forEach(range => {
                outputRegionRanges.push({start: range.start, end: range.end});
            });
        }

        // Track gliders that reach output regions
        const glidersReachingOutput = new Set();

        currentGliderTracks.forEach((track, idx) => {
            const startStep = track.start_step;
            const endStep = Math.min(track.end_step, height - 1);

            // Check if glider reaches output region
            for (let step = startStep; step <= endStep; step++) {
                const pos = Math.round(track.start_pos + track.velocity * (step - startStep));
                const inOutputRegion = outputRegionRanges.some(r =>
                    pos >= r.start && pos < r.end
                );
                if (inOutputRegion) {
                    glidersReachingOutput.add(idx);
                    break;
                }
            }
        });

        // Build glider position map for each step
        const gliderPositionsByStep = {};
        currentGliderTracks.forEach((track, idx) => {
            const reachesOutput = glidersReachingOutput.has(idx);

            for (let step = track.start_step; step <= track.end_step && step < height; step++) {
                if (!gliderPositionsByStep[step]) {
                    gliderPositionsByStep[step] = {};
                }
                // Calculate glider position at this step
                const pos = Math.round(track.start_pos + track.velocity * (step - track.start_step));
                if (pos >= 0 && pos < width) {
                    if (!gliderPositionsByStep[step][pos]) {
                        gliderPositionsByStep[step][pos] = [];
                    }
                    gliderPositionsByStep[step][pos].push({
                        type: track.type,
                        reachesOutput: reachesOutput
                    });
                }
            }
        });

        const lastStep = height - 1;

        // Ultra-fast drawing: Process row by row, drawing horizontal runs of same color
        // Performance optimization: when zoomed out, skip every Nth cell for better performance
        const skipFactor = cellSize < 1 ? Math.max(1, Math.floor(1 / cellSize)) : 1;

        for (let step = 0; step < height; step += skipFactor) {
            const state = currentHistory[step];
            const y = step * cellSize;

            // Only process if row is visible
            if (y + panY < -cellSize || y + panY >= canvas.height) continue;

            let currentColor = null;
            let runStart = 0;

            for (let x = 0; x <= width; x++) {
                let color;

                // Determine color for this cell
                if (x < width) {
                    // Input region highlighting (step 0 only)
                    if (step === 0 && inputRegionRanges.some(r => x >= r.start && x < r.end)) {
                        color = '#00ff00'; // Bright green for input
                    }
                    // Output region highlighting (final step only)
                    else if (step === lastStep && outputRegionRanges.some(r => x >= r.start && x < r.end)) {
                        color = '#ff9800'; // Orange for output
                    }
                    // Default cell color
                    else {
                        color = state[x] ? '#fff' : '#111';
                    }
                } else {
                    color = null; // End of row marker
                }

                // If color changed, draw the previous run
                if (color !== currentColor && currentColor !== null) {
                    const cellX = runStart * cellSize;
                    const runWidth = (x - runStart) * cellSize;

                    // Only draw if visible
                    if (cellX + panX < canvas.width && cellX + runWidth + panX > 0) {
                        ctx.fillStyle = currentColor;
                        ctx.fillRect(cellX, y, runWidth, cellSize * skipFactor);
                    }

                    runStart = x;
                }

                currentColor = color;
            }
        }

        // Step markers removed as requested

        // Draw encoding section marker (vertical line at cell 100)
        const markerX = 100 * cellSize;
        if (markerX + panX > 0 && markerX + panX < canvas.width) {
            ctx.strokeStyle = '#ff6b6b';
            ctx.lineWidth = 2;
            ctx.beginPath();
            ctx.moveTo(markerX, 0);
            ctx.lineTo(markerX, canvas.height);
            ctx.stroke();

            // Label the encoding section
            ctx.fillStyle = '#ff6b6b';
            ctx.font = `${12 * zoom}px monospace`;
            ctx.fillText('PROGRAM', markerX + 5, 20);
            ctx.fillText('ENCODING', markerX + 5, 35);
            ctx.fillText('→', markerX + 5, 50);
        }

        ctx.restore();

        // Update stats
        document.getElementById('matrix-stats').textContent =
            `Total gliders: ${currentGliderTracks.length} | Output gliders: ${glidersReachingOutput.size}`;
    } catch (error) {
        console.error('Error drawing matrix:', error);
        // Try to show an error message on canvas if possible
        try {
            ctx.restore();
            ctx.fillStyle = '#ff0000';
            ctx.font = '16px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('Drawing error - refresh page', canvas.width / 2, canvas.height / 2);
        } catch (canvasError) {
            console.error('Canvas error handling failed:', canvasError);
        }
    }
}

    console.log('Drawing matrix with history length:', currentHistory.length, 'width:', currentHistory[0].length);

    const cellSize = 3 * zoom;
    const width = currentHistory[0].length;
    const height = currentHistory.length;

    try {
        // Clear canvas
        ctx.fillStyle = '#000';
        ctx.fillRect(0, 0, canvas.width, canvas.height);
    } catch (error) {
        console.error('Error clearing canvas:', error);
        return;
    }

    // Apply pan transform
    try {
        ctx.save();
        ctx.translate(panX, panY);

        // Prepare region data
    const inputRegionRanges = [];
    const outputRegionRanges = [];

    if (currentRegions['input-tape']) {
        currentRegions['input-tape'].forEach(range => {
            inputRegionRanges.push({start: range.start, end: range.end});
        });
    }

    if (currentRegions['output-tape']) {
        currentRegions['output-tape'].forEach(range => {
            outputRegionRanges.push({start: range.start, end: range.end});
        });
    }

    // Track gliders that reach output regions
    const glidersReachingOutput = new Set();

    currentGliderTracks.forEach((track, idx) => {
        const startStep = track.start_step;
        const endStep = Math.min(track.end_step, height - 1);

        // Check if glider reaches output region
        for (let step = startStep; step <= endStep; step++) {
            const pos = Math.round(track.start_pos + track.velocity * (step - startStep));
            const inOutputRegion = outputRegionRanges.some(r =>
                pos >= r.start && pos < r.end
            );
            if (inOutputRegion) {
                glidersReachingOutput.add(idx);
                break;
            }
        }
    });

    // Build glider position map for each step
    const gliderPositionsByStep = {};
    currentGliderTracks.forEach((track, idx) => {
        const reachesOutput = glidersReachingOutput.has(idx);

        for (let step = track.start_step; step <= track.end_step && step < height; step++) {
            if (!gliderPositionsByStep[step]) {
                gliderPositionsByStep[step] = {};
            }
            // Calculate glider position at this step
            const pos = Math.round(track.start_pos + track.velocity * (step - track.start_step));
            if (pos >= 0 && pos < width) {
                if (!gliderPositionsByStep[step][pos]) {
                    gliderPositionsByStep[step][pos] = [];
                }
                gliderPositionsByStep[step][pos].push({
                    type: track.type,
                    reachesOutput: reachesOutput
                });
            }
        }
    });

    // Performance optimization: Batch drawing by color groups
    const lastStep = height - 1;

    // Pre-compute visibility bounds
    const startX = Math.max(0, Math.floor(-panX / cellSize));
    const endX = Math.min(width, Math.ceil((canvas.width - panX) / cellSize));
    const startY = Math.max(0, Math.floor(-panY / cellSize));
    const endY = Math.min(height, Math.ceil((canvas.height - panY) / cellSize));

    // Pre-compute input/output region sets for O(1) lookup
    const inputRegionSet = new Set();
    if (showInputRegions) {
        inputRegionRanges.forEach(r => {
            for (let x = r.start; x < r.end; x++) {
                inputRegionSet.add(x);
            }
        });
    }

    const outputRegionSet = new Set();
    if (showOutputRegions) {
        outputRegionRanges.forEach(r => {
            for (let x = r.start; x < r.end; x++) {
                outputRegionSet.add(x);
            }
        });
    }

    // Ultra-fast drawing: Process row by row, drawing horizontal runs of same color
    // Performance optimization: when zoomed out, skip every Nth cell for better performance
    const skipFactor = cellSize < 1 ? Math.max(1, Math.floor(1 / cellSize)) : 1;

    for (let step = startY; step < endY; step += skipFactor) {
        const state = currentHistory[step];
        const y = step * cellSize;

        // Only process if row is visible
        if (y + panY < -cellSize || y + panY >= canvas.height) continue;

        let currentColor = null;
        let runStart = startX;

        for (let x = startX; x <= endX; x++) {
            let color;

            // Determine color for this cell
            if (x < endX) {
                // Input region highlighting (step 0 only)
                if (step === 0 && inputRegionSet.has(x)) {
                    color = '#00ff00'; // Bright green for input
                }
                // Output region highlighting (final step only)
                else if (step === lastStep && outputRegionSet.has(x)) {
                    color = '#ff9800'; // Orange for output
                }
                // Default cell color
                else {
                    color = state[x] ? '#fff' : '#111';
                }
            } else {
                color = null; // End of row marker
            }

            // If color changed, draw the previous run
            if (color !== currentColor && currentColor !== null) {
                const cellX = runStart * cellSize;
                const runWidth = (x - runStart) * cellSize;

                // Only draw if visible
                if (cellX + panX < canvas.width && cellX + runWidth + panX > 0) {
                    ctx.fillStyle = currentColor;
                    ctx.fillRect(cellX, y, runWidth, cellSize * skipFactor);
                }

                runStart = x;
            }

            currentColor = color;
        }
    }

    // Step markers removed as requested

    // Draw encoding section marker (vertical line at cell 100)
    const markerX = 100 * cellSize;
    if (markerX + panX > 0 && markerX + panX < canvas.width) {
        ctx.strokeStyle = '#ff6b6b';
        ctx.lineWidth = 2;
        ctx.beginPath();
        ctx.moveTo(markerX, 0);
        ctx.lineTo(markerX, canvas.height);
        ctx.stroke();

        // Label the encoding section
        ctx.fillStyle = '#ff6b6b';
        ctx.font = `${12 * zoom}px monospace`;
        ctx.fillText('PROGRAM', markerX + 5, 20);
        ctx.fillText('ENCODING', markerX + 5, 35);
        ctx.fillText('→', markerX + 5, 50);
    }

    ctx.restore();

        // Update stats
        document.getElementById('matrix-stats').textContent =
            `Total gliders: ${currentGliderTracks.length} | Output gliders: ${glidersReachingOutput.size}`;
    } catch (error) {
        console.error('Error drawing matrix:', error);
        // Try to show an error message on canvas if possible
        try {
            ctx.restore();
            ctx.fillStyle = '#ff0000';
            ctx.font = '16px monospace';
            ctx.textAlign = 'center';
            ctx.fillText('Drawing error - refresh page', canvas.width / 2, canvas.height / 2);
        } catch (canvasError) {
            console.error('Canvas error handling failed:', canvasError);
        }
    }
