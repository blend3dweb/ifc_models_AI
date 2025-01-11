import ifcopenshell
import ifcopenshell.api
import uuid
import time
import math

# Create new IFC file
ifc = ifcopenshell.file()

# Create project structure
project = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcProject", name="Residential Pipeline System")
site = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcSite", name="Building Site")
building = ifcopenshell.api.run("root.create_entity", ifc, ifc_class="IfcBuilding", name="Residential Building")

# Set units
ifcopenshell.api.run("unit.assign_unit", ifc, length={"is_metric": True, "raw": "METERS"})

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
def create_pipe(start_point, end_point, is_hot):
    pipe = ifc.create_entity("IfcFlowSegment")
    
    # Set pipe properties using direct entity creation
    color = (1.0, 0.0, 0.0) if is_hot else (0.0, 0.0, 1.0)
    style = ifc.create_entity("IfcPresentationStyle", Name=f"{'Hot' if is_hot else 'Cold'} Water Pipe")
    
    return pipe

# Create main vertical pipes
main_cold_pipe = create_pipe([0, 0, 0], [0, 0, 18], False)
main_hot_pipe = create_pipe([0.5, 0, 0], [0.5, 0, 18], True)

# Create horizontal distribution pipes for each floor
for i, floor in enumerate(floors):
    height = i * 3  # 3m per floor
    
    # Create horizontal pipes for both hot and cold water
    for j in range(4):  # 4 apartments per floor
        cold_pipe = create_pipe([0, 0, height], [5, j*5, height], False)
        hot_pipe = create_pipe([0.5, 0, height], [5, j*5, height], True)

# Save the IFC file
ifc.write("residential_pipeline_system.ifc")
