# Numpy Server Example

This example demonstrates how to create a minimal XtalMCP server with numpy statistical functions.

## Configuration

The `numpy_tools.yaml` file defines three numpy functions:
- **`mean`**: Compute arithmetic mean of arrays
- **`std`**: Compute standard deviation of arrays  
- **`quantile`**: Compute quantiles of arrays

## Usage

### 1. Start the server

```bash
PYTHONPATH=src python -m xtalmcp serve --host 127.0.0.1 --port 8080 --config examples/numpy_server/numpy_tools.yaml
```

### 2. Test the tools

The server will be available at `http://127.0.0.1:8080` with the following tools registered:
- `hello_tool` (default)
- `mean` (numpy)
- `std` (numpy)
- `quantile` (numpy)

### 3. Example API calls

```bash
# Test mean function
curl -X POST "http://127.0.0.1:8080/tools/mean" \
  -H "Content-Type: application/json" \
  -d '{"a": [1, 2, 3, 4, 5]}'

# Test std function  
curl -X POST "http://127.0.0.1:8080/tools/std" \
  -H "Content-Type: application/json" \
  -d '{"a": [1, 2, 3, 4, 5], "ddof": 1}'

# Test quantile function
curl -X POST "http://127.0.0.1:8080/tools/quantile" \
  -H "Content-Type: application/json" \
  -d '{"a": [1, 2, 3, 4, 5], "q": 0.5}'
```

## Key Features

- **Direct numpy integration** - No wrapper functions needed
- **Custom schemas** - Explicit input/output validation
- **FastMCP infrastructure** - Built on FastMCP framework
- **REST API** - Tools accessible via HTTP endpoints

## Adding More Functions

To add more numpy functions, simply add them to `numpy_tools.yaml`:

```yaml
  min:
    module: "numpy"
    function: "min"
    description: "Find the minimum value in an array"
    auto_schema: false
    input_schema:
      type: "object"
      properties:
        a:
          type: "array"
          items:
            type: "number"
          description: "Input array"
      required: ["a"]
    output_schema:
      type: "number"
      description: "Minimum value"
```

This example shows how to integrate any Python function (including numpy) into XtalMCP without wrapper complexity. 