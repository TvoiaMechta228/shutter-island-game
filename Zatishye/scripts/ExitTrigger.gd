extends Area3D

@export var target_act: int = -1
@export var requires_flag: String = ""

func _ready() -> void:
	body_entered.connect(_on_body)

func _on_body(b: Node3D) -> void:
	if b.name != "Player": return
	if requires_flag != "" and not GameManager.get_flag(requires_flag): return
	if target_act >= 0: GameManager.load_act(target_act)
	else: GameManager.next_act()
