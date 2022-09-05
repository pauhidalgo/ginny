from abc import ABC
from datetime import datetime
from typing import Dict

import matplotlib
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.ticker import MultipleLocator


class TimelinePlot(ABC):  # Hardcoded to watering for now
    def __init__(self, items: Dict):
        super().__init__()
        self.items = items
        self.fig = None  # Defined after get_fig is called

    def get_fig(self):
        fig, ax = plt.subplots(1, 1)
        y_labels, y_ticks = [], []

        freqs = self.compute_frequencies()
        # Define color map based on watering frequencies
        freqs = [f for f in freqs if f < 0.2 and f > 0]
        norm = matplotlib.colors.Normalize(vmin=min(freqs), vmax=max(freqs), clip=True)
        mapper = matplotlib.cm.ScalarMappable(norm=norm, cmap="viridis")

        sorted_items = [
            d for d in sorted(self.items, key=lambda i: i["watering_frequency"])
        ]
        for y_item, item in enumerate(sorted_items, start=1):
            ax.scatter(
                x=item["dates_watered"],
                y=[y_item for i in item["dates_watered"]],
                alpha=0.6,
                s=50,
                color=mapper.to_rgba(item["watering_frequency"]),
            )
            y_labels.append(
                f"{item['name']}\n{1/item['watering_frequency']: .0f} days avg."
            )
            y_ticks.append(y_item)

        ax.set_yticks(y_ticks)
        ax.set_yticklabels(y_labels)
        ax.tick_params(axis="both", which="major", labelsize=7)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b\n%Y"))
        ax.yaxis.set_major_locator(MultipleLocator(1))

        ax.set_title("Watering frequency")
        ax.spines.right.set_visible(False)
        ax.spines.top.set_visible(False)

        self.fig = fig
        return fig

    def compute_frequencies(self):
        # Compute watering frequency as freq = (number of days watered / number of days plant owned)
        # 1/freq yields average number of days between watering
        freqs = []
        for item in self.items:
            dates_col = pd.to_datetime(item["dates_watered"])
            dates_owned = (datetime.now() - dates_col.min()).days
            if dates_owned > 0:
                freq = len(dates_col) / (datetime.now() - dates_col.min()).days
            else:
                freq = 1
            item["watering_frequency"] = freq
            freqs.append(freq)
        return freqs
