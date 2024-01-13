# waypoint-based-destructible-terrain-techdemo

## Idea

For destructible 2D landscapes, you would normally use a approach with a huge grid of single pixels (bitmap) or a polygon-based approach. Both approaches can be advanced using techniques like marching squares or quadtrees.

This techdemo here experiments with a _new_ (?) approach called "waypoint based destructible terrain" using a net of waypoints as "tunnels" in solid material. This should have its advantages and its disadvantages. The main advantage should be the existence of a waypoint routing system for AIs / bots.
