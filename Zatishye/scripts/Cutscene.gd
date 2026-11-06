extends Node3D

var cam: Camera3D
var speed: float = 25.0

func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	Input.set_mouse_mode(Input.MOUSE_MODE_VISIBLE)
	
	if has_node("/root/AudioManager"):
		AudioManager.play_ambient("sea")
	
	cam = Camera3D.new()
	cam.position = Vector3(0, 8, 200)
	cam.look_at(Vector3(0, 4, 100))
	add_child(cam)
	
	var cl := CanvasLayer.new()
	var lbl := Label.new()
	lbl.text = "Сентябрь 1954 года.\nОстров Эшклифф."
	lbl.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	lbl.vertical_alignment = VERTICAL_ALIGNMENT_CENTER
	lbl.add_theme_font_size_override("font_size", 36)
	lbl.set_anchors_preset(Control.PRESET_FULL_RECT)
	cl.add_child(lbl)
	add_child(cl)

func _process(delta: float) -> void:
	if cam.position.z > 140:
		cam.position.z -= speed * delta
	else:
		if has_node("/root/AudioManager"):
			AudioManager.stop_all()
		get_tree().change_scene_to_file("res://scenes/World.tscn")
