from abc import ABC
from typing import List, Dict, Optional

import pandas as pd
import plotly.express as px


class HoverTimelinePlot(ABC): 
    def __init__(self, items: List[Dict]):
        self.items = items
        self.df: Optional[pd.DataFrame] = None
        self.fig = None

        self.convert_to_df()

    def convert_to_df(self):
        # Convert items to long df for easier plotting
        plant, action, date, action_freq = [], [], [], []
        for item in self.items:
            for d in item['dates_watered']:
                plant.append(item["name"])
                action.append('water')
                date.append(d)
                action_freq.append(item['watering_frequency'])
            # TODO other actions

        self.df = pd.DataFrame(data={'plant': plant, 'action': action, 'date': date, 'freq': action_freq})
        self.df = self.df.sort_values(by='freq', ascending=False)
        self.df['avg_days'] = 1 / self.df['freq']

    def get_fig(self):
        fig = px.scatter(self.df, y="plant", x="date", color="avg_days", template='plotly_white',
                         hover_data=["avg_days"], color_continuous_scale=px.colors.sequential.Viridis[::-1])
        fig.update_traces(marker_size=8)

        fig.update_layout(
            showlegend=False,
            paper_bgcolor='white',
            plot_bgcolor='white',
        )

        return fig
