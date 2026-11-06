extends Node

const ACTS = [
	"res://scenes/Act1_Ferry.tscn",
	"res://scenes/Act2_Asylum.tscn",
	"res://scenes/Act3_Cell.tscn",
	"res://scenes/Act4_Lighthouse.tscn",
	"res://scenes/Act5_Finale.tscn",
]

var current_act: int = -1
var flags: Dictionary = {}
var clues: Array = []

func _ready() -> void:
	var actions = {
		"move_forward": KEY_W,
		"move_back": KEY_S,
		"move_left": KEY_A,
		"move_right": KEY_D,
		"interact": KEY_E,
		"sprint": KEY_SHIFT,
	}
	for action in actions:
		if not InputMap.has_action(action):
			InputMap.add_action(action)
		var ev := InputEventKey.new()
		ev.physical_keycode = actions[action]
		InputMap.action_add_event(action, ev)

func load_act(index: int) -> void:
	if has_node("/root/SaveSystem") and index > 0:
		SaveSystem.save_game()
	current_act = index
	if index < 0 or index >= ACTS.size():
		get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")
		return
	get_tree().paused = false
	get_tree().change_scene_to_file(ACTS[index])

func next_act() -> void:
	load_act(current_act + 1)

func set_flag(key: String, value = true) -> void:
	flags[key] = value

func get_flag(key: String, default = false):
	return flags.get(key, default)

func add_clue(clue: String) -> void:
	if not clues.has(clue):
		clues.append(clue)
		print("[Clue] + ", clue)
		if has_node("/root/ClueInventory"):
			ClueInventory.refresh()
