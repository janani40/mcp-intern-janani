from mcp.server.fastmcp import FastMCP

# Create the server. "hello-server" is its name.
mcp = FastMCP("hello-server")


@mcp.tool()
def say_hello(name: str) -> str:
    """Greet a person by name."""
    return f"Hello, {name}! Welcome to my first MCP server."


@mcp.tool()
def add_numbers(a: float, b: float) -> float:
    """Add two numbers and return the result."""
    return a + b


if __name__ == "__main__":
    mcp.run()