Methodology

The development of the 3D model was carried out using a parametric approach in Build123d.

1. Extraction of Outer Profile Coordinates

First, the outer profile of the component was identified.
The coordinate points (X, Y) of the boundary were manually extracted from the CAD model (Fusion/visual reference).
These coordinates represent the exact geometry of the outer contour.

2. Creation of 2D Profile

The extracted coordinate points were used to construct a closed 2D profile.
This was achieved by connecting all the points sequentially using line segments (Polyline approach) to ensure a continuous boundary.

3. Conversion to 3D Model (Extrusion)

Once the 2D closed profile was created, it was converted into a 3D solid by applying an extrusion operation.
A thickness of 4 mm was used to generate the base plate.

4. Bounding Box Calculation

After creating the base plate, the bounding box of the geometry was computed.
This helped in identifying the extreme edges (minimum and maximum X and Y values), which are necessary for positioning additional features accurately.

5. Addition of Secondary Feature (Box)

A square feature of 30 mm × 30 mm was created on the top surface of the plate.
The position of this box was defined relative to the bounding box (bottom-right corner alignment).

6. Extrusion of Secondary Feature

The square profile was extruded by 20 mm to create a raised feature on the plate.

7. Position Adjustment

The box was further adjusted using translation operations:

Shifted in Y-direction (32 mm) for correct placement
Shifted in Z-direction (-34 mm) to align it properly with the base geometry
8. Future Improvement (Automation)

Currently, coordinate extraction was done manually.
To improve accuracy and efficiency, AutoCAD has been installed.
In future steps, coordinates will be extracted automatically from DXF/DWG files using AutoCAD tools, reducing manual errors and improving precision.
