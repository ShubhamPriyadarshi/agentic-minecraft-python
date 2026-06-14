"""OpenGL utility functions and shader management."""

import OpenGL.GL as gl
import numpy as np
import ctypes


def create_shader_program(vertex_src: str, fragment_src: str) -> int:
    """Create and compile a shader program from source strings."""
    
    # Compile vertex shader
    vertex_shader = gl.glCreateShader(gl.GL_VERTEX_SHADER)
    gl.glShaderSource(vertex_shader, vertex_src)
    gl.glCompileShader(vertex_shader)
    
    # Check compilation
    status = gl.glGetShaderiv(vertex_shader, gl.GL_COMPILE_STATUS)
    if not status:
        error = gl.glGetShaderInfoLog(vertex_shader).decode()
        gl.glDeleteShader(vertex_shader)
        # Debug: print the shader source
        print(f"VERTEX SHADER SOURCE:\n{vertex_src}")
        print(f"VERTEX SHADER ERROR: {error}")
        raise RuntimeError(f"Vertex shader compilation failed: {error}")
    
    # Compile fragment shader
    fragment_shader = gl.glCreateShader(gl.GL_FRAGMENT_SHADER)
    gl.glShaderSource(fragment_shader, fragment_src)
    gl.glCompileShader(fragment_shader)
    
    # Check compilation
    status = gl.glGetShaderiv(fragment_shader, gl.GL_COMPILE_STATUS)
    if not status:
        error = gl.glGetShaderInfoLog(fragment_shader).decode()
        print(f"FRAGMENT SHADER SOURCE:\n{fragment_src}")
        print(f"FRAGMENT SHADER ERROR: {error}")
        gl.glDeleteShader(fragment_shader)
        gl.glDeleteShader(vertex_shader)
        raise RuntimeError(f"Fragment shader compilation failed: {error}")
    
    # Link program
    program = gl.glCreateProgram()
    gl.glAttachShader(program, vertex_shader)
    gl.glAttachShader(program, fragment_shader)
    gl.glLinkProgram(program)
    
    # Check linking
    if not gl.glGetProgramiv(program, gl.GL_LINK_STATUS):
        error = gl.glGetProgramInfoLog(program).decode()
        gl.glDeleteProgram(program)
        gl.glDeleteShader(vertex_shader)
        gl.glDeleteShader(fragment_shader)
        raise RuntimeError(f"Shader program linking failed: {error}")
    
    # Clean up shaders (linked into program)
    gl.glDeleteShader(vertex_shader)
    gl.glDeleteShader(fragment_shader)
    
    return program


def create_vbo(data: np.ndarray) -> int:
    """Create a Vertex Buffer Object from numpy data."""
    vbo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glBufferData(gl.GL_ARRAY_BUFFER, data, gl.GL_STATIC_DRAW)
    return vbo


def create_ibo(indices: np.ndarray) -> int:
    """Create an Element Buffer Object from numpy indices."""
    ibo = gl.glGenBuffers(1)
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
    gl.glBufferData(gl.GL_ELEMENT_ARRAY_BUFFER, indices, gl.GL_STATIC_DRAW)
    return ibo


def create_vao(vbo: int, ibo: int, num_components: int = 8, 
               color_vbo: int = 0) -> int:
    """Create a Vertex Array Object.
    
    For OpenGL ES 2.0 compatibility, uses separate attribute locations
    for position (location 0) and color (location 1).
    """
    vao = gl.glGenVertexArrays(1)
    gl.glBindVertexArray(vao)
    
    gl.glBindBuffer(gl.GL_ARRAY_BUFFER, vbo)
    gl.glEnableVertexAttribArray(0)
    gl.glVertexAttribPointer(0, 3, gl.GL_FLOAT, False, 
                             num_components * 4, None)
    
    if color_vbo:
        gl.glBindBuffer(gl.GL_ARRAY_BUFFER, color_vbo)
        gl.glEnableVertexAttribArray(1)
        gl.glVertexAttribPointer(1, 3, gl.GL_FLOAT, False,
                                 num_components * 4, 
                                 ctypes.c_void_p(3 * 4))
    
    gl.glBindBuffer(gl.GL_ELEMENT_ARRAY_BUFFER, ibo)
    
    gl.glBindVertexArray(0)
    
    return vao


def delete_vao(vao: int):
    """Delete a Vertex Array Object."""
    if vao:
        gl.glDeleteVertexArrays(1, [vao])


def delete_vbo(vbo: int):
    """Delete a Vertex Buffer Object."""
    if vbo:
        gl.glDeleteBuffers(1, [vbo])


def delete_ibo(ibo: int):
    """Delete an Element Buffer Object."""
    if ibo:
        gl.glDeleteBuffers(1, [ibo])
