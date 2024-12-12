#![allow(clippy::too_many_arguments)]

use bevy::prelude::*;
use std::collections::{HashMap, VecDeque};

pub const HGT_HUMANOID: f32 = 40.0;
pub const HGT_JUMP_PARABOLA: f32 = 50.0;
pub const WDT_JUMP_PARABOLA: f32 = 60.0;
pub const SPEED_WALKING: f32 = 3.0;
pub const HGT_TUNNEL: f32 = 60.0;
#[derive(Debug, Resource)]
pub struct Floors(pub Vec<Floor>);
#[derive(Component)]
pub struct ControledByPlayer;
#[derive(Component)]
pub struct ControledByAI;
#[derive(Component)]
pub struct CurrentFloor(pub Option<Floor>);

pub fn jump_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
}

pub fn fall_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
}

pub fn dig_fall_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
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
    pub id_jump_neighbor: Vec<JumpRoute>,
    pub id_all: Vec<usize>,
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
            ..default()
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
