extends Node3D

var _moon: DirectionalLight3D
var _timer: float = 0.0
var _flash_timer: float = 0.0
var _flashing: bool = false

func setup(moon_node: DirectionalLight3D) -> void:
	_moon = moon_node
	_timer = randf_range(5.0, 10.0)

func _process(delta: float) -> void:
	if not _moon: return
	_timer -= delta
	if _timer <= 0.0 and not _flashing:
		_flashing = true
		_flash_timer = 0.2
		_timer = randf_range(8.0, 15.0)
		_moon.light_energy = 3.0
		_moon.light_color = Color(0.9, 0.9, 1.0)
	if _flashing:
		_flash_timer -= delta
		if _flash_timer <= 0.0:
			_flashing = false
			_moon.light_energy = 0.7
			_moon.light_color = Color(0.6, 0.65, 0.7)
