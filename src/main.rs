#![allow(clippy::type_complexity, clippy::collapsible_if)]

use bevy::prelude::*;
use rand::Rng;
use std::collections::{HashMap, VecDeque};

// Public consts.
pub const HGT_HUMANOID: f32 = 40.0;
pub const HGT_JUMP_PARABOLA: f32 = 50.0;
pub const WDT_JUMP_PARABOLA: f32 = 60.0;
pub const SPEED_WALKING: f32 = 3.0;
pub const AMOUNT_AIS: usize = 0;
// Hidden consts.
pub const HGT_TUNNEL: f32 = 60.0;
pub const WDT_MAP: f32 = 1920.0;
pub const HGT_MAP: f32 = 1080.0;

#[derive(Component)]
pub struct ControledByPlayer;
#[derive(Component)]
pub struct ControledByAI;
#[derive(Component)]
pub struct CurrentTunnel(pub [usize; 3]);
#[derive(Debug, Resource)]
pub struct Map {
    horizontal_lines: Vec<[f32; 3]>,        // [y, x, length].
    baroque_diagonal_lines: Vec<[f32; 3]>,  // [y, x, length].
    sinister_diagonal_lines: Vec<[f32; 3]>, // [y, x, length].
}
#[derive(Component, Debug, PartialEq)]
pub enum GazeDirection {
    Left,
    Right,
}
#[derive(Component, Debug, PartialEq)]
pub enum Action {
    Idle,
    WalkingLeft,
    WalkingRight,
    _Falling,
    Digging,
}

pub fn jump_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
}

impl Default for Map {
    fn default() -> Self {
        let mut rng = rand::rng();
        let max_tunnel_length = WDT_MAP / 2.0;
        let tunnel_per_category = 10;
        let mut horizontal_lines: Vec<[f32; 3]> = (0..tunnel_per_category)
            .map(|_| {
                [
                    rng.random_range(HGT_TUNNEL..HGT_MAP),
                    rng.random_range(0.0..WDT_MAP),
                    rng.random_range(10.0..max_tunnel_length),
                ]
            })
            .collect();
        let mut baroque_diagonal_lines: Vec<[f32; 3]> = (0..tunnel_per_category)
            .map(|_| {
                [
                    rng.random_range(HGT_TUNNEL..HGT_MAP),
                    rng.random_range(0.0..WDT_MAP),
                    rng.random_range(10.0..max_tunnel_length),
                ]
            })
            .collect();
        let mut sinister_diagonal_lines: Vec<[f32; 3]> = (0..tunnel_per_category)
            .map(|_| {
                [
                    rng.random_range(HGT_TUNNEL..HGT_MAP),
                    rng.random_range(0.0..WDT_MAP),
                    rng.random_range(10.0..max_tunnel_length),
                ]
            })
            .collect();
        // Sort each vector by first f32 in it (y-coordinate).
        horizontal_lines.sort_by(|a, b| a[1].partial_cmp(&b[1]).unwrap());
        baroque_diagonal_lines.sort_by(|a, b| a[1].partial_cmp(&b[1]).unwrap());
        sinister_diagonal_lines.sort_by(|a, b| a[1].partial_cmp(&b[1]).unwrap());
        Map {
            horizontal_lines,
            baroque_diagonal_lines,
            sinister_diagonal_lines,
        }
    }
}

#[derive(Clone, Debug)]
pub struct JumpRoute {
    pub id_target: usize,
    pub x_jump_start_position: f32,
}

#[derive(Clone, Debug, Default)]
pub struct Floor {
    pub top_left: Position2,
    pub top_right: Position2,
    pub bottom_right: Position2,
    pub bottom_left: Position2,
    pub id_left_walking_neighbor: Option<usize>,
    pub id_right_walking_neighbor: Option<usize>,
    pub id_left_digging_neighbor: Option<usize>,
    pub id_right_digging_neighbor: Option<usize>,
    pub id_jump_neighbors: Vec<JumpRoute>, // Only neighbors that aren't reachable by digging or walking.
}

#[derive(Debug, Clone, Default)]
pub struct Position2 {
    pub x: f32,
    pub y: f32,
}

impl Floor {
    pub fn new(x1: f32, y1: f32, x2: f32, y2: f32, x3: f32, y3: f32, x4: f32, y4: f32) -> Floor {
        Floor {
            top_left: Position2 { x: x1, y: y1 },
            top_right: Position2 { x: x2, y: y2 },
            bottom_right: Position2 { x: x3, y: y3 },
            bottom_left: Position2 { x: x4, y: y4 },
            id_left_walking_neighbor: None,
            id_right_walking_neighbor: None,
            id_left_digging_neighbor: None,
            id_right_digging_neighbor: None,
            id_jump_neighbors: Vec::new(),
        }
    }
}

pub fn weightless_breadth_first_search(
    graph: &HashMap<usize, Vec<usize>>,
    start: usize,
    end: usize,
) -> Option<Vec<usize>> {
    let mut queue: VecDeque<Vec<usize>> = VecDeque::new();
    let mut visited: Vec<usize> = Vec::new();
    if start == end {
        return Some(vec![]);
    }
    queue.push_back(vec![start]);
    while let Some(path) = queue.pop_front() {
        let node = path.last().unwrap();
        if !visited.contains(node) {
            if let Some(connected_nodes) = graph.get(node) {
                for connected_node in connected_nodes {
                    let mut next_path = path.clone();
                    next_path.push(*connected_node);
                    queue.push_back(next_path.clone());

                    if *connected_node == end {
                        return Some(next_path);
                    }
                }
            }
            visited.push(*node);
        }
    }
    None
}

fn main() {
    let mut app = App::new();
    app.add_plugins(DefaultPlugins).add_systems(Startup, setup);
    app.insert_resource(Map::default());
    app.run();
}

fn mass_mover() {}

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut map: ResMut<Map>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    // Camera.
    commands.spawn((
        Camera2d,
        Transform::from_xyz(WDT_MAP / 2.0, -HGT_MAP / 2.0, 0.0),
    ));

    // Background.
    let texture_earth = asset_server.load("texture_earth.png");
    commands.spawn((
        Sprite {
            image: texture_earth.clone(),
            ..default()
        },
        Transform::from_xyz(WDT_MAP / 2.0, -HGT_MAP / 2.0, 0.0),
    ));

    // Tunnels.
    *map = Map::default();
    for tunnel in &map.horizontal_lines {
        commands.spawn((
            Mesh2d(meshes.add(Circle::new(HGT_TUNNEL / 2.0))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0] + HGT_TUNNEL / 2.0, 0.0001 * tunnel[0]),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Circle::new(HGT_TUNNEL / 2.0))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(
                tunnel[1] + tunnel[2],
                -tunnel[0] + HGT_TUNNEL / 2.0,
                0.0001 * tunnel[0],
            ),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Triangle2d::new(
                Vec2::new(0.0, 0.0),
                Vec2::new(0.0, HGT_TUNNEL),
                Vec2::new(tunnel[2], HGT_TUNNEL),
            ))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0], 0.0001 * tunnel[0]),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Triangle2d::new(
                Vec2::new(0.0, 0.0),
                Vec2::new(tunnel[2], HGT_TUNNEL),
                Vec2::new(tunnel[2], 0.0),
            ))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0], 0.0001 * tunnel[0]),
        ));
    }
    for tunnel in &map.baroque_diagonal_lines {
        commands.spawn((
            Mesh2d(meshes.add(Circle::new(HGT_TUNNEL / 2.0))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0] + HGT_TUNNEL / 2.0, 0.0001 * tunnel[0]),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Circle::new(HGT_TUNNEL / 2.0))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(
                tunnel[1] + tunnel[2],
                -tunnel[0] + tunnel[2] + HGT_TUNNEL / 2.0,
                0.0001 * tunnel[0],
            ),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Triangle2d::new(
                Vec2::new(0.0, 0.0),
                Vec2::new(0.0, HGT_TUNNEL),
                Vec2::new(tunnel[2], tunnel[2] + HGT_TUNNEL),
            ))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0], 0.0001 * tunnel[0]),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Triangle2d::new(
                Vec2::new(0.0, 0.0),
                Vec2::new(tunnel[2], tunnel[2] + HGT_TUNNEL),
                Vec2::new(tunnel[2], tunnel[2]),
            ))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0], 0.0001 * tunnel[0]),
        ));
    }
    for tunnel in &map.sinister_diagonal_lines {
        commands.spawn((
            Mesh2d(meshes.add(Circle::new(HGT_TUNNEL / 2.0))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0] + HGT_TUNNEL / 2.0, 0.0001 * tunnel[0]),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Circle::new(HGT_TUNNEL / 2.0))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(
                tunnel[1] + tunnel[2],
                -tunnel[0] - tunnel[2] + HGT_TUNNEL / 2.0,
                0.0001 * tunnel[0],
            ),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Triangle2d::new(
                Vec2::new(0.0, 0.0),
                Vec2::new(0.0, HGT_TUNNEL),
                Vec2::new(tunnel[2], HGT_TUNNEL - tunnel[2]),
            ))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0], 0.0001 * tunnel[0]),
        ));
        commands.spawn((
            Mesh2d(meshes.add(Triangle2d::new(
                Vec2::new(0.0, 0.0),
                Vec2::new(tunnel[2], HGT_TUNNEL - tunnel[2]),
                Vec2::new(tunnel[2], -tunnel[2]),
            ))),
            MeshMaterial2d(materials.add(Color::srgb(0.2, 0.1, 0.05))),
            Transform::from_xyz(tunnel[1], -tunnel[0], 0.0001 * tunnel[0]),
        ));
    }

    // Humanoids.
    let texture_player = asset_server.load("player.png");
    commands.spawn((
        Sprite {
            image: texture_player.clone(),
            ..default()
        },
        Transform::from_xyz(50.0, 50.0, 0.0),
        ControledByAI,
        Action::Idle,
        GazeDirection::Left,
        CurrentTunnel([0, 0, 0]),
    ));
    commands.spawn((
        Sprite {
            image: texture_player.clone(),
            ..default()
        },
        Transform::from_xyz(0.0, 0.0 + HGT_HUMANOID / 2.0, 1.0),
        ControledByPlayer,
        Action::Idle,
        GazeDirection::Left,
        CurrentTunnel([0, 0, 0]),
    ));

    // HUD.
    commands.spawn((
        Text::new(
            "HGT_HUMANOID = ".to_owned()
                + &HGT_HUMANOID.to_string()
                + "\nHGT_JUMP_PARABOLA = "
                + &HGT_JUMP_PARABOLA.to_string()
                + "\nWDT_JUMP_PARABOLA = "
                + &WDT_JUMP_PARABOLA.to_string()
                + "\nSPEED_WALKING = "
                + &SPEED_WALKING.to_string()
                + "\nAMOUNT_AIS = "
                + &AMOUNT_AIS.to_string(),
        ),
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(12.0),
            left: Val::Px(12.0),
            ..default()
        },
    ));
}

fn keyboard_control(
    keyboard_input: Res<ButtonInput<KeyCode>>,
    map: Res<Map>,
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut humanoids: Query<
        (&mut Action, &mut GazeDirection),
        (With<ControledByPlayer>, Without<ControledByAI>),
    >,
    mut _ai_players: Query<(&mut Transform,), (With<ControledByAI>, Without<ControledByPlayer>)>,
) {
    for (mut action, mut direction) in &mut humanoids {
        if keyboard_input.pressed(KeyCode::ArrowLeft)
            || keyboard_input.pressed(KeyCode::KeyA)
            || keyboard_input.pressed(KeyCode::ArrowRight)
            || keyboard_input.pressed(KeyCode::KeyD)
            || keyboard_input.pressed(KeyCode::ArrowDown)
            || keyboard_input.pressed(KeyCode::KeyS)
        {
            if keyboard_input.pressed(KeyCode::ArrowRight) || keyboard_input.pressed(KeyCode::KeyD)
            {
                *action = Action::WalkingRight;
                *direction = GazeDirection::Right;
            } else if keyboard_input.pressed(KeyCode::ArrowLeft)
                || keyboard_input.pressed(KeyCode::KeyA)
            {
                *action = Action::WalkingLeft;
                *direction = GazeDirection::Left;
            } else if keyboard_input.pressed(KeyCode::ArrowDown)
                || keyboard_input.pressed(KeyCode::KeyS)
            {
                *action = Action::Idle;
            }
        }
        if keyboard_input.pressed(KeyCode::ArrowUp) || keyboard_input.pressed(KeyCode::KeyW) {
            if *action == Action::Idle {
                //*action = Action::Falling;
            }
            if *action == Action::Digging {
                // Nach oben graben.
            }
        }
        if keyboard_input.pressed(KeyCode::ArrowDown) || keyboard_input.pressed(KeyCode::KeyS) {
            if *action == Action::Digging {
                // Nach unten graben.
            }
        }
        if keyboard_input.pressed(KeyCode::ControlLeft)
            || keyboard_input.pressed(KeyCode::ControlRight)
        {
            if *action == Action::Idle {
                //*action = Action::Digging;
            } else if *action == Action::Digging {
                //*action = Action::Walking;
            }
        }
    }
}
