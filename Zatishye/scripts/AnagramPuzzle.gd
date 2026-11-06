extends Control

signal solved

@onready var inp: LineEdit = $VBox/Input
@onready var hint: Label = $VBox/Hint
@onready var sub: Button = $VBox/Buttons/Submit
@onready var clo: Button = $VBox/Buttons/Close

var _t: String = ""

func _ready() -> void:
	hide()
	process_mode = Node.PROCESS_MODE_ALWAYS
	sub.pressed.connect(_submit)
	clo.pressed.connect(_close)
	inp.text_submitted.connect(func(_s): _submit())

func open(target: String, hint_text: String) -> void:
	_t = target.to_upper().replace(" ", "")
	hint.text = hint_text
	inp.text = ""
	show()
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	get_tree().paused = true
	inp.grab_focus()

func _submit() -> void:
	var g := inp.text.to_upper().replace(" ", "")
	if g == _t:
		hint.text = "ВЕРНО."
		await get_tree().create_timer(1.0).timeout
		solved.emit()
		_close()
	else:
		hint.text = "Не складывается. Попробуйте ещё."
		SanitySystem.drain(5.0)

func _close() -> void:
	hide()
	get_tree().paused = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
