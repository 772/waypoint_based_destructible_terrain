#![allow(clippy::too_many_arguments)]

use bevy::prelude::*;
use std::collections::{HashMap, VecDeque};

pub const HGT_HUMANOID: f32 = 40.0;
pub const HGT_JUMP: f32 = 3.0;
pub const SPEED_WALKING: f32 = 3.0;
pub const HGT_TUNNEL: f32 = 60.0;
#[derive(Debug, Resource)]
pub struct Floors(pub Vec<Floor>);
#[derive(Component)]
pub struct IsHumanoid;
#[derive(Component)]
pub struct ControledByPlayer;
#[derive(Component)]
pub struct ControledByAI;
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
    pub id_jump_to_neighbor: Vec<usize>,
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
            id_jump_to_neighbor: Vec::new(),
        }
    }

    pub fn find_path_to_another_floor(self, goal: usize) -> Option<Vec<usize>> {
        let mut path = Vec::new();
        if self.id_left_neighbor == Some(goal)
            || self.id_right_neighbor == Some(goal)
            || self.id_jump_to_neighbor.contains(&goal)
        {
            path.push(goal);
        }
        if path.is_empty() {
            return None;
        }
        Some(path)
    }
}

pub fn weightless_breadth_first_search(
    graph: &HashMap<String, Vec<String>>,
    start: &str,
    end: &str,
) -> Option<Vec<String>> {
    let mut queue: VecDeque<Vec<String>> = VecDeque::new();
    let mut visited: Vec<String> = Vec::new();

    if start == end {
        return Some(vec![]);
    }

    // Die erste Pfadliste mit dem Startknoten initialisieren.
    queue.push_back(vec![start.to_string()]);

    while let Some(path) = queue.pop_front() {
        let node = path.last().unwrap(); // Letztes Element des aktuellen Pfads.

        if !visited.contains(node) {
            // Alle mit dem aktuellen Knoten verbundenen Knoten iterieren.
            if let Some(connected_nodes) = graph.get(node) {
                for connected_node in connected_nodes {
                    let mut next_path = path.clone();
                    next_path.push(connected_node.to_string());
                    queue.push_back(next_path.clone());

                    if connected_node == end {
                        return Some(next_path); // Rückgabe des Pfads, wenn das Ziel gefunden wurde.
                    }
                }
            }
            visited.push(node.clone());
        }
    }
    None
}
