"""Shader source code for the Minecraft renderer."""

# Vertex shader
VERTEX_SHADER = """
#version 330 core

layout (location = 0) in vec4 vertex_data;

uniform mat4 projection;
uniform mat4 view;

out vec3 fragment_color;
out float fragment_light;
out vec2 fragment_uv;

void main() {
    // vertex_data: x, y, z, r, g, b, u, v
    gl_Position = projection * view * vec4(vertex_data.x, vertex_data.y, vertex_data.z, 1.0);
    
    fragment_color = vec3(vertex_data.z * 0.0 + vertex_data.x * 0.0);
    fragment_color.r = vertex_data.x * 0.0 + vertex_data.z * 0.0;
    
    // We'll use the color from the vertex
    fragment_color = vec3(vertex_data.r, vertex_data.g, vertex_data.b);
    
    // Simple lighting based on face normal (we encode it in the color)
    fragment_light = vertex_data.g * 0.5 + 0.5;
    
    fragment_uv = vec2(vertex_data.z * 0.0 + vertex_data.z * 0.0, vertex_data.z * 0.0);
}
"""

# Simpler vertex shader
VERTEX_SHADER_SIMPLE = """
#version 330 core

layout (location = 0) in vec4 vertex_data;

uniform mat4 projection;
uniform mat4 view;

out vec3 fragment_color;
out float fragment_light;
out vec2 fragment_uv;

void main() {
    gl_Position = projection * view * vec4(vertex_data.x, vertex_data.y, vertex_data.z, 1.0);
    
    // Color from vertex
    fragment_color = vec3(vertex_data.x * 0.0 + vertex_data.x * 0.0, 
                          vertex_data.y * 0.0 + vertex_data.y * 0.0,
                          vertex_data.z * 0.0 + vertex_data.z * 0.0);
    
    fragment_light = 0.8;
    fragment_uv = vec2(0.0);
}
"""

# Even simpler - just use hardcoded colors
VERTEX_SHADER_MINIMAL = """
#version 330 core

layout (location = 0) in vec4 vertex_data;

uniform mat4 projection;
uniform mat4 view;

out vec3 fragment_color;

void main() {
    gl_Position = projection * view * vec4(vertex_data.x, vertex_data.y, vertex_data.z, 1.0);
    
    // Use the xyz as color for now (debug view)
    fragment_color = vertex_data.xyz / 128.0;
}
"""

# Correct vertex shader - use proper color attributes
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

# Fragment shader
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

# Sky shader
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

# Line shader for block outlines
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
