extends CanvasLayer

var sanity: float = 100.0
@onready var overlay: ColorRect = $Overlay

func drain(n: float) -> void:
	sanity = clampf(sanity - n, 0.0, 100.0)
	_update()

func _update() -> void:
	var t := (100.0 - sanity) / 100.0
	overlay.color = Color(0.4, 0.02, 0.02, t * 0.55)
