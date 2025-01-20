import ifcopenshell
import ifcopenshell.api
import uuid
import time
import math
import bpy

# Create new IFC file
ifc = ifcopenshell.file()

# Create project structure
project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject", name="Residential Pipeline System")
site = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSite", name="Building Site")
building = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuilding", name="Residential Building")

# Set units
ifcopenshell.api.run("unit.assign_unit", ifc, length={"is_metric": True, "raw": "METERS"})



# Create cube geometry
verts = [(1,1,1), (-1,1,1), (-1,-1,1), (1,-1,1)]
faces = [(0,1,2,3)]
mesh.from_pydata(verts, [], faces)

# Create floors
floors = []
for i in range(6):
    floor = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuildingStorey", name=f"Floor {i+1}")
    floors.append(floor)
    
# Create apartments per floor (4 apartments per floor)
apartments = []
for floor in floors:
    for j in range(4):
        apartment = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSpace", name=f"Apartment {j+1}")
        apartments.append(apartment)

# Create pipe systems using IfcSystem directly
cold_water_system = ifc.create_entity("IfcSystem", Name="Cold Water System")
hot_water_system = ifc.create_entity("IfcSystem", Name="Hot Water System")

# Create pipes with different colors for hot and cold water
# After creating pipes, add this geometry creation function
def create_pipe_geometry(ifc, pipe, start_point, end_point, diameter=0.1):
    # Calculate direction vector and length
    direction = [end_point[i] - start_point[i] for i in range(3)]
    length = math.sqrt(sum(d*d for d in direction))
    
    # Normalize direction vector
    direction = [d/length for d in direction]
    
    # Create placement
    placement = ifc.create_entity(
        "IfcLocalPlacement",
        RelativePlacement=ifc.create_entity(
            "IfcAxis2Placement3D",
            Location=ifc.create_entity("IfcCartesianPoint", Coordinates=start_point),
            Axis=ifc.create_entity("IfcDirection", DirectionRatios=direction),
            RefDirection=ifc.create_entity("IfcDirection", DirectionRatios=[1.0, 0.0, 0.0])
        )
    )
    
    # Create circular profile
    circle = ifc.create_entity(
        "IfcCircleProfileDef",
        ProfileType="AREA",
        Radius=diameter/2
    )
    
    # Create extruded geometry
    solid = ifc.create_entity(
        "IfcExtrudedAreaSolid",
        SweptArea=circle,
        Position=ifc.create_entity("IfcAxis2Placement3D", Location=ifc.create_entity("IfcCartesianPoint", Coordinates=(0., 0., 0.))),
        ExtrudedDirection=ifc.create_entity("IfcDirection", DirectionRatios=(0., 0., 1.)),
        Depth=length
    )
    
    # Create shape representation
    shape = ifc.create_entity(
        "IfcShapeRepresentation",
        ContextOfItems=ifc.by_type("IfcGeometricRepresentationContext")[0],
        RepresentationIdentifier="Body",
        RepresentationType="SweptSolid",
        Items=[solid]
    )
    
    # Assign geometry to pipe
    product_shape = ifc.create_entity(
        "IfcProductDefinitionShape",
        Representations=[shape]
    )
    
    pipe.Representation = product_shape
    pipe.ObjectPlacement = placement

# Modify the create_pipe function to include geometry
def create_pipe(ifc, start_point, end_point, is_hot):
    pipe = ifc.create_entity("IfcFlowSegment")
    create_pipe_geometry(ifc, pipe, start_point, end_point)
    
    # Set pipe properties
    color = (1.0, 0.0, 0.0) if is_hot else (0.0, 0.0, 1.0)
    style = ifc.create_entity("IfcPresentationStyle", Name=f"{'Hot' if is_hot else 'Cold'} Water Pipe")
    
    return pipe

    # Create main vertical pipes
    main_cold_pipe = create_pipe(ifc, [0, 0, 0], [0, 0, 18], False)
    main_hot_pipe = create_pipe(ifc, [0.5, 0, 0], [0.5, 0, 18], True)

    # Create horizontal distribution pipes for each floor
    for i, floor in enumerate(floors):
        height = i * 3  # 3m per floor
        for j in range(4):  # 4 apartments per floor
            cold_pipe = create_pipe(ifc, [0, 0, height], [5, j*5, height], False)
            hot_pipe = create_pipe(ifc, [0.5, 0, height], [5, j*5, height], True)
# Save the IFC file
ifc.write("residential_pipeline_system.ifc")
