import numpy as np
import geopandas as gpd
import rasterio
from rasterstats import zonal_stats
from shapely.geometry import box
from shapely.affinity import rotate


def angle_from_longest_edge(polygon):
    """Return the angle in degrees of the longest polygon edge."""
    coords = list(polygon.exterior.coords)
    max_length = 0.0
    best_angle = 0.0

    for i in range(len(coords) - 1):
        dx = coords[i + 1][0] - coords[i][0]
        dy = coords[i + 1][1] - coords[i][1]
        length = np.hypot(dx, dy)

        if length > max_length:
            max_length = length
            best_angle = np.degrees(np.arctan2(dy, dx))

    return best_angle


def generate_modules_with_offset(
    polygon,
    angle,
    module_length,
    module_width,
    spacing,
    offset_steps=5,
):
    """
    Generate module rectangles inside a polygon using a rotated packing strategy.
    Multiple offsets are tested to maximize module count.
    """
    rotated_polygon = rotate(polygon, -angle, origin="centroid", use_radians=False)
    bounds = rotated_polygon.bounds
    best_modules = []

    x_offsets = np.linspace(0, module_length + spacing, offset_steps)
    y_offsets = np.linspace(0, module_width + spacing, offset_steps)

    for dx in x_offsets:
        for dy in y_offsets:
            modules = []
            x = bounds[0] + dx

            while x + module_length <= bounds[2] + 1e-6:
                y = bounds[1] + dy
                while y + module_width <= bounds[3] + 1e-6:
                    rect = box(x, y, x + module_length, y + module_width)
                    if rotated_polygon.contains(rect):
                        modules.append(rect)
                    y += module_width + spacing
                x += module_length + spacing

            if len(modules) > len(best_modules):
                best_modules = modules

    return [
        rotate(module, angle, origin=polygon.centroid, use_radians=False)
        for module in best_modules
    ]


def run_optimization(
    geopackage_path,
    layer_name,
    module_length,
    module_width,
    spacing,
    margin,
    power_kwp,
    irradiance_raster_path=None,
    output_path=None,
):
    """
    Run rooftop PV allocation and save results to a GeoPackage.

    Returns
    -------
    tuple
        (output_path, roofs_gdf, modules_gdf)
    """
    roofs = gpd.read_file(geopackage_path, layer=layer_name)

    if roofs.crs is None or not roofs.crs.is_projected:
        raise ValueError("The rooftop layer must use a projected coordinate system.")

    all_modules = []
    results = []

    for idx, row in roofs.iterrows():
        roof_polygon = row.geometry.buffer(-margin)

        if roof_polygon.is_empty or not roof_polygon.is_valid:
            results.append(
                {
                    "idx": idx,
                    "num_modules": 0,
                    "power_kwp": 0.0,
                }
            )
            continue

        base_angle = angle_from_longest_edge(roof_polygon)

        combinations = [
            (base_angle, module_length, module_width),
            (base_angle + 90, module_length, module_width),
            (base_angle, module_width, module_length),
            (base_angle + 90, module_width, module_length),
        ]

        best_modules = []
        for angle, length, width in combinations:
            test_modules = generate_modules_with_offset(
                roof_polygon,
                angle,
                length,
                width,
                spacing,
                offset_steps=5,
            )
            if len(test_modules) > len(best_modules):
                best_modules = test_modules

        all_modules.extend(best_modules)
        results.append(
            {
                "idx": idx,
                "num_modules": len(best_modules),
                "power_kwp": round(len(best_modules) * power_kwp, 2),
            }
        )

    roofs["num_modules"] = [r["num_modules"] for r in results]
    roofs["power_kwp"] = [r["power_kwp"] for r in results]

    if irradiance_raster_path:
        with rasterio.open(irradiance_raster_path) as src:
            stats = zonal_stats(
                roofs.geometry,
                irradiance_raster_path,
                stats="median",
                nodata=src.nodata,
            )
        roofs["irr_kwh_m2"] = [
            s["median"] if s["median"] is not None else 0 for s in stats
        ]

    modules_gdf = gpd.GeoDataFrame(geometry=all_modules, crs=roofs.crs)
    modules_gdf["roof_id"] = np.repeat(
        roofs.index.values,
        roofs["num_modules"].fillna(0).astype(int),
    )

    if output_path is None:
        output_path = geopackage_path.replace(".gpkg", "_result.gpkg")

    roofs.to_file(output_path, layer="roofs_with_potential", driver="GPKG")
    modules_gdf.to_file(output_path, layer="allocated_modules", driver="GPKG")

    return output_path, roofs, modules_gdf