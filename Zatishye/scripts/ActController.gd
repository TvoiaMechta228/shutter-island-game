extends Node3D

@export var intro_dialogue: String = ""
@export var ambient: String = "drone"

func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	if ambient != "": AudioManager.play_ambient(ambient)
	if intro_dialogue != "":
		var key := "seen_" + intro_dialogue
		if not GameManager.get_flag(key):
			GameManager.set_flag(key, true)
			await get_tree().process_frame
			var lines = DialogueManager.load_dialogue(intro_dialogue)
			if lines.size() > 0:
				DialogueManager.start_dialogue(lines)
