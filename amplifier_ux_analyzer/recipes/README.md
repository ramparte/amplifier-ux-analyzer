# UX Analyzer Recipes

Workflow orchestration recipes for the UX Analyzer bundle.

## Available Recipes

### `roundtrip.yaml`

Complete iterative refinement workflow:

1. **Analyze** reference screenshot → JSON
2. **Convert** JSON → YAML spec
3. **Generate** HTML/CSS/JS from spec
4. **Render** generated HTML → screenshot
5. **Analyze** generated screenshot → JSON
6. **Compare** reference vs generated
7. **Evaluate** match quality
8. **Iterate** with feedback if needed (up to max_iterations)

**Usage**:

```bash
# From Amplifier CLI
amplifier tool invoke recipes operation=execute \
  recipe_path=@ux-analyzer:recipes/roundtrip.yaml \
  context='{"reference_image": "reference.png", "max_iterations": 3}'

# Or using recipes tool directly
recipes execute @ux-analyzer:recipes/roundtrip.yaml \
  --context reference_image=reference.png \
  --context max_iterations=3
```

**Context Parameters**:

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `reference_image` | Path to reference screenshot | - | ✓ |
| `output_dir` | Output directory for all files | `./roundtrip-output` | |
| `max_iterations` | Maximum refinement iterations | `3` | |

**Output Files**:

```
roundtrip-output/
├── reference-analysis.json      # CV analysis of reference
├── reference-spec.yaml          # Design spec from reference
├── generated.html               # Generated HTML/CSS/JS
├── generated-screenshot.png     # Screenshot of generated UI
├── generated-analysis.json      # CV analysis of generated
└── comparison-diff.png          # Visual diff overlay
```

---

### `simple-generate.yaml`

Single-pass generation without iteration:

1. **Analyze** screenshot → JSON
2. **Convert** JSON → YAML spec
3. **Generate** HTML from spec

**Usage**:

```bash
# From Amplifier CLI
amplifier tool invoke recipes operation=execute \
  recipe_path=@ux-analyzer:recipes/simple-generate.yaml \
  context='{"reference_image": "reference.png"}'

# Or using recipes tool directly
recipes execute @ux-analyzer:recipes/simple-generate.yaml \
  --context reference_image=reference.png
```

**Context Parameters**:

| Parameter | Description | Default | Required |
|-----------|-------------|---------|----------|
| `reference_image` | Path to reference screenshot | - | ✓ |
| `output_dir` | Output directory | `./generation-output` | |

**Output Files**:

```
generation-output/
├── analysis.json          # CV analysis
├── spec.yaml             # Design spec
└── generated.html        # Generated HTML
```

---

## Match Quality Criteria

The roundtrip recipe uses SSIM (Structural Similarity Index) to evaluate match quality:

| SSIM Range | Quality | Action |
|------------|---------|--------|
| > 0.85 | ✅ Acceptable | Stop, use generated HTML |
| 0.75 - 0.85 | ⚠️ Good | Iterate if iterations remain |
| < 0.75 | ❌ Poor | Iterate with feedback |

---

## Examples

### Basic Roundtrip

```bash
# Analyze and generate with default settings
recipes execute @ux-analyzer:recipes/roundtrip.yaml \
  --context reference_image=ui-design.png
```

### Custom Output Directory

```bash
# Save to specific directory
recipes execute @ux-analyzer:recipes/roundtrip.yaml \
  --context reference_image=ui-design.png \
  --context output_dir=./my-ui-output
```

### More Iterations

```bash
# Allow up to 5 refinement iterations
recipes execute @ux-analyzer:recipes/roundtrip.yaml \
  --context reference_image=ui-design.png \
  --context max_iterations=5
```

### Quick Generation

```bash
# Just generate once, no iteration
recipes execute @ux-analyzer:recipes/simple-generate.yaml \
  --context reference_image=ui-design.png
```

---

## Requirements

These recipes require:

- **Python tools**: `amplifier-ux-analyzer` CLI installed
- **agent-browser**: For rendering and screenshotting generated HTML
- **Amplifier**: Recipe execution environment
- **Provider**: Anthropic API access (Claude models)

---

## Extending the Recipes

### Adding Custom Steps

You can extend these recipes by adding steps:

```yaml
steps:
  # ... existing steps ...
  
  - id: custom_validation
    type: bash
    command: |
      # Your custom validation logic
      python my_validator.py "{{context.output_dir}}/generated.html"
```

### Creating Variants

Copy a recipe and modify for specific use cases:

- `roundtrip-mobile.yaml` - Mobile-specific viewport
- `roundtrip-fast.yaml` - Use Haiku for faster generation
- `roundtrip-strict.yaml` - Higher SSIM threshold (0.95)

---

## Troubleshooting

### Recipe Fails at analyze Step

**Issue**: `amplifier-ux-analyzer: command not found`

**Solution**: Install the package:
```bash
cd amplifier-ux-analyzer-dev
pip install -e .
```

### Recipe Fails at render_html Step

**Issue**: `agent-browser: command not found`

**Solution**: Ensure agent-browser bundle is installed in Amplifier.

### Low SSIM Scores

**Issue**: Generated UI doesn't match reference well (SSIM < 0.75)

**Possible causes**:
- Reference screenshot has complex gradients or effects
- OCR failed to extract text accurately
- Color detection missed subtle variations

**Solutions**:
- Provide higher resolution reference screenshot
- Manually refine the spec YAML before generation
- Increase `max_iterations` for more refinement passes

### HTML Generation Timeout

**Issue**: LLM takes too long to generate HTML

**Solution**: Use faster model in recipe:
```yaml
model: claude-haiku-*  # Instead of claude-sonnet-4-*
```
