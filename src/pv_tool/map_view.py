import webbrowser
import folium
from branca.colormap import LinearColormap


def display_interactive_map(roofs, modules, output_html="map_visualization.html"):
    roofs_wgs84 = roofs.to_crs(epsg=4326)
    modules_wgs84 = modules.to_crs(epsg=4326)
    centroid = roofs_wgs84.geometry.centroid.iloc[0]

    values = (
        roofs_wgs84["irr_kwh_m2"]
        if "irr_kwh_m2" in roofs_wgs84.columns
        else roofs_wgs84["power_kwp"]
    )

    colors = ["#000004", "#2c115f", "#721f81", "#b63679", "#f1605d", "#feb078", "#fcfdbf"]
    colormap = LinearColormap(
        colors=colors,
        vmin=values.min(),
        vmax=values.max(),
        caption="Irradiance (kWh/m²/year)",
    )

    m = folium.Map(
        location=[centroid.y, centroid.x],
        zoom_start=19,
        tiles="CartoDB positron",
    )

    def roof_style(feature):
        value = (
            feature["properties"].get("irr_kwh_m2")
            or feature["properties"].get("power_kwp", 0)
        )
        return {
            "fillColor": colormap(value),
            "color": "black",
            "weight": 1,
            "fillOpacity": 0.6,
        }

    tooltip_fields = (
        ["power_kwp", "irr_kwh_m2"]
        if "irr_kwh_m2" in roofs_wgs84.columns
        else ["power_kwp"]
    )

    folium.GeoJson(
        roofs_wgs84,
        name="Roofs",
        style_function=roof_style,
        tooltip=folium.GeoJsonTooltip(fields=tooltip_fields),
    ).add_to(m)

    folium.GeoJson(
        modules_wgs84,
        name="Modules",
        style_function=lambda x: {
            "fillColor": "#ffaa00",
            "color": "#444",
            "weight": 0.5,
            "fillOpacity": 0.7,
        },
    ).add_to(m)

    colormap.add_to(m)
    folium.LayerControl().add_to(m)

    m.save(output_html)
    webbrowser.open(output_html)