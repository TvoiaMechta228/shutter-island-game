extends Node3D

var lighthouse_pivot: Node3D

func _mat(c: Color, rough: float = 0.85, metal: float = 0.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.roughness = rough
	m.metallic = metal
	return m

func _glow(c: Color, energy: float = 2.0) -> StandardMaterial3D:
	var m := StandardMaterial3D.new()
	m.albedo_color = c
	m.emission_enabled = true
	m.emission = c
	m.emission_energy_multiplier = energy
	return m

func _box(parent: Node, pos: Vector3, size: Vector3, mat: Material, rot_y: float = 0.0, collide: bool = true) -> Node3D:
	var body: Node3D
	if collide:
		body = StaticBody3D.new()
		var col := CollisionShape3D.new()
		var shape := BoxShape3D.new()
		shape.size = size
		col.shape = shape
		body.add_child(col)
	else:
		body = Node3D.new()
	body.position = pos
	body.rotation.y = rot_y
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mi.mesh = mesh
	mi.material_override = mat
	body.add_child(mi)
	parent.add_child(body)
	return body

func _cyl(parent: Node, pos: Vector3, radius: float, height: float, mat: Material, collide: bool = true) -> Node3D:
	var body: Node3D
	if collide:
		body = StaticBody3D.new()
		var col := CollisionShape3D.new()
		var shape := CylinderShape3D.new()
		shape.radius = radius
		shape.height = height
		col.shape = shape
		body.add_child(col)
	else:
		body = Node3D.new()
	body.position = pos
	var mi := MeshInstance3D.new()
	var mesh := CylinderMesh.new()
	mesh.top_radius = radius
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = 16
	mi.mesh = mesh
	mi.material_override = mat
	body.add_child(mi)
	parent.add_child(body)
	return body

func _cone(parent: Node, pos: Vector3, radius: float, height: float, mat: Material) -> void:
	var mi := MeshInstance3D.new()
	mi.position = pos
	var mesh := CylinderMesh.new()
	mesh.top_radius = 0
	mesh.bottom_radius = radius
	mesh.height = height
	mesh.radial_segments = 8
	mi.mesh = mesh
	mi.material_override = mat
	parent.add_child(mi)

func _light(parent: Node, pos: Vector3, color: Color, energy: float, rng: float) -> void:
	var l := OmniLight3D.new()
	l.position = pos
	l.light_color = color
	l.light_energy = energy
	l.omni_range = rng
	parent.add_child(l)

func _npc(parent: Node, pos: Vector3, script_path: String, dlg: String, flag: String, clue: String, color: Color) -> void:
	var body := StaticBody3D.new()
	body.position = pos
	var sc = load(script_path)
	if sc:
		body.set_script(sc)
		if dlg != "": body.set("dialogue_path", dlg)
		if flag != "": body.set("sets_flag", flag)
		if clue != "": body.set("clue", clue)
	var col := CollisionShape3D.new()
	var shape := BoxShape3D.new()
	shape.size = Vector3(1, 2, 1)
	col.shape = shape
	body.add_child(col)
	var mi := MeshInstance3D.new()
	var mesh := CapsuleMesh.new()
	mesh.radius = 0.35
	mesh.height = 2.0
	mi.mesh = mesh
	mi.material_override = _mat(color, 0.7)
	body.add_child(mi)
	parent.add_child(body)

func _ready() -> void:
	print("[WorldBuilder] Building...")
	_build_environment()
	_build_sea_and_island()
	_build_dock()
	_build_main_hospital()
	_build_womens_wing()
	_build_c_block()
	_build_cemetery()
	_build_cave()
	_build_lighthouse()
	_build_trees()
	_build_npcs()
	_build_rain()
	_spawn_player()
	print("[WorldBuilder] Built!")

func _build_environment() -> void:
	var sky_mat := ProceduralSkyMaterial.new()
	sky_mat.sky_top_color = Color(0.05, 0.06, 0.08)
	sky_mat.sky_horizon_color = Color(0.15, 0.16, 0.18)
	var sky := Sky.new()
	sky.sky_material = sky_mat
	var env := Environment.new()
	env.background_mode = Environment.BG_SKY
	env.sky = sky
	env.ambient_light_source = Environment.AMBIENT_SOURCE_COLOR
	env.ambient_light_color = Color(0.5, 0.55, 0.6)
	env.ambient_light_energy = 0.6
	env.tonemap_mode = Environment.TONE_MAPPER_FILMIC
	env.fog_enabled = true
	env.fog_light_color = Color(0.12, 0.13, 0.15)
	env.fog_density = 0.04
	var we := WorldEnvironment.new()
	we.environment = env
	add_child(we)
	var sun := DirectionalLight3D.new()
	sun.rotation_degrees = Vector3(-60, 30, 0)
	sun.light_color = Color(0.6, 0.65, 0.7)
	sun.light_energy = 0.7
	sun.shadow_enabled = true
	add_child(sun)

func _build_sea_and_island() -> void:
	_box(self, Vector3(0, -1.5, 0), Vector3(800, 0.1, 800), _mat(Color(0.05, 0.08, 0.12), 0.1, 0.8), 0.0, false)
	_box(self, Vector3(0, -0.3, -50), Vector3(200, 0.6, 300), _mat(Color(0.15, 0.16, 0.15), 0.95))

func _build_dock() -> void:
	_box(self, Vector3(0, 0.2, 120), Vector3(10, 0.2, 40), _mat(Color(0.2, 0.15, 0.1), 0.9))
	for z in [102, 110, 118, 126]:
		for x in [-4.5, 4.5]:
			_cyl(self, Vector3(x, -1, z), 0.2, 3, _mat(Color(0.15, 0.12, 0.1), 0.9))
	_light(self, Vector3(-4, 4, 110), Color(1, 0.8, 0.5), 2.0, 15.0)
	_light(self, Vector3(4, 4, 110), Color(1, 0.8, 0.5), 2.0, 15.0)

func _build_main_hospital() -> void:
	_box(self, Vector3(0, 8, 20), Vector3(60, 16, 40), _mat(Color(0.25, 0.24, 0.22), 0.95))
	_box(self, Vector3(0, 16.5, 20), Vector3(62, 1, 42), _mat(Color(0.1, 0.1, 0.1), 0.9))
	for x in [-28, 28]:
		for z in [2, 38]:
			_cyl(self, Vector3(x, 17, z), 3, 6, _mat(Color(0.2, 0.2, 0.2), 0.9))
			_cone(self, Vector3(x, 21, z), 3.5, 4, _mat(Color(0.08, 0.08, 0.08), 0.9))
	for floor_y in [4, 9, 14]:
		for x in range(-25, 26, 5):
			_box(self, Vector3(x, floor_y, 0.1), Vector3(1.5, 2.5, 0.2), _glow(Color(0.8, 0.7, 0.5), 1.5), 0.0, false)
	_light(self, Vector3(0, 4, 2), Color(1, 0.7, 0.4), 3.0, 12.0)

func _build_womens_wing() -> void:
	_box(self, Vector3(-45, 5, -20), Vector3(25, 10, 20), _mat(Color(0.22, 0.2, 0.18), 0.9))
	for x in [-52, -45, -38]:
		_box(self, Vector3(x, 4, -9.9), Vector3(1.5, 2, 0.2), _glow(Color(0.6, 0.8, 1.0), 1.5), 0.0, false)

func _build_c_block() -> void:
	_box(self, Vector3(50, 6, -30), Vector3(30, 12, 25), _mat(Color(0.15, 0.15, 0.15), 0.95))
	for x in [40, 50, 60]:
		_box(self, Vector3(x, 5, -17.4), Vector3(1.2, 1.5, 0.2), _glow(Color(0.4, 0.6, 1.0), 1.5), 0.0, false)

func _build_cemetery() -> void:
	for i in range(12):
		var x = -65 + (i % 6) * 4
		var z = 15 + (i / 6) * 5
		_box(self, Vector3(x, 1, z), Vector3(0.2, 2, 0.2), _mat(Color(0.2, 0.2, 0.2), 0.95))
		_box(self, Vector3(x, 1.5, z), Vector3(1, 0.2, 0.2), _mat(Color(0.2, 0.2, 0.2), 0.95))

func _build_cave() -> void:
	_box(self, Vector3(75, 4, -5), Vector3(20, 8, 30), _mat(Color(0.12, 0.12, 0.12), 0.95))
	_light(self, Vector3(65, 1, -5), Color(1, 0.6, 0.3), 2.0, 5.0)

func _build_lighthouse() -> void:
	var base := Vector3(0, 0, -120)
	_cyl(self, base + Vector3(0, 20, 0), 4, 40, _mat(Color(0.4, 0.4, 0.4), 0.9))
	for y in [8, 16, 24, 32]:
		_cyl(self, base + Vector3(0, y, 0), 4.1, 1, _mat(Color(0.3, 0.1, 0.1), 0.9), false)
	lighthouse_pivot = Node3D.new()
	lighthouse_pivot.position = base + Vector3(0, 44, 0)
	add_child(lighthouse_pivot)
	var spot := SpotLight3D.new()
	spot.light_color = Color(1, 0.9, 0.5)
	spot.light_energy = 12.0
	spot.spot_range = 120.0
	spot.spot_angle = 25.0
	spot.rotation_degrees = Vector3(-90, 0, 0)
	lighthouse_pivot.add_child(spot)
	_cyl(self, base + Vector3(0, 44, 0), 2.0, 3.0, _glow(Color(1, 0.9, 0.5), 6.0), false)

func _build_trees() -> void:
	var trunk := _mat(Color(0.1, 0.08, 0.05), 0.9)
	var leaves := _mat(Color(0.05, 0.08, 0.05), 0.95)
	var pos := [Vector3(-30, 0, 70), Vector3(30, 0, 70), Vector3(-40, 0, 50), Vector3(40, 0, 50)]
	for p in pos:
		_cyl(self, p + Vector3(0, 2, 0), 0.3, 4, trunk)
		_cone(self, p + Vector3(0, 5, 0), 2.5, 5, leaves)

func _build_npcs() -> void:
	_npc(self, Vector3(3, 1, 115), "res://scripts/Interactable.gd", "res://dialogues/act1_stan.json", "met_stan", "Стас", Color(0.4, 0.4, 0.5))
	_npc(self, Vector3(0, 1, 15), "res://scripts/Interactable.gd", "res://dialogues/act2_remizov.json", "met_remizov", "Ремизов", Color(0.5, 0.5, 0.5))
	_npc(self, Vector3(50, 1, -30), "res://scripts/Interactable.gd", "res://dialogues/act3_vetrov.json", "met_vetrov", "Ветров", Color(0.6, 0.3, 0.3))
	_npc(self, Vector3(65, 1, -5), "res://scripts/Interactable.gd", "res://dialogues/act4_raisa.json", "met_true_raisa", "Раиса", Color(0.6, 0.5, 0.6))
	_npc(self, Vector3(0, 42, -122), "res://scripts/Interactable.gd", "res://dialogues/act5_finale.json", "finale_seen", "", Color(0.5, 0.5, 0.5))

func _build_rain() -> void:
	var rain := GPUParticles3D.new()
	rain.amount = 8000
	rain.lifetime = 1.5
	rain.position = Vector3(0, 20, 0)
	rain.visibility_aabb = AABB(Vector3(-100, -20, -200), Vector3(200, 40, 400))
	var pm := ParticleProcessMaterial.new()
	pm.emission_shape = ParticleProcessMaterial.EMISSION_SHAPE_BOX
	pm.emission_box_extents = Vector3(80, 1, 150)
	pm.direction = Vector3(0.1, -1, 0)
	pm.spread = 2.0
	pm.initial_velocity_min = 20.0
	pm.initial_velocity_max = 25.0
	pm.gravity = Vector3(0, -9.8, 0)
	rain.process_material = pm
	var mesh := BoxMesh.new()
	mesh.size = Vector3(0.02, 0.6, 0.02)
	rain.draw_pass_1 = mesh
	add_child(rain)

func _process(delta: float) -> void:
	if lighthouse_pivot:
		lighthouse_pivot.rotate_y(delta * 1.2)

func _spawn_player() -> void:
	var player_scene = load("res://scenes/Player.tscn")
	if not player_scene: return
	var p = player_scene.instantiate()
	p.position = Vector3(0, 1, 130)
	add_child(p)
