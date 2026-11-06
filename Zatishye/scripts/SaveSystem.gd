extends Node

const SAVE_PATH := "user://save.json"

func save_game() -> void:
	var data := {
		"act": GameManager.current_act,
		"flags": GameManager.flags,
		"clues": GameManager.clues,
	}
	var f := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if f == null: return
	f.store_string(JSON.stringify(data, "\t"))
	f.close()

func load_game() -> bool:
	if not FileAccess.file_exists(SAVE_PATH): return false
	var f := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if f == null: return false
	var data = JSON.parse_string(f.get_as_text())
	f.close()
	if not (data is Dictionary): return false
	GameManager.flags = data.get("flags", {})
	GameManager.clues = data.get("clues", [])
	GameManager.load_act(int(data.get("act", 0)))
	return true

func has_save() -> bool:
	return FileAccess.file_exists(SAVE_PATH)

func delete_save() -> void:
	if has_save():
		DirAccess.remove_absolute(ProjectSettings.globalize_path(SAVE_PATH))
