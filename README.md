# waypoint_based_destructible_terrain

A waypoint net that is both used for AI player navigation and rendering a destructible terrain for 2D side-scrolling games. 

Why? In the context of destructible two-dimensional (2D) landscapes, conventional approaches involve the usage of either a vast grid comprising individual pixels (bitmap) or a polygon-based approach. Both approaches (bitmaps and polygons) encounter big challenges when moving AI players within an unstable environment because waypoints are usually only used in games with static landscapes. This project here uses a very limited but easy polygon-based approach that is optimized for waypoint usage. The data structure consist of three large vectors that contain all horizontal and diagonal free spaces in the environment. All free spaces have the same height, but can be stacked on each other and overlap.

Open https://772.github.io/waypoint_based_destructible_terrain/ to test an example.

## Features

- AI friendly landscape.
- Pixel perfect precision without bitmap.
- No Featuritis: Less than 1000 lines of safe Rust code.
- 100% free. Forever and always.

![Example](example.png)

## Downsides

- Transparent materials are hard to implement.

## How to update the wasm in this repository

```
cargo build --target wasm32-unknown-unknown --release
wasm-bindgen --no-typescript --target web --out-dir ./ --out-name "waypoint_based_destructible_terrain" ./target/wasm32-unknown-unknown/release/waypoint_based_destructible_terrain.wasm
git add -A && git commit -m "Update wasm." && git push
```

If you haven`t used wasm so far, use this first:

```
rustup target add wasm32-unknown-unknown
cargo install wasm-bindgen-cli
```

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as GNU General Public License 3, without any additional terms or conditions.
