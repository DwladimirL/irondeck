# The IronDeck brand

<img src="../marca/png/irondeck-256.png" width="128" height="128" alt="IronDeck logo">

The logo is a matte steel plate with an anvil cut through it. The heat of tempering rises from the bottom to the middle of the plate: the colors steel takes as it heats up, the same ones the website uses, toned down.

[Versión en español](marca.md) · [Back to the start](../README.md)

## Files

| File | What it's for |
|---|---|
| `marca/irondeck-icono.svg` | The detailed logo, for 48 px and up: matte texture, rivets and the wall of the cut |
| `marca/irondeck-icono-simple.svg` | For 32 px and below: headers, favicon, toolbars |
| `marca/irondeck-horizontal.svg`, `irondeck-horizontal-clara.svg` | The logo with the name, for light and for dark backgrounds. The name is outlined, so it doesn't need the font installed |
| `marca/irondeck-una-tinta.svg`, `irondeck-una-tinta-blanca.svg` | One color, with the anvil as a real hole: stamps, laser engraving, embroidery, black-and-white documents |
| `marca/irondeck-yunque.svg` | The anvil on its own |
| `marca/png/irondeck-16.png` to `irondeck-512.png` | The icon as PNG; up to 32 px it uses the simple drawing |
| `marca/png/irondeck-avatar-800.png` | Avatar for GitHub, Ko-fi, YouTube or X: dark background with room for the round crop |
| `marca/png/irondeck-horizontal@2x.png`, `irondeck-horizontal-clara@2x.png` | The logo with the name, as PNG |
| `marca/irondeck.ico` | The program's Windows icon: 16, 24, 32, 48, 64, 128 and 256 px |
| `favicon.ico`, `apple-touch-icon.png` | The browser tab and the iPhone or iPad icon (at the site root) |

## Rules

- **The anvil is a hole in the plate, not a shape placed on it.** No shadow, relief or shine of its own: the inside is dark and, at the bottom, you see the wall of the cut.
- **Up to 32 px, the simple drawing; from 48 px, the detailed one.** The simple one drops the texture and rivets and makes the anvil larger so it reads.
- **Clear space around it:** at least one eighth of the icon's width.
- **Don't** rotate, stretch or crop the plate, change the heat colors, or put the anvil on another shape.
- On photos or busy backgrounds, use the one-color version.
- The name is always **IRONDECK**, in stencil capitals, to the right of the icon, with a cap height close to half the icon's height.

## Colors

| Use | Hex |
|---|---|
| Steel, top to bottom | `#525962` → `#3d434a` → `#30353b` |
| Heat, hottest to coolest | `#405584` blue · `#6c5570` purple · `#946748` bronze · `#bf9c64` straw |
| Ink (text and one color on light) | `#121820` |
| Light (text on dark) | `#e4e9ef` |

## Typography

The name: Big Shoulders Stencil Display, weight 800, 0.04 em tracking. Website text: Inter Tight and IBM Plex Mono. They live in `fuentes/`, under the SIL Open Font License.

## The anvil

A London-pattern anvil: a conical horn whose underside sweeps in one curve into the body, a table lower than the face, a steel face, the heel, a narrow waist and feet with an arch. Its height is 46% of its length.

## Changing or regenerating it

- The SVGs come from `herramientas/marca.py` (Python 3, no dependencies): `python herramientas/marca.py`. The anvil drawing, colors and positions live there.
- PNGs and ICOs are exported from those SVGs with any browser or Inkscape. The ICO holds 16, 24 and 32 px from the simple drawing and 48, 64, 128 and 256 px from the detailed one.
- The social images (`og-es.png`, `og-en.png`) come from `fuente/og.html`, which already uses the icon.

---

IronDeck is an independent project and is not affiliated with Anthropic. Claude and Claude Code are trademarks of Anthropic, PBC.
