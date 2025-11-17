## What is RustyClonk?

Look here: https://772.github.io/waypoint_based_destructible_terrain.

In the context of destructible two-dimensional (2D) landscapes, conventional approaches involve the usage of either a vast grid comprising individual pixels (bitmap) or a polygon-based approach. Both approaches (bitmaps and polygons) encounter big challenges when moving AI players within an unstable environment because waypoints are usually only used in games with static landscapes. This project here uses a very limited but easy approach that is optimized for waypoint usage. The whole destructable 2D terrain data is stored in this simple Rust struct called `Main`:

```rust
pub struct Map {
    horizontal_lines: Vec<Line>,
    baroque_diagonal_lines: Vec<Line>,
    sinister_diagonal_lines: Vec<Line>,
}

pub struct Line {
	x: f32,
	y: f32,
	length: f32,
	midair: bool,
}
```

![Example](example.png)

## Info

- Even tho there is only a limited amount of lines, this fact gives structure (Stronghold) and keeps the optical illusion of completely destructable landscapes. Also: Only using this kind of pattern is very **AI friendly**.
- Very simple distance-based collision detection.
- 'Clonk' is a registered trademark of Matthes Bender.

## Updates

- **2025-11-17:** We are still in an experimental stage.
