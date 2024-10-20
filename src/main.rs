#![allow(clippy::type_complexity, clippy::collapsible_if)]

use bevy::sprite::Wireframe2dConfig;
use bevy::sprite::Wireframe2dPlugin;
use bevy::{
    prelude::*,
    sprite::{MaterialMesh2dBundle, Mesh2dHandle},
};
use waypoint_based_2d_destructible_terrain::*;

fn main() {
    let mut app = App::new();
    app.add_plugins((DefaultPlugins, Wireframe2dPlugin))
        .add_systems(Startup, setup);
    app.add_systems(Update, keyboard_control);
    app.insert_resource(Floors(Vec::new()));
    app.run();
}

fn setup(
    mut commands: Commands,
    asset_server: Res<AssetServer>,
    mut meshes: ResMut<Assets<Mesh>>,
    mut all_floors: ResMut<Floors>,
    mut materials: ResMut<Assets<ColorMaterial>>,
) {
    // Camera.
    commands.spawn(Camera2dBundle::default());

    // Background.
    let texture_earth = asset_server.load("texture_earth.png");
    commands.spawn(SpriteBundle {
        texture: texture_earth.clone(),
        transform: Transform::from_xyz(0.0, 0.0, 0.0),
        global_transform: GlobalTransform::from_xyz(0.0, 0.0, 0.0),
        ..default()
    });

    // Tunnel.
    let mut floors: Vec<Floor> = vec![
        Floor::new(
            -960.0,
            100.0 + HGT_TUNNEL,
            -500.0,
            100.0 + HGT_TUNNEL,
            -500.0,
            100.0,
            -960.0,
            100.0,
        ),
        Floor::new(
            -500.0,
            100.0 + HGT_TUNNEL,
            -100.0,
            0.0 + HGT_TUNNEL,
            -100.0,
            0.0,
            -500.0,
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
            800.0,
            -200.0 + HGT_TUNNEL,
            800.0,
            -200.0,
            300.0,
            100.0,
        ),
        Floor::new(
            800.0,
            -200.0 + HGT_TUNNEL,
            960.0,
            -200.0 + HGT_TUNNEL,
            960.0,
            -200.0,
            800.0,
            -200.0,
        ),
    ];
    floors[0].id_right_neighbor = Some(1);
    floors[1].id_left_neighbor = Some(0);
    floors[1].id_right_neighbor = Some(2);
    floors[2].id_left_neighbor = Some(1);
    floors[2].id_right_neighbor = Some(3);
    floors[3].id_left_neighbor = Some(2);
    floors[3].id_right_neighbor = Some(4);
    floors[4].id_left_neighbor = Some(3);
    floors[4].id_right_neighbor = Some(5);
    floors[5].id_left_neighbor = Some(4);
    *all_floors = Floors(floors.clone());
    let mut shapes: Vec<Mesh2dHandle> = Vec::new();
    for floor in &floors {
        shapes.push(Mesh2dHandle(meshes.add(Triangle2d::new(
            Vec2::new(floor.bottom_left.x, floor.bottom_left.y),
            Vec2::new(floor.top_left.x, floor.top_left.y),
            Vec2::new(floor.bottom_right.x, floor.bottom_right.y),
        ))));
        shapes.push(Mesh2dHandle(meshes.add(Triangle2d::new(
            Vec2::new(floor.top_left.x, floor.top_left.y),
            Vec2::new(floor.top_right.x, floor.top_right.y),
            Vec2::new(floor.bottom_right.x, floor.bottom_right.y),
        ))));
    }
    for (i, shape) in shapes.into_iter().enumerate() {
        let color = Color::srgba(0.0, 0.0, 0.0, 0.7);
        commands.spawn(MaterialMesh2dBundle {
            mesh: shape,
            material: materials.add(color),
            transform: Transform::from_xyz(0.0, 0.0, 0.1 + 0.001 * (i as f32)),
            global_transform: GlobalTransform::from_xyz(0.0, 0.0, i as f32),
            ..default()
        });
    }

    // HUD.
    commands.spawn(
        TextBundle::from_section(
            "Press space to toggle wireframes. Left / right arrow key to move player.",
            TextStyle::default(),
        )
        .with_style(Style {
            position_type: PositionType::Absolute,
            top: Val::Px(12.0),
            left: Val::Px(12.0),
            ..default()
        }),
    );

    // Humanoids.
    let texture_player = asset_server.load("player.png");
    commands.spawn((
        SpriteBundle {
            texture: texture_player.clone(),
            transform: Transform::from_xyz(-50.0, 0.0 + HGT_HUMANOID / 2.0, 1.0),
            ..default()
        },
        IsHumanoid,
        Action::Walking,
        GazeDirection::Left,
        CurrentFloor(Some(floors[2].clone())),
    ));
    commands.spawn((
        SpriteBundle {
            texture: texture_player.clone(),
            transform: Transform::from_xyz(0.0, 0.0 + HGT_HUMANOID / 2.0, 1.0),
            ..default()
        },
        IsHumanoid,
        ControledByPlayer,
        Action::Walking,
        GazeDirection::Left,
        CurrentFloor(Some(floors[2].clone())),
    ));
}

fn keyboard_control(
    keyboard_input: Res<ButtonInput<KeyCode>>,
    all_floors: ResMut<Floors>,
    mut humanoids: Query<
        (
            &mut Transform,
            &mut Action,
            &mut CurrentFloor,
            &mut GazeDirection,
        ),
        (With<IsHumanoid>, With<ControledByPlayer>),
    >,
    mut wireframe_config: ResMut<Wireframe2dConfig>,
) {
    for (mut humanoid_transform, action, mut current_floor, mut direction) in &mut humanoids {
        if keyboard_input.pressed(KeyCode::ArrowLeft)
            || keyboard_input.pressed(KeyCode::KeyA)
            || keyboard_input.pressed(KeyCode::ArrowRight)
            || keyboard_input.pressed(KeyCode::KeyD)
        {
            if *action == Action::Walking {
                // Spielerposition (humanoid_transform) und Zielposition (current_floor)
                let current_position_x = humanoid_transform.translation[0];
                let current_position_y = humanoid_transform.translation[1];
                let mut target_position_x = current_floor.0.clone().unwrap().bottom_left.x;
                let mut target_position_y =
                    current_floor.0.clone().unwrap().bottom_left.y + HGT_HUMANOID / 2.0;
                if keyboard_input.pressed(KeyCode::ArrowRight)
                    || keyboard_input.pressed(KeyCode::KeyD)
                {
                    *direction = GazeDirection::Right;
                    target_position_x = current_floor.0.clone().unwrap().bottom_right.x;
                    target_position_y =
                        current_floor.0.clone().unwrap().bottom_right.y + HGT_HUMANOID / 2.0;
                    // Left current floor?
                    if current_position_x >= target_position_x
                        && current_floor.0.clone().unwrap().id_right_neighbor.is_some()
                    {
                        let new_id: usize =
                            current_floor.0.clone().unwrap().id_right_neighbor.unwrap();
                        let neighbor: Floor = all_floors.0[new_id].clone();
                        *current_floor = CurrentFloor(Some(neighbor));
                    }
                } else {
                    *direction = GazeDirection::Left;
                    // Left current floor?
                    if current_position_x <= target_position_x
                        && current_floor.0.clone().unwrap().id_left_neighbor.is_some()
                    {
                        let new_id: usize =
                            current_floor.0.clone().unwrap().id_left_neighbor.unwrap();
                        let neighbor: Floor = all_floors.0[new_id].clone();
                        *current_floor = CurrentFloor(Some(neighbor));
                    }
                }
                // Differenzvektor zwischen Spieler und Ziel
                let diff_x = target_position_x - current_position_x;
                let diff_y = target_position_y - current_position_y;
                // Berechne die Länge (Magnitude) des Vektors
                let distance = (diff_x * diff_x + diff_y * diff_y).sqrt();
                // Überprüfe, ob die Distanz größer als ein sehr kleiner Wert ist (um NaN und Nulldivision zu verhindern)
                if distance > 0.0 {
                    // Normiere den Differenzvektor (damit die Länge des Vektors 1 beträgt)
                    let dir_x = diff_x / distance;
                    let dir_y = diff_y / distance;
                    // Bewegung in Richtung Ziel multipliziert mit der Geschwindigkeit
                    let movement_x = dir_x * SPEED_WALKING;
                    let movement_y = dir_y * SPEED_WALKING;
                    // Aktualisiere die Spielerposition
                    humanoid_transform.translation[0] += movement_x;
                    humanoid_transform.translation[1] += movement_y;
                }
            }
            println!(
                "x: {} y: {} action: {:?} Dir: {:?}",
                humanoid_transform.translation[0],
                humanoid_transform.translation[1],
                *action,
                *direction
            );
        }
        if keyboard_input.pressed(KeyCode::ArrowUp) || keyboard_input.pressed(KeyCode::KeyW) {
            if *action == Action::Walking {
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
            if *action == Action::Walking {
                //*action = Action::Digging;
            } else if *action == Action::Digging {
                //*action = Action::Walking;
            }
        }
        if keyboard_input.just_pressed(KeyCode::Space) {
            wireframe_config.global = !wireframe_config.global;
        }
    }
}
