from ttkthemes import ThemedTk
from tkinter import filedialog, messagebox
from tkinter import DoubleVar
from tkinter import ttk

from pv_tool.optimizer import run_optimization
from pv_tool.map_view import display_interactive_map
from pv_tool.config import (
    DEFAULT_MODULE_LENGTH,
    DEFAULT_MODULE_WIDTH,
    DEFAULT_SPACING,
    DEFAULT_MARGIN,
    DEFAULT_POWER_KWP,
    DEFAULT_LAYER_NAME,
    DEFAULT_PR,
    DEFAULT_FALLBACK_IRRADIANCE,
)


def choose_file(entry_widget, filetypes):
    path = filedialog.askopenfilename(filetypes=filetypes)
    if path:
        entry_widget.delete(0, "end")
        entry_widget.insert(0, path)


def run_analysis():
    gpkg_path = entry_gpkg.get().strip()
    raster_path = entry_raster.get().strip() or None
    layer_name = entry_layer.get().strip()

    if not gpkg_path:
        messagebox.showerror("Error", "Please select a GeoPackage file.")
        return

    try:
        output_gpkg, roofs, modules = run_optimization(
            geopackage_path=gpkg_path,
            layer_name=layer_name,
            module_length=module_length.get(),
            module_width=module_width.get(),
            spacing=spacing.get(),
            margin=margin.get(),
            power_kwp=power_kwp.get(),
            irradiance_raster_path=raster_path,
        )

        total_modules = roofs["num_modules"].sum()
        total_power = roofs["power_kwp"].sum()

        if "irr_kwh_m2" in roofs.columns:
            total_energy = (roofs["power_kwp"] * roofs["irr_kwh_m2"] * DEFAULT_PR).sum()
        else:
            total_energy = total_power * DEFAULT_FALLBACK_IRRADIANCE * DEFAULT_PR

        messagebox.showinfo(
            "Analysis Completed",
            f"Result saved to: {output_gpkg}\n\n"
            f"Total modules: {int(total_modules)}\n"
            f"Total power: {total_power:.2f} kWp\n"
            f"Estimated energy: {total_energy:,.0f} kWh/year",
        )

        if messagebox.askyesno("Visualization", "Would you like to view the interactive map?"):
            display_interactive_map(roofs, modules)

    except Exception as e:
        messagebox.showerror("Error", str(e))


root = ThemedTk(theme="arc")
root.title("Photovoltaic Optimizer")
root.geometry("600x480")

frame = ttk.Frame(root, padding=20)
frame.grid(row=0, column=0)

entry_gpkg = ttk.Entry(frame, width=50)
entry_raster = ttk.Entry(frame, width=50)
entry_layer = ttk.Entry(frame, width=30)
entry_layer.insert(0, DEFAULT_LAYER_NAME)

module_length = DoubleVar(value=DEFAULT_MODULE_LENGTH)
module_width = DoubleVar(value=DEFAULT_MODULE_WIDTH)
spacing = DoubleVar(value=DEFAULT_SPACING)
margin = DoubleVar(value=DEFAULT_MARGIN)
power_kwp = DoubleVar(value=DEFAULT_POWER_KWP)

fields = [
    (
        "Path to GeoPackage (.gpkg):",
        entry_gpkg,
        lambda: choose_file(entry_gpkg, [("GPKG", "*.gpkg")]),
    ),
    (
        "(Optional) Irradiance Raster (.tif):",
        entry_raster,
        lambda: choose_file(entry_raster, [("GeoTIFF", "*.tif")]),
    ),
    ("Roof layer name:", entry_layer, None),
]

for i, (label, entry, func) in enumerate(fields):
    ttk.Label(frame, text=label).grid(row=i, column=0, sticky="w")
    entry.grid(row=i, column=1, padx=5, pady=4)
    if func:
        ttk.Button(frame, text="Select", command=func).grid(row=i, column=2, padx=5)

params = [
    ("Module length (m):", module_length),
    ("Module width (m):", module_width),
    ("Spacing (m):", spacing),
    ("Margin (m):", margin),
    ("Power (kWp):", power_kwp),
]

for i, (text, var) in enumerate(params, start=len(fields)):
    ttk.Label(frame, text=text).grid(row=i, column=0, sticky="w")
    ttk.Entry(frame, textvariable=var, width=10).grid(row=i, column=1, sticky="w", pady=2)

ttk.Button(frame, text="Run Analysis", command=run_analysis).grid(
    row=i + 1, column=0, columnspan=3, pady=20
)

root.mainloop()