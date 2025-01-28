#![allow(clippy::too_many_arguments)]

use std::collections::{HashMap, VecDeque};

pub const HGT_HUMANOID: f32 = 40.0;
pub const HGT_JUMP_PARABOLA: f32 = 50.0;
pub const WDT_JUMP_PARABOLA: f32 = 60.0;
pub const SPEED_WALKING: f32 = 3.0;
pub const HGT_TUNNEL: f32 = 60.0;

pub fn jump_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
}

pub fn fall_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
}

pub fn dig_fall_function(x: f32) -> f32 {
    -(4.0 * HGT_JUMP_PARABOLA) / (WDT_JUMP_PARABOLA.powf(2.0)) * x.powf(2.0) + HGT_JUMP_PARABOLA
}

/*
fn main() {
	let mut list = Vec::new();
}
*/

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
