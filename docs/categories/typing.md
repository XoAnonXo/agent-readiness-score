# Static Typing Category (10% Weight)

The Static Typing category measures your project's use of type systems and type checking tools. Strong typing helps AI agents understand interfaces and prevents type errors.

## Why Static Typing Matters for Agents

AI agents benefit from static typing because:

1. **Interface Understanding** - Clear parameter and return types
2. **Error Prevention** - Catch type errors before runtime
3. **IDE Support** - Better autocomplete and suggestions
4. **Self-Documentation** - Types serve as inline documentation
5. **Refactoring Safety** - Type checker validates changes

**Without type hints, agents must guess at function signatures and data structures.**

## What This Category Checks

### Python Type Checking (Weight: 2.0)

**mypy:**
- `mypy.ini`
- `.mypy.ini`
- `pyproject.toml` with `[tool.mypy]`
- `setup.cfg` with `[mypy]`

**Example mypy.ini:**
```ini
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
disallow_any_unimported = True
no_implicit_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
warn_no_return = True
check_untyped_defs = True
strict_equality = True
```

**Example pyproject.toml:**
```toml
[tool.mypy]
python_version = "3.10"
strict = true
warn_return_any = true
warn_unused_ignores = true
disallow_untyped_defs = true
```

**Pyright/Pylance:**
- `pyrightconfig.json`
- `pyproject.toml` with `[tool.pyright]`

**Example pyrightconfig.json:**
```json
{
  "include": ["src"],
  "exclude": ["**/node_modules", "**/__pycache__"],
  "typeCheckingMode": "strict",
  "reportMissingImports": true,
  "reportMissingTypeStubs": false,
  "pythonVersion": "3.10"
}
```

**Pydantic:**
- Usage of Pydantic models for runtime validation
- `from pydantic import BaseModel`

### TypeScript Configuration (Weight: 2.5)

**Files:**
- `tsconfig.json`
- `tsconfig.*.json` (multiple configs)

**Example tsconfig.json:**
```json
{
  "compilerOptions": {
    "target": "ES2022",
    "module": "ESNext",
    "lib": ["ES2022", "DOM"],
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "declaration": true,
    "declarationMap": true,
    "sourceMap": true,
    "outDir": "./dist"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules", "dist"]
}
```

**Strict mode options (highly valued):**
```json
{
  "compilerOptions": {
    "strict": true,              // Enables all strict checks
    "noImplicitAny": true,       // Error on implicit 'any'
    "strictNullChecks": true,    // Null/undefined checking
    "strictFunctionTypes": true, // Function type checking
    "strictBindCallApply": true, // Strict bind/call/apply
    "strictPropertyInitialization": true,
    "noImplicitThis": true,
    "alwaysStrict": true
  }
}
```

### Type Stubs (Weight: 1.5)

**Python:**
- `.pyi` stub files
- `py.typed` marker file in package
- `types-*` packages in dependencies

**Example py.typed:**
```
# Just an empty file indicating package is typed
```

**Example stub file (mymodule.pyi):**
```python
from typing import Optional

def process_data(data: str, strict: bool = ...) -> Optional[dict]: ...

class DataProcessor:
    def __init__(self, config: dict) -> None: ...
    def process(self, input: str) -> str: ...
```

**TypeScript:**
- `.d.ts` declaration files
- `@types/*` packages

**Example types.d.ts:**
```typescript
declare module 'my-module' {
  export function doSomething(x: number): string;
  export class MyClass {
    constructor(name: string);
    process(): void;
  }
}
```

### Go Interfaces (Weight: 1.5)

Go's interface system for type safety.

**Well-defined interfaces:**
```go
// types.go
package myapp

type Reader interface {
    Read(p []byte) (n int, err error)
}

type Writer interface {
    Write(p []byte) (n int, err error)
}

type Processor interface {
    Process(data string) (string, error)
}
```

### Flow Type (Weight: 1.0)

Flow for JavaScript type checking.

**Files:**
- `.flowconfig`

**Example .flowconfig:**
```ini
[ignore]
.*/node_modules/.*

[include]

[libs]

[lints]

[options]
all=true
```

### Protocol Buffers (Weight: 1.2)

Strongly-typed data definitions.

**Files:**
- `*.proto` files
- `buf.yaml` (Buf configuration)

**Example user.proto:**
```protobuf
syntax = "proto3";

package myapp;

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
  repeated string roles = 4;
}

service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc CreateUser(CreateUserRequest) returns (User);
}
```

### GraphQL Schema (Weight: 1.0)

Type-safe GraphQL definitions.

**Files:**
- `schema.graphql`
- `*.graphql` files

**Example schema.graphql:**
```graphql
type User {
  id: ID!
  name: String!
  email: String!
  posts: [Post!]!
}

type Post {
  id: ID!
  title: String!
  content: String!
  author: User!
}

type Query {
  user(id: ID!): User
  users: [User!]!
}

type Mutation {
  createUser(name: String!, email: String!): User!
}
```

### Rust Type System (Weight: 1.5)

Rust's strong type system (built-in).

**Indicators:**
- `Cargo.toml` with typed dependencies
- Comprehensive type annotations

### JVM Type Systems (Weight: 1.0)

**Kotlin:**
- Null safety built-in
- Type inference

**Java:**
- Generic types
- `@NonNull` annotations

### Runtime Type Validation (Weight: 1.0)

**Python:**
- Pydantic models
- TypeGuard usage
- Runtime type checking with typeguard

**Example with Pydantic:**
```python
from pydantic import BaseModel, EmailStr, Field

class User(BaseModel):
    id: int
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr
    age: int = Field(..., ge=0, le=150)

# Runtime validation
user = User(id=1, name="John", email="john@example.com", age=30)
# Raises ValidationError if invalid
```

**TypeScript:**
- Zod schema validation
- io-ts runtime types

**Example with Zod:**
```typescript
import { z } from 'zod';

const UserSchema = z.object({
  id: z.number(),
  name: z.string().min(1).max(100),
  email: z.string().email(),
  age: z.number().min(0).max(150),
});

type User = z.infer<typeof UserSchema>;

// Runtime validation
const user = UserSchema.parse(data);
```

## Scoring Examples

### Example 1: No Type Checking (Score: 0/100)

```python
# No type hints
def process_data(data):
    return data.upper()
```

**Score:** 0/100 | **Contribution:** 0

### Example 2: Type Hints Only (Score: 30/100)

```python
# Type hints but no checking
def process_data(data: str) -> str:
    return data.upper()
```

**Score:** ~30/100 | **Contribution:** 3.0

### Example 3: mypy Configuration (Score: 60/100)

```
repo/
├── mypy.ini            # ✓ Type checker (2.0)
├── src/
│   └── app.py          # With type hints
└── pyproject.toml
```

**Score:** ~60/100 | **Contribution:** 6.0

### Example 4: TypeScript Strict (Score: 80/100)

```
repo/
├── tsconfig.json       # ✓ TypeScript (2.5)
│   # with strict: true
├── src/
│   └── index.ts
└── package.json
```

**Score:** ~80/100 | **Contribution:** 8.0

### Example 5: Excellent (Score: 95/100)

```
repo/
├── mypy.ini            # ✓ Type checker (2.0)
├── py.typed            # ✓ Typed marker (1.5)
├── src/
│   ├── models.py       # Pydantic models (1.0)
│   └── app.py
└── pyproject.toml
```

**Score:** 95/100 | **Contribution:** 9.5

## Improvement Roadmap

### Level 1: Add Type Hints (Target: 30/100)

```python
# Before
def add(a, b):
    return a + b

# After
def add(a: int, b: int) -> int:
    return a + b
```

### Level 2: Configure Type Checker (Target: 60/100)

```bash
# Python
cat > mypy.ini << 'EOF'
[mypy]
python_version = 3.10
warn_return_any = True
warn_unused_configs = True
disallow_untyped_defs = True
EOF

# TypeScript
cat > tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "strict": true,
    "target": "ES2022"
  }
}
EOF
```

### Level 3: Enable Strict Mode (Target: 80/100)

```ini
# mypy.ini
[mypy]
strict = true
```

```json
// tsconfig.json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true
  }
}
```

### Level 4: Full Coverage (Target: 95/100)

- Add `py.typed` marker
- Type all public APIs
- Add runtime validation (Pydantic)
- Generate type stubs

## Best Practices

### 1. Progressive Typing

Start with critical paths:
```python
# High priority: Public APIs
def public_api(data: dict[str, Any]) -> Response:
    ...

# Lower priority: Internal helpers
def _internal_helper(x):  # Can add types later
    ...
```

### 2. Use Strict Settings

```ini
# mypy.ini - Start strict
[mypy]
strict = true

# Allow exceptions for specific files
[mypy-tests.*]
disallow_untyped_defs = false
```

### 3. Type Narrow Carefully

```python
from typing import Union

def process(data: Union[str, int]) -> str:
    if isinstance(data, str):
        # Type checker knows data is str here
        return data.upper()
    else:
        # Type checker knows data is int here
        return str(data)
```

### 4. Use Generic Types

```python
from typing import TypeVar, Generic, List

T = TypeVar('T')

class Container(Generic[T]):
    def __init__(self, items: List[T]) -> None:
        self.items = items

    def get_first(self) -> T:
        return self.items[0]

# Type-safe usage
numbers: Container[int] = Container([1, 2, 3])
first: int = numbers.get_first()
```

### 5. Document Complex Types

```python
from typing import TypedDict

class UserDict(TypedDict):
    """User data structure.

    Attributes:
        id: Unique user identifier
        name: User's full name
        email: User's email address
    """
    id: int
    name: str
    email: str
```

## Common Pitfalls

### Pitfall 1: Using `Any` Everywhere

**Problem:**
```python
def process(data: Any) -> Any:
    ...
```

**Solution:**
```python
def process(data: dict[str, str]) -> list[str]:
    ...
```

### Pitfall 2: Ignoring Type Errors

**Problem:**
```python
result = some_function()  # type: ignore
```

**Solution:** Fix the underlying type issue

### Pitfall 3: Missing Return Types

**Problem:**
```python
def calculate(x: int, y: int):  # No return type
    return x + y
```

**Solution:**
```python
def calculate(x: int, y: int) -> int:
    return x + y
```

### Pitfall 4: Mutable Default Arguments

**Problem:**
```python
def process(items: list[str] = []) -> None:  # Dangerous!
    items.append("x")
```

**Solution:**
```python
def process(items: list[str] | None = None) -> None:
    if items is None:
        items = []
    items.append("x")
```

## Integration with CI

```yaml
# .github/workflows/typecheck.yml
name: Type Check

on: [push, pull_request]

jobs:
  mypy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Install dependencies
        run: |
          pip install mypy
          pip install -e .

      - name: Run mypy
        run: mypy src/

  typescript:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - uses: actions/setup-node@v4
        with:
          node-version: '20'

      - run: npm install
      - run: npx tsc --noEmit
```

## Quick Wins

**30 minutes:**

1. Add type hints to main functions
2. Create `mypy.ini` or `tsconfig.json`
3. Run type checker and fix errors
4. Add type checking to CI

**Result:** Score 0 → 60+

## Tool Recommendations

### Python
- **mypy** - Industry standard
- **Pyright** - Fast, VS Code default
- **Pydantic** - Runtime validation

### JavaScript/TypeScript
- **TypeScript** - De facto standard
- **Zod** - Runtime validation
- **io-ts** - Type-safe runtime types

### Multi-language
- **Protocol Buffers** - Cross-language types
- **GraphQL** - API type safety

## Further Reading

- [mypy Documentation](https://mypy.readthedocs.io/)
- [TypeScript Handbook](https://www.typescriptlang.org/docs/)
- [Python Type Hints PEP 484](https://peps.python.org/pep-0484/)
- [Pydantic Documentation](https://docs.pydantic.dev/)

## Next Steps

- Review [Extending](../extending.md) guide
- Set up [CI Integration](../ci-integration.md)
- Check overall [Scoring System](../scoring-system.md)
