extends Area3D

@export var target_position: Vector3 = Vector3.ZERO
@export var requires_flag: String = ""
@export var set_flag: String = ""

var _busy: bool = false

func _ready() -> void:
	body_entered.connect(_on_body)

func _on_body(body: Node3D) -> void:
	if _busy or body.name != "Player":
		return
	if requires_flag != "" and not GameManager.get_flag(requires_flag):
		return
	_busy = true
	if set_flag != "":
		GameManager.set_flag(set_flag, true)
	body.global_position = target_position
	body.velocity = Vector3.ZERO
	await get_tree().create_timer(0.7).timeout
	_busy = false
