import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash.dependencies import Input, Output

path = "https://raw.githubusercontent.com/JeremyVino/Data-Visualization/master/dataset-vis.csv"
df = pd.read_csv(path)


df['Start Time']=pd.to_datetime(df['Start Time'])
df['hour']=""
df['local_time']=""
for i in range(df.shape[0]):
	df.at[i,'hour']=int(df.at[i,'Start Time'].strftime("%H"))
	df.at[i,'local_time']=df.at[i,'Start Time'].strftime("%X")

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)


app.layout = html.Div([

	html.Div([
		dash_table.DataTable(
			id='datatable-interactivity',
			columns=[
				{"name": i, "id": i, "deletable": True, "selectable": True} for i in df.columns
			],
			data=df.to_dict('records'),
			editable=True,
			filter_action="native",
			sort_action="native",
			sort_mode="multi",
			column_selectable="single",
			row_selectable="multi",
			row_deletable=False,
			selected_columns=[],
			selected_rows=[],
			page_action="native",
			page_current= 0,
			page_size= 10,
		),
		html.Div(id='datatable-interactivity-container')
	]),


	html.Div([

		html.Div([
			dcc.Dropdown(
				id='crossfilter-xaxis-column',
				options=[{'label': i, 'value': i} for i in df['Start Station Name'].unique()],
				value='Jersey & 6th St'
			),

		],
		style={'width': '30%', 'display': 'inline-block'}),

		html.Div([
			dcc.Dropdown(
				id='crossfilter-yaxis-column',
				options=[{'label': i, 'value': i} for i in df['End Station Name'].unique()],
				value='Manila & 1st'
			),

		], style={'width': '30%', 'float': 'right', 'display': 'inline-block'})
	], style={
		'borderBottom': 'thin lightgrey solid',
		'backgroundColor': 'rgb(250, 250, 250)',
		'padding': '10px 5px'
	}),

	html.Div([
		dcc.Graph(id='line-charts')
	]),

	html.Div([
		dcc.Markdown(children="## Below are local time based graphs, including pie chart, parallel coordinates, and scatter plots. Please drag the slide at the bottom to interact.")
	]),




	html.Div([
		dcc.Graph(id='parallel-coordinates')
	],style={'width': '49%', 'display': 'inline-block'}),
	html.Div([
		dcc.Graph(id='scatter-plots')
	],style={'height':500,'width': '49%', 'display': 'inline-block'}),

	html.Div([
		dcc.Graph(id='End pie Graph'),
	],style={'width': '49%', 'display': 'inline-block'}),

	html.Div([
		dcc.Graph(id='Start pie Graph'),
	], style={'width': '49%', 'display': 'inline-block'}),

	html.Div([
		dcc.Slider(
			id='hour-slider',
			min=df['hour'].min(),
			max=df['hour'].max(),
			value=df['hour'].min(),
			marks={str(hour): str(hour) for hour in df['hour'].unique()},
			step=None
		)
	])
])


@app.callback(
	[Output('End pie Graph','figure'),
	 Output('Start pie Graph','figure'),
	 Output('scatter-plots','figure'),
	 Output('parallel-coordinates', 'figure')],
	[Input('hour-slider', 'value')])

def update_figure(selected_hour):
	filtered_df=df[df.hour==selected_hour]
	scatter=[]
	for i in filtered_df['User Type'].unique():
		df_by_usertype=filtered_df[filtered_df['User Type']==i]
		scatter.append(dict(
			x=df_by_usertype['local_time'],
			y=df_by_usertype['Trip Duration'],
			mode='markers',
			opacity=0.7,
			marker={
				'size':10,
				'line': {'width':0.5,'color':'white'}
			},
			name=i
		))

	scatter_plot= {
		'data':scatter,
		'layout':dict (
			title='The relation between Time and Duration',
			xaxis={'title':'Start time'},
			yaxis={'title':'Duration'},
			margin={'t':40},
			legned={'y':1,'x':0},
			hovermode='closest',
		)
	}

	groupstation=filtered_df.groupby(['Start Station Name'])['Start Station Name'].count()
	groupendstation=filtered_df.groupby(['End Station Name'])['End Station Name'].count()

	pie_plot={
		"data": [go.Pie(labels=groupstation.index, values=groupstation.values,
						marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1']}, textinfo='percent')],
		"layout": go.Layout(title="Top frequent start stations", margin={'l': 90, 'r': 1, 't': 1, 'b': 90},
							legend={"x": 2, "y": 2})
	}
	parallel=px.parallel_coordinates(filtered_df,title='Parallel Coordinates',dimensions=['Trip Duration','Start Station ID','Start Station Latitude','Start Station Longitude','End Station ID','End Station Latitude','End Station Longitude','Bike ID','Birth Year','Gender'],
                labels={'Trip Duration':'Duration','Start Station ID':'Start ID','Start Station Latitude':'Start Lat.','Start Station Longitude':'Start Longi.','End Station ID':'End ID','End Station Latitude':'End Lat.','End Station Longitude':'End Longi.','Bike ID':'Bike ID','Birth Year':'Birth Year','Gender':'Gender'}
            )

	end_pie_plot={
		"data": [go.Pie(labels=groupendstation.index, values=groupendstation.values,
						marker={'colors': ['#EF963B', '#C93277', '#349600', '#EF533B', '#57D4F1']}, textinfo='percent')],
		"layout": go.Layout(title="Top frequent end stations", margin={'l': 90, 'r': 1, 't': 1, 'b': 90},
							legend={"x": 2, "y": 2})
	}

	return pie_plot,end_pie_plot,scatter_plot,parallel


@app.callback(
	Output('line-charts', 'figure'),
	[Input('crossfilter-xaxis-column', 'value'),
	 Input('crossfilter-yaxis-column', 'value'),
	 ])
def update_graph(xaxis_column_name, yaxis_column_name,
				 ):
	dff = df[df['Start Station Name'] == xaxis_column_name]
	return {
		'data': [dict(
			x=dff['Start Time'],
			y=dff[dff['End Station Name'] == yaxis_column_name]['Trip Duration'],
			marker={
				'size': 15,
				'opacity': 0.5,
			}
		)],
		'layout': dict(
			title='Form {0} to {1}'.format(xaxis_column_name,yaxis_column_name),
			xaxis={
				'title': "Start Time",
			},
			yaxis={
				'title': "Time Duration",
			},

			hovermode='closest'
		)
	}





if __name__=="__main__":
	app.run_server(debug=True)