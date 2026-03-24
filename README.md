# Rooftop PV Potential Assessment Tool for Informal Settlements

![Python](https://img.shields.io/badge/python-3.11-blue)
![License](https://img.shields.io/badge/license-MIT-green)

An open-access decision-support tool designed to estimate rooftop photovoltaic (PV) potential in data-scarce and morphologically complex urban environments, particularly informal settlements.

This tool integrates geospatial data (GeoPackage), optional solar irradiance rasters, and a geometric optimization algorithm to estimate:

- Maximum number of PV modules per rooftop
- Installed capacity (kWp)
- Estimated annual energy generation (kWh/year)
- Spatial distribution of modules
- Interactive web-based visualization

---

## 📌 Features

- ✔ Automated rooftop-level PV allocation  
- ✔ Works with UAV-derived or GIS-based rooftop data  
- ✔ Supports irradiance raster (optional)  
- ✔ Generates GIS-ready outputs (GeoPackage)  
- ✔ Interactive map visualization (Folium)  
- ✔ User-friendly graphical interface (Tkinter)  

---

## 🧠 Methodological Scope

The tool is designed for pre-feasibility assessment of rooftop PV systems and integrates:

- Geometric optimization of module placement (2D bin-packing heuristic)
- Rotation based on rooftop geometry (longest-edge orientation)
- Multi-offset grid search for optimal module allocation
- Irradiance-based energy estimation
- GIS-based spatial analysis and visualization

The methodology prioritizes accessibility, scalability, and applicability in data-scarce environments, particularly in informal settlements.

---

## 📂 Repository Structure

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/asousaujaen/pv-rooftop-tool-informal-settlements.git
cd pv-rooftop-tool-informal-settlements
