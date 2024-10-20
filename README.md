# waypoint_based_destructible_terrain

A waypoint net that is both used for AI player navigation and rendering a destructible terrain for 2D side-scrolling games. 

Why? In the context of destructible two-dimensional (2D) landscapes, conventional approaches involve the usage of either a vast grid comprising individual pixels (bitmap) or a polygon-based approach. Advanced techniques such as marching squares or quadtrees are often employed to enhance these approaches. However, both approaches (bitmaps and polygons) encounter big challenges when moving AI players within an unstable environment. Waypoints are usually only used in games with static landscapes.

## Legacy Python PoC

```
git clone https://github.com/772/waypoint_based_destructible_terrain
pip install pygame
python waypoint_based_destructible_terrain/waypoint_based_destructible_terrain.py
```

https://github.com/772/waypoint_based_destructible_terrain/assets/13351564/241ac18c-6b9e-476c-b557-5d33b818c0ba

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as GNU General Public License 3, without any additional terms or conditions.
