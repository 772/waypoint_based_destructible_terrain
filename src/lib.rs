#![allow(clippy::too_many_arguments)]

use bevy::prelude::*;

pub const HGT_TUNNEL: f32 = 60.0;
pub const HGT_HUMANOID: f32 = 40.0;
pub const SPEED_WALKING: f32 = 3.0;
pub const _SPEED_DIGGING: f32 = 2.0;
#[derive(Debug, Resource)]
pub struct Floors(pub Vec<Floor>);
#[derive(Component)]
pub struct IsHumanoid;
#[derive(Component)]
pub struct ControledByPlayer;
#[derive(Component)]
pub struct CurrentFloor(pub Option<Floor>);

#[derive(Component, Debug)]
pub enum GazeDirection {
    Left,
    Right,
}

#[derive(Component, Debug, PartialEq)]
pub enum Action {
    Walking,
    _Falling,
    Digging,
}

#[derive(Clone, Debug)]
pub struct Floor {
    pub top_left: Position2,
    pub top_right: Position2,
    pub bottom_right: Position2,
    pub bottom_left: Position2,
    pub id_left_neighbor: Option<usize>,
    pub id_right_neighbor: Option<usize>,
}

#[derive(Debug, Clone)]
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
            id_left_neighbor: None,
            id_right_neighbor: None,
        }
    }
}
