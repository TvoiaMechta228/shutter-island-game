extends CharacterBody3D

@export var walk_speed: float = 3.5
@export var sprint_speed: float = 6.0
@export var mouse_sensitivity: float = 0.0022
@export var gravity: float = 20.0

@onready var camera: Camera3D = $Camera3D
@onready var ray: RayCast3D = $Camera3D/RayCast3D

var _step_cd: float = 0.0
var _paused: bool = false
var _pause_ui: CanvasLayer = null

func _ready() -> void:
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)
	ray.target_position = Vector3(0, 0, -3.5)
	_build_pause_ui()

func _build_pause_ui() -> void:
	_pause_ui = CanvasLayer.new()
	_pause_ui.layer = 20
	_pause_ui.visible = false
	add_child(_pause_ui)

	var dim := ColorRect.new()
	dim.color = Color(0, 0, 0, 0.75)
	dim.set_anchors_preset(Control.PRESET_FULL_RECT)
	_pause_ui.add_child(dim)

	var vbox := VBoxContainer.new()
	vbox.set_anchors_preset(Control.PRESET_CENTER)
	vbox.offset_left = -180
	vbox.offset_top = -160
	vbox.offset_right = 180
	vbox.offset_bottom = 160
	vbox.add_theme_constant_override("separation", 18)
	_pause_ui.add_child(vbox)

	var title := Label.new()
	title.text = "ПАУЗА"
	title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	title.add_theme_font_size_override("font_size", 48)
	title.add_theme_color_override("font_color", Color(0.85, 0.2, 0.2))
	vbox.add_child(title)

	var resume_btn := _mk_btn("Продолжить")
	resume_btn.pressed.connect(_resume)
	vbox.add_child(resume_btn)

	var menu_btn := _mk_btn("Главное меню")
	menu_btn.pressed.connect(_to_menu)
	vbox.add_child(menu_btn)

	var quit_btn := _mk_btn("Выход")
	quit_btn.pressed.connect(func(): get_tree().quit())
	vbox.add_child(quit_btn)

func _mk_btn(text: String) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(0, 55)
	b.add_theme_font_size_override("font_size", 22)
	return b

func _toggle_pause() -> void:
	if _paused:
		_resume()
	else:
		_pause()

func _pause() -> void:
	_paused = true
	_pause_ui.visible = true
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)

func _resume() -> void:
	_paused = false
	_pause_ui.visible = false
	Input.set_mouse_mode(Input.MOUSE_MODE_CAPTURED)

func _to_menu() -> void:
	_paused = false
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	get_tree().change_scene_to_file("res://scenes/MainMenu.tscn")

func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("ui_cancel"):
		_toggle_pause()
		return
	if _paused:
		return
	if event is InputEventMouseMotion and Input.get_mouse_mode() == Input.MOUSE_MODE_CAPTURED:
		rotate_y(-event.relative.x * mouse_sensitivity)
		camera.rotate_x(-event.relative.y * mouse_sensitivity)
		camera.rotation.x = clampf(camera.rotation.x, -1.4, 1.4)
	elif event.is_action_pressed("interact"):
		if ray.is_colliding():
			var t = ray.get_collider()
			if t and t.has_method("interact"):
				t.interact()
	elif event.is_action_pressed("toggle_inventory"):
		if has_node("/root/ClueInventory"):
			ClueInventory.toggle()

func _physics_process(delta: float) -> void:
	if _paused:
		return
	if not is_on_floor():
		velocity.y -= gravity * delta
	else:
		velocity.y = 0.0
	var d := Input.get_vector("move_left", "move_right", "move_forward", "move_back")
	var dir := (transform.basis * Vector3(d.x, 0, d.y)).normalized()
	var sp := sprint_speed if Input.is_action_pressed("sprint") else walk_speed
	velocity.x = dir.x * sp
	velocity.z = dir.z * sp
	move_and_slide()
	_step_cd -= delta
	if is_on_floor() and Vector2(velocity.x, velocity.z).length() > 0.5 and _step_cd <= 0.0:
		_step_cd = 0.45
		if has_node("/root/AudioManager"):
			AudioManager.play_step()
