
### Basic Version ###
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from google.colab import files


# Upload the CSV file
print("Please select your data.csv file:")
uploaded = files.upload()
file_name = next(iter(uploaded))


# Select the variables
variables = {
    "volume": "VOLUME",
    "total_working_cycle_power": "CYCLE\nPOWER",
    "thermal_conductivity": "THERMAL\nCONDUCTIVITY",
    "insulation_density": "INSULATION\nDENSITY",
    "insulation_thickness": "INSULATION\nTHICKNESS",
    "cooling_fan_power": "COOLING FAN\nPOWER",
    "cooling_fan_rpm": "COOLING FAN\nSPEED",
    "cavity_fan_rpm": "CAVITY FAN\nSPEED",
    "num_glass": "GLASS\nCOUNT",
    "chimney": "CHIMNEY",
}

columns = list(variables.keys())
labels = list(variables.values())


# Read and prepare the data
df = pd.read_csv(file_name)
df["energy_class"] = df["energy_class"].astype(str).str.strip().str.upper()
df = df[df["energy_class"].isin(["A", "A+"])].copy()
df[columns] = df[columns].apply(pd.to_numeric, errors="coerce")

# Correct misplaced decimal values in volume
df.loc[df["volume"] > 200, "volume"] /= 10


# Normalize the values between 0 and 1
minimum = df[columns].min()
maximum = df[columns].max()
normalized = (df[columns] - minimum) / (maximum - minimum).replace(0, np.nan)
normalized["energy_class"] = df["energy_class"]

# Calculate the mean profile for each energy class
profiles = normalized.groupby("energy_class")[columns].mean()
aplus_values = profiles.loc["A+"].fillna(0).to_numpy()
a_values = profiles.loc["A"].fillna(0).to_numpy()


# Prepare the radar chart
number_of_axes = len(columns)
angles = np.linspace(0, 2 * np.pi, number_of_axes, endpoint=False)
closed_angles = np.append(angles, angles[0])
aplus_values = np.append(aplus_values, aplus_values[0])
a_values = np.append(a_values, a_values[0])

background = "#FFFFFF"
text_color = "#253238"
muted_text = "#60736E"
grid_color = "#D7E2E8"
aplus_color = "#3E8FC2"
a_color = "#8B2635"

plt.rcParams["font.family"] = "serif"
plt.rcParams["font.serif"] = ["cmr10", "DejaVu Serif"]
plt.rcParams["axes.formatter.use_mathtext"] = True

fig = plt.figure(figsize=(12, 10), facecolor=background)
ax = fig.add_axes([0.16, 0.18, 0.68, 0.66], polar=True)

ax.set_facecolor(background)
ax.set_theta_offset(np.pi / 2)
ax.set_theta_direction(-1)
ax.set_ylim(0, 1)


# Add the title and subtitle
fig.text(
    0.5, 0.955,
    "HOW DO A AND A+ OVEN DESIGNS DIFFER?",
    ha="center", va="top", fontsize=25, color=text_color,
)

fig.text(
    0.5, 0.910,
    "A comparison of the average design characteristics of A and A+ rated ovens.",
    ha="center", va="top", fontsize=13.5, color=muted_text,
)


# Add the variable labels
ax.set_xticks(angles)
ax.set_xticklabels(labels, fontsize=11, color=text_color)
ax.tick_params(axis="x", pad=18)
ax.set_yticks([])
ax.grid(False)
ax.spines["polar"].set_visible(False)


# Draw the polygon grid
for radius in [0.2, 0.4, 0.6, 0.8, 1.0]:
    ax.plot(
        closed_angles,
        [radius] * (number_of_axes + 1),
        color=grid_color,
        linewidth=1.25,
        zorder=0,
    )

for angle in angles:
    ax.plot(
        [angle, angle],
        [0, 1],
        color=grid_color,
        linewidth=1.05,
        zorder=0,
    )


# Draw the A+ profile
line_aplus, = ax.plot(
    closed_angles,
    aplus_values,
    color=aplus_color,
    linewidth=3,
    marker="o",
    markersize=6.3,
    label=f"A+  ({(df['energy_class'] == 'A+').sum()} designs)",
)

ax.fill(
    closed_angles,
    aplus_values,
    color=aplus_color,
    alpha=0.20,
)


# Draw the A profile
line_a, = ax.plot(
    closed_angles,
    a_values,
    color=a_color,
    linewidth=2.5,
    marker="o",
    markersize=6.3,
    alpha=0.78,
    label=f"A  ({(df['energy_class'] == 'A').sum()} designs)",
)

ax.fill(
    closed_angles,
    a_values,
    color=a_color,
    alpha=0.13,
)


# Add the legend
fig.legend(
    handles=[line_aplus, line_a],
    loc="lower center",
    bbox_to_anchor=(0.5, 0.095),
    ncol=2,
    frameon=False,
    fontsize=13,
    handlelength=2.5,
    columnspacing=3,
)


# Add the normalization note
fig.text(
    0.5, 0.050,
    "Values are min-max normalized; a larger radius indicates a higher class-average value.",
    ha="center",
    va="center",
    fontsize=11.5,
    color=muted_text,
)


# Save and download the chart
output_file = "/content/oven_energy_radar.png"

plt.savefig(
    output_file,
    dpi=220,
    facecolor=background,
    bbox_inches="tight",
    pad_inches=0.25,
)

plt.show()
plt.close()

print(f"Chart saved as: {output_file}")
files.download(output_file)

####################################################### SECOND CODE ########################################################################
### Function-Based Version ###
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from google.colab import files


def radar_chart(labels, values, groups, colors, title, subtitle, note, save_path):
    """Create and save a polygon-style radar chart."""

    labels = np.array(labels)
    values = np.array(values, dtype=float)

    if values.ndim == 1:
        values = values.reshape(1, -1)

    if values.shape[1] != len(labels):
        raise ValueError("Each profile must have one value for every label.")

    if len(groups) != len(values):
        raise ValueError("The number of groups and profiles must be equal.")

    angles = np.linspace(0, 2 * np.pi, len(labels), endpoint=False)
    closed_angles = np.append(angles, angles[0])

    background = "#FFFFFF"
    text_color = "#253238"
    muted_text = "#60736E"
    grid_color = "#D7E2E8"

    plt.rcParams["font.family"] = "serif"
    plt.rcParams["font.serif"] = ["cmr10", "DejaVu Serif"]
    plt.rcParams["axes.formatter.use_mathtext"] = True

    fig = plt.figure(figsize=(12, 10), facecolor=background)
    ax = fig.add_axes([0.16, 0.18, 0.68, 0.66], polar=True)

    ax.set_facecolor(background)
    ax.set_theta_offset(np.pi / 2)
    ax.set_theta_direction(-1)
    ax.set_ylim(0, 1)
    ax.set_xticks(angles)
    ax.set_xticklabels(labels, fontsize=11, color=text_color)
    ax.tick_params(axis="x", pad=18)
    ax.set_yticks([])
    ax.grid(False)
    ax.spines["polar"].set_visible(False)

    fig.text(
        0.5, 0.955,
        title,
        ha="center",
        va="top",
        fontsize=25,
        color=text_color,
    )

    fig.text(
        0.5, 0.910,
        subtitle,
        ha="center",
        va="top",
        fontsize=13.5,
        color=muted_text,
    )

    # Draw the polygon grid
    for radius in [0.2, 0.4, 0.6, 0.8, 1.0]:
        ax.plot(
            closed_angles,
            [radius] * (len(labels) + 1),
            color=grid_color,
            linewidth=1.25,
            zorder=0,
        )

    for angle in angles:
        ax.plot(
            [angle, angle],
            [0, 1],
            color=grid_color,
            linewidth=1.05,
            zorder=0,
        )

    # Draw the profiles
    lines = []
    fill_alphas = [0.20, 0.13]
    line_alphas = [1.00, 0.78]
    line_widths = [3.0, 2.5]

    for index, profile in enumerate(values):
        closed_profile = np.append(profile, profile[0])

        line, = ax.plot(
            closed_angles,
            closed_profile,
            color=colors[index],
            linewidth=line_widths[index],
            marker="o",
            markersize=6.3,
            alpha=line_alphas[index],
            label=groups[index],
            zorder=3,
        )

        ax.fill(
            closed_angles,
            closed_profile,
            color=colors[index],
            alpha=fill_alphas[index],
            zorder=2,
        )

        lines.append(line)

    fig.legend(
        handles=lines,
        loc="lower center",
        bbox_to_anchor=(0.5, 0.095),
        ncol=len(groups),
        frameon=False,
        fontsize=13,
        handlelength=2.5,
        columnspacing=3,
    )

    fig.text(
        0.5, 0.050,
        note,
        ha="center",
        va="center",
        fontsize=11.5,
        color=muted_text,
    )

    plt.savefig(
        save_path,
        dpi=220,
        facecolor=background,
        bbox_inches="tight",
        pad_inches=0.25,
    )

    plt.show()
    plt.close()


# Upload the CSV file
print("Please select your data.csv file:")
uploaded = files.upload()
file_name = next(iter(uploaded))


# Select the variables
variables = {
    "volume": "VOLUME",
    "total_working_cycle_power": "CYCLE\nPOWER",
    "thermal_conductivity": "THERMAL\nCONDUCTIVITY",
    "insulation_density": "INSULATION\nDENSITY",
    "insulation_thickness": "INSULATION\nTHICKNESS",
    "cooling_fan_power": "COOLING FAN\nPOWER",
    "cooling_fan_rpm": "COOLING FAN\nSPEED",
    "cavity_fan_rpm": "CAVITY FAN\nSPEED",
    "num_glass": "GLASS\nCOUNT",
    "chimney": "CHIMNEY",
}

columns = list(variables.keys())
labels = list(variables.values())


# Read and prepare the data
df = pd.read_csv(file_name)

df["energy_class"] = (
    df["energy_class"]
    .astype(str)
    .str.strip()
    .str.upper()
)

df = df[df["energy_class"].isin(["A", "A+"])].copy()

df[columns] = df[columns].apply(
    pd.to_numeric,
    errors="coerce",
)

df.loc[df["volume"] > 200, "volume"] /= 10


# Normalize the values
minimum = df[columns].min()
maximum = df[columns].max()

normalized = (
    (df[columns] - minimum)
    / (maximum - minimum).replace(0, np.nan)
)

normalized["energy_class"] = df["energy_class"]

profiles = (
    normalized
    .groupby("energy_class")[columns]
    .mean()
)

aplus_values = profiles.loc["A+"].fillna(0).to_numpy()
a_values = profiles.loc["A"].fillna(0).to_numpy()


# Plot and download the chart
output_file = "/content/oven_energy_radar.png"

radar_chart(
    labels=labels,
    values=[aplus_values, a_values],
    groups=[
        f"A+  ({(df['energy_class'] == 'A+').sum()} designs)",
        f"A  ({(df['energy_class'] == 'A').sum()} designs)",
    ],
    colors=["#3E8FC2", "#8B2635"],
    title="HOW DO A AND A+ OVEN DESIGNS DIFFER?",
    subtitle=(
        "A comparison of the average design characteristics "
        "of A and A+ rated ovens."
    ),
    note=(
        "Values are min-max normalized; a larger radius indicates "
        "a higher class-average value."
    ),
    save_path=output_file,
)

print(f"Chart saved as: {output_file}")
files.download(output_file)
