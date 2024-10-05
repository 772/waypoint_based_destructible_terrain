# waypoint_based_destructible_terrain

waypoint_based_destructible_terrain is a small techdemo showcasing an artificial intelligence (AI)-compatible destructible terrain designed for side-scrolling games. The functionality is achieved through the implementation of a dynamic waypoint network, utilized concurrently for AI player navigation and landscape rendering. The landscape allows no modification other than the creation of new tunnels (waypoints).

Why? In the context of destructible two-dimensional (2D) landscapes, conventional approaches involve the usage of either a vast grid comprising individual pixels (bitmap) or a polygon-based approach. Advanced techniques such as marching squares or quadtrees are often employed to enhance these approaches. However, both approaches (bitmaps and polygons) encounter big challenges when moving AI players within an unstable environment. Waypoints are usually only used in games with static landscapes.

https://github.com/772/waypoint_based_destructible_terrain/assets/13351564/241ac18c-6b9e-476c-b557-5d33b818c0ba

## Build

```
git clone https://github.com/772/waypoint_based_destructible_terrain
pip install pygame
python waypoint_based_destructible_terrain/waypoint_based_destructible_terrain.py
```

## Contribution

Unless you explicitly state otherwise, any contribution intentionally submitted for inclusion in the work by you, shall be licensed as GNU General Public License 3, without any additional terms or conditions.
