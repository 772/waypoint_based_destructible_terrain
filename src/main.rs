#![allow(clippy::type_complexity, clippy::collapsible_if)]

use bevy::prelude::*;
use bevy::sprite::{Wireframe2dConfig, Wireframe2dPlugin};
use waypoint_based_destructible_terrain::*;

#[derive(Component)]
pub struct ControledByPlayer;
#[derive(Component)]
pub struct ControledByAI;
#[derive(Component)]
pub struct CurrentFloor(pub Option<Floor>);
#[derive(Debug, Resource)]
pub struct Floors(pub Vec<Floor>);

fn main() {
    let mut app = App::new();
    app.add_plugins((DefaultPlugins, Wireframe2dPlugin::default()))
    .add_systems(Startup, setup);
    app.add_systems(Update, keyboard_control);
    app.add_systems(Update, mass_mover);
    app.add_systems(Update, control_ai);
    app.insert_resource(Floors(Vec::new()));
    app.run();
}

pub fn mass_mover(
    mut humanoids: Query<
        (
            &mut Transform,
            &mut Action,
            &mut CurrentFloor,
            &mut GazeDirection,
        ),
        With<Humanoid>,
    >,
    all_floors: ResMut<Floors>,
) {
    // Walking.
    for (mut humanoid_transform, mut action, mut current_floor, mut gaze_direction) in
        &mut humanoids
    {
        let target_position_x;
        let target_position_y;
        if *action == Action::WalkingLeft {
            target_position_x = current_floor.0.clone().unwrap().bottom_left.x;
            target_position_y = current_floor.0.clone().unwrap().bottom_left.y + HGT_HUMANOID / 2.0;
        } else if *action == Action::WalkingRight {
            target_position_x = current_floor.0.clone().unwrap().bottom_right.x;
            target_position_y =
                current_floor.0.clone().unwrap().bottom_right.y + HGT_HUMANOID / 2.0;
        } else {
            continue;
        }
        let current_position_x = humanoid_transform.translation[0];
        let current_position_y = humanoid_transform.translation[1];
        let diff_x = target_position_x - current_position_x;
        let diff_y = target_position_y - current_position_y;
        let distance = (diff_x * diff_x + diff_y * diff_y).sqrt();
        if distance > SPEED_WALKING {
            let dir_x = diff_x / distance;
            let dir_y = diff_y / distance;
            let movement_x = dir_x * SPEED_WALKING;
            let movement_y = dir_y * SPEED_WALKING;
            humanoid_transform.translation[0] += movement_x;
            humanoid_transform.translation[1] += movement_y;
        } else {
            humanoid_transform.translation[0] = target_position_x;
            humanoid_transform.translation[1] = target_position_y;
            if *gaze_direction == GazeDirection::Left {
                if current_floor
                    .0
                    .clone()
                    .unwrap()
                    .id_left_walking_neighbor
                    .is_some()
                {
                    *current_floor = CurrentFloor(Some(
                        all_floors.0[current_floor
                            .0
                            .clone()
                            .unwrap()
                            .id_left_walking_neighbor
                            .unwrap()]
                        .clone(),
                    ));
                } else {
                    *action = Action::WalkingRight;
                    *gaze_direction = GazeDirection::Right;
                }
            } else if current_floor
                .0
                .clone()
                .unwrap()
                .id_right_walking_neighbor
                .is_some()
            {
                *current_floor = CurrentFloor(Some(
                    all_floors.0[current_floor
                        .0
                        .clone()
                        .unwrap()
                        .id_right_walking_neighbor
                        .unwrap()]
                    .clone(),
                ));
            } else {
                *action = Action::WalkingLeft;
                *gaze_direction = GazeDirection::Left;
            }
        }
    }
}

pub fn control_ai(mut humanoids: Query<&mut Action, With<ControledByAI>>) {
    for mut action in &mut humanoids {
        if *action == Action::Idle {
            *action = Action::WalkingLeft;
        }
    }
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

#[derive(Component)]
pub struct Humanoid {
    pub current_path: Vec<usize>,
}

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut all_floors: ResMut<Floors>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    // Camera.
    commands.spawn(Camera2d);

    // Background.
    let texture_earth = asset_server.load("texture_earth.png");
    commands.spawn((
        Sprite {
            image: texture_earth.clone(),
            ..default()
        },
        Transform::from_xyz(0.0, 0.0, 0.0),
        GlobalTransform::from_xyz(0.0, 0.0, 0.0),
    ));

    // Tunnel.
    let mut floors: Vec<Floor> = vec![
        Floor::new(
            -640.0,
            100.0 + HGT_TUNNEL,
            -100.0,
            0.0 + HGT_TUNNEL,
            -100.0,
            0.0,
            -640.0,
            100.0,
        ),
        Floor::new(
            -100.0,
            0.0 + HGT_TUNNEL,
            0.0,
            0.0 + HGT_TUNNEL,
            0.0,
            0.0,
            -100.0,
            0.0,
        ),
        Floor::new(
            0.0,
            0.0 + HGT_TUNNEL,
            300.0,
            100.0 + HGT_TUNNEL,
            300.0,
            100.0,
            0.0,
            0.0,
        ),
        Floor::new(
            300.0,
            100.0 + HGT_TUNNEL,
            640.0,
            -200.0 + HGT_TUNNEL,
            640.0,
            -200.0,
            300.0,
            100.0,
        ),
    ];
    floors[0].id_right_walking_neighbor = Some(1);
    floors[1].id_left_walking_neighbor = Some(0);
    floors[1].id_right_walking_neighbor = Some(2);
    floors[2].id_left_walking_neighbor = Some(1);
    floors[2].id_right_walking_neighbor = Some(3);
    floors[3].id_left_walking_neighbor = Some(2);
    *all_floors = Floors(floors.clone());
    let mut shapes = Vec::new();
    for floor in &floors {
        shapes.push(meshes.add(Triangle2d::new(
            Vec2::new(floor.bottom_left.x, floor.bottom_left.y),
            Vec2::new(floor.top_left.x, floor.top_left.y),
            Vec2::new(floor.bottom_right.x, floor.bottom_right.y),
        )));
        shapes.push(meshes.add(Triangle2d::new(
            Vec2::new(floor.top_left.x, floor.top_left.y),
            Vec2::new(floor.top_right.x, floor.top_right.y),
            Vec2::new(floor.bottom_right.x, floor.bottom_right.y),
        )));
    }
    for (i, shape) in shapes.into_iter().enumerate() {
        let color = Color::srgba(0.0, 0.0, 0.0, 0.7);
        commands.spawn((
            Mesh2d(shape),
            MeshMaterial2d(materials.add(color)),
            Transform::from_xyz(0.0, 0.0, 0.1 + 0.001 * (i as f32)),
            GlobalTransform::from_xyz(0.0, 0.0, i as f32),
        ));
    }

    // HUD.
    commands.spawn((
        Text::new(
            "Press space to toggle wireframes. Arrow keys to move the player.\nHGT_HUMANOID = "
                .to_owned()
                + &HGT_HUMANOID.to_string()
                + "\nHGT_JUMP_PARABOLA = "
                + &HGT_JUMP_PARABOLA.to_string()
                + "\nWDT_JUMP_PARABOLA = "
                + &WDT_JUMP_PARABOLA.to_string()
                + "\nSPEED_WALKING = "
                + &SPEED_WALKING.to_string()
                + "\nAdd more AI humanoids with key [1]",
        ),
        Node {
            position_type: PositionType::Absolute,
            top: Val::Px(12.0),
            left: Val::Px(12.0),
            ..default()
        },
    ));

    // Humanoids.
    let texture_player = asset_server.load("player.png");
    commands.spawn((
        Sprite {
            image: texture_player.clone(),
            ..default()
        },
        Transform::from_xyz(-50.0, 0.0 + HGT_HUMANOID / 2.0, 1.0),
        Humanoid {
            current_path: Vec::new(),
        },
        ControledByAI,
        Action::Idle,
        GazeDirection::Left,
        CurrentFloor(Some(floors[2].clone())),
    ));
    commands.spawn((
        Sprite {
            image: texture_player.clone(),
            ..default()
        },
        Transform::from_xyz(0.0, 0.0 + HGT_HUMANOID / 2.0, 1.0),
        Humanoid {
            current_path: Vec::new(),
        },
        ControledByPlayer,
        Action::Idle,
        GazeDirection::Left,
        CurrentFloor(Some(floors[2].clone())),
    ));
}

fn keyboard_control(
    keyboard_input: Res<ButtonInput<KeyCode>>,
    all_floors: ResMut<Floors>,
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut humanoids: Query<
        (&mut Action, &mut GazeDirection),
        (With<ControledByPlayer>, Without<ControledByAI>),
    >,
    mut _ai_players: Query<(&mut Transform,), (With<ControledByAI>, Without<ControledByPlayer>)>,
    mut wireframe_config: ResMut<Wireframe2dConfig>,
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
        if keyboard_input.just_pressed(KeyCode::Space) {
            wireframe_config.global = !wireframe_config.global;
        }
        if keyboard_input.just_pressed(KeyCode::Digit1) {
            let texture_player = asset_server.load("player.png");
            commands.spawn((
                Sprite {
                    image: texture_player.clone(),
                    ..default()
                },
                Transform::from_xyz(-50.0, 0.0 + HGT_HUMANOID / 2.0, 1.0),
                Humanoid {
                    current_path: Vec::new(),
                },
                ControledByAI,
                Action::Idle,
                GazeDirection::Left,
                CurrentFloor(Some(all_floors.0[2].clone())),
            ));
        }
    }
}
