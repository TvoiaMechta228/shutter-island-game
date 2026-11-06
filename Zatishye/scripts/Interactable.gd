extends StaticBody3D

@export var dialogue_path: String = ""
@export var one_time: bool = true
@export var requires_flag: String = ""
@export var sets_flag: String = ""
@export var ending: String = ""
@export var clue: String = ""

var used: bool = false

func interact() -> void:
	if one_time and used: return
	if requires_flag != "" and not GameManager.get_flag(requires_flag): return
	used = true
	if sets_flag != "": GameManager.set_flag(sets_flag, true)
	if clue != "": GameManager.add_clue(clue)
	if dialogue_path != "":
		var lines = DialogueManager.load_dialogue(dialogue_path)
		if lines.size() > 0:
			DialogueManager.start_dialogue(lines, ending)
