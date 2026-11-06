extends CanvasLayer

signal dialogue_finished

@onready var panel: PanelContainer = $Panel
@onready var speaker_label: Label = $Panel/VBox/Speaker
@onready var text_label: Label = $Panel/VBox/Text
@onready var hint: Label = $Panel/VBox/Hint

var _lines: Array = []
var _i: int = 0
var _active: bool = false
var _ending: String = ""

func _ready() -> void:
	panel.hide()
	process_mode = Node.PROCESS_MODE_ALWAYS

func load_dialogue(path: String) -> Array:
	if not FileAccess.file_exists(path): return []
	var f := FileAccess.open(path, FileAccess.READ)
	if f == null: return []
	var data = JSON.parse_string(f.get_as_text())
	if data is Dictionary and data.has("lines"): return data["lines"]
	return []

func start_dialogue(lines: Array, ending: String = "") -> void:
	if _active or lines.is_empty():
		dialogue_finished.emit()
		return
	_lines = lines
	_i = 0
	_active = true
	_ending = ending
	panel.show()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	get_tree().paused = true
	_show()

func _show() -> void:
	if _i >= _lines.size():
		_end()
		return
	var ln: Dictionary = _lines[_i]
	speaker_label.text = String(ln.get("speaker", ""))
	text_label.text = String(ln.get("text", ""))
	hint.text = "[E] завершить" if _i == _lines.size() - 1 else "[E] далее"
	if has_node("/root/AudioManager"):
		AudioManager.play_voice()

func _unhandled_input(e: InputEvent) -> void:
	if not _active: return
	if e.is_action_pressed("interact"):
		get_viewport().set_input_as_handled()
		_i += 1
		_show()

func _end() -> void:
	_active = false
	panel.hide()
	get_tree().paused = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	var m := _ending
	_ending = ""
	dialogue_finished.emit()
	if m == "monster" or m == "human":
		await get_tree().create_timer(0.3).timeout
		_show_ending(m)

func _show_ending(which: String) -> void:
	panel.show()
	if which == "monster":
		speaker_label.text = "— КОНЕЦ: МОНСТР —"
		text_label.text = "Бред вернулся."
	else:
		speaker_label.text = "— КОНЕЦ: ЧЕЛОВЕК —"
		text_label.text = "Осознанный выбор."
	hint.text = ""
	await get_tree().create_timer(5.0).timeout
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")
