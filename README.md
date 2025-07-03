__Because less is more.__

# waypoint_based_destructible_terrain

A waypoint net that is both used for AI player navigation and rendering a destructible terrain for 2D side-scrolling games.

Why? In the context of destructible two-dimensional (2D) landscapes, conventional approaches involve the usage of either a vast grid comprising individual pixels (bitmap) or a polygon-based approach. Both approaches (bitmaps and polygons) encounter big challenges when moving AI players within an unstable environment because waypoints are usually only used in games with static landscapes. This project here uses a very limited but easy polygon-based approach that is optimized for waypoint usage. The data structure consist of three large vectors that contain all horizontal and diagonal free spaces in the environment. All free spaces have the same height, but can be stacked on each other and overlap.

Open https://772.github.io/waypoint_based_destructible_terrain/ to test an example.

The whole data is stored in this simple struct:

```
pub struct Map {
    horizontal_lines: Vec<[f32; 3]>,        // [y, x, length].
    baroque_diagonal_lines: Vec<[f32; 3]>,  // [y, x, length].
    sinister_diagonal_lines: Vec<[f32; 3]>, // [y, x, length].
}
```

## Info

- Even tho there is only a limited amount of lines, this fact gives structure (Stronghold) and keeps the optical illusion of completely destructable landscapes. Also: Only using this kind of pattern is very **AI friendly**.
- Very simple distance-based collision detection.

![Example](example.png)

## How to update the wasm branch in this repository

Note that after the WebAssembly branch was initially created, I deleted all files in it.

```
cargo b
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli
git add -A && git commit -m "Update."
git push
cargo build --target wasm32-unknown-unknown --release
wasm-bindgen --no-typescript --target web --out-dir ./../ --out-name "wasm" ./target/wasm32-unknown-unknown/release/*.wasm
cp index.html ..
cp example.md ..
cp assets .. -r
git checkout wasm
rm assets -R
mv ../index.html .
mv ../example.md .
mv ../wasm.js .
mv ../wasm_bg.wasm .
mv ../assets .
git add wasm.js wasm_bg.wasm index.html example.md assets
git commit -m "Update wasm files."
git push -f
git checkout main
```
