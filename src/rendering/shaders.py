"""Shader source code for the Minecraft renderer.

Uses #version 100 (OpenGL ES 2.0) for maximum compatibility including
macOS on Apple Silicon (M1/M2/M3) which only supports OpenGL ES.
"""

import sys
import platform

# Detect macOS on ARM (Apple Silicon) and use ES2 shaders
IS_MACOS_ARM = (platform.system() == "Darwin" and platform.machine() == "arm64")

if IS_MACOS_ARM:
    # OpenGL ES 2.0 compatible shaders for macOS on Apple Silicon
    # Uses attribute/varying instead of in/out, and no layout locations
    VERTEX_SHADER_PROPER = """
    attribute vec3 aPos;
    attribute vec3 aColor;
    
    uniform mat4 projection;
    uniform mat4 view;
    
    varying vec3 fragment_color;
    varying float fragment_light;
    
    void main() {
        gl_Position = projection * view * vec4(aPos, 1.0);
        fragment_color = aColor;
        fragment_light = 0.85;
    }
    """
    
    FRAGMENT_SHADER_PROPER = """
    precision mediump float;
    
    varying vec3 fragment_color;
    varying float fragment_light;
    
    void main() {
        vec3 color = fragment_color * fragment_light;
        
        // Add fog effect
        float fog_factor = smoothstep(40.0, 120.0, gl_FragCoord.z / 1.0);
        vec3 fog_color = vec3(0.53, 0.61, 0.73);
        
        gl_FragColor = vec4(mix(color, fog_color, fog_factor * 0.3), 1.0);
    }
    """
    
    VERTEX_SHADER_SKY = """
    attribute vec3 aPos;
    
    uniform mat4 projection;
    uniform mat4 view;
    
    void main() {
        mat4 viewNoTranslation = mat4(
            mat3(view)
        );
        gl_Position = (projection * viewNoTranslation * vec4(aPos, 1.0)).xyww;
    }
    """
    
    FRAGMENT_SHADER_SKY = """
    precision mediump float;
    
    varying vec3 fragment_color;
    varying float fragment_light;
    
    void main() {
        vec3 color = fragment_color * fragment_light;
        
        // Add fog effect
        float fog_factor = smoothstep(40.0, 120.0, gl_FragCoord.z / 1.0);
        vec3 fog_color = vec3(0.53, 0.61, 0.73);
        
        gl_FragColor = vec4(mix(color, fog_color, fog_factor * 0.3), 1.0);
    }
    """
    
    VERTEX_SHADER_LINES = """
    attribute vec3 aPos;
    
    uniform mat4 projection;
    uniform mat4 view;
    
    void main() {
        gl_Position = projection * view * vec4(aPos, 1.0);
    }
    """
    
    FRAGMENT_SHADER_LINES = """
    precision mediump float;
    
    uniform vec3 line_color;
    
    void main() {
        gl_FragColor = vec4(line_color, 1.0);
    }
    """
else:
    # Standard desktop OpenGL 3.3 shaders for other platforms
    VERTEX_SHADER_PROPER = """
    #version 330 core
    
    layout (location = 0) in vec3 aPos;
    layout (location = 1) in vec3 aColor;
    
    uniform mat4 projection;
    uniform mat4 view;
    
    out vec3 fragment_color;
    out float fragment_light;
    
    void main() {
        gl_Position = projection * view * vec4(aPos, 1.0);
        fragment_color = aColor;
        fragment_light = 0.85;
    }
    """
    
    FRAGMENT_SHADER_PROPER = """
    #version 330 core
    
    in vec3 fragment_color;
    in float fragment_light;
    
    out vec4 FragColor;
    
    void main() {
        vec3 color = fragment_color * fragment_light;
        
        // Add fog effect
        float fog_factor = smoothstep(40.0, 120.0, gl_FragCoord.z / 1.0);
        vec3 fog_color = vec3(0.53, 0.61, 0.73);
        
        FragColor = vec4(mix(color, fog_color, fog_factor * 0.3), 1.0);
    }
    """
    
    VERTEX_SHADER_SKY = """
    #version 330 core
    
    layout (location = 0) in vec3 aPos;
    
    uniform mat4 projection;
    uniform mat4 view;
    
    void main() {
        mat4 viewNoTranslation = mat4(
            mat3(view)
        );
        gl_Position = (projection * viewNoTranslation * vec4(aPos, 1.0)).xyww;
    }
    """
    
    FRAGMENT_SHADER_SKY = """
    #version 330 core
    
    out vec4 FragColor;
    
    uniform vec3 sky_top;
    uniform vec3 sky_bottom;
    uniform float fog_density;
    
    void main() {
        float height = normalize(FragCoord.xyz * 2.0 - 1.0).y;
        vec3 color = mix(sky_bottom, sky_top, max(height, 0.0));
        FragColor = vec4(color, 1.0);
    }
    """
    
    VERTEX_SHADER_LINES = """
    #version 330 core
    
    layout (location = 0) in vec3 aPos;
    
    uniform mat4 projection;
    uniform mat4 view;
    
    void main() {
        gl_Position = projection * view * vec4(aPos, 1.0);
    }
    """
    
    FRAGMENT_SHADER_LINES = """
    #version 330 core
    
    out vec4 FragColor;
    
    uniform vec3 line_color;
    
    void main() {
        FragColor = vec4(line_color, 1.0);
    }
    """

# Legacy shader strings (kept for backwards compatibility)
VERTEX_SHADER = VERTEX_SHADER_PROPER
FRAGMENT_SHADER_PROPER = FRAGMENT_SHADER_PROPER
