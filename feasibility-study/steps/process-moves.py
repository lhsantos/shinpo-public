import datetime
import io
import json
import math
import zipfile

import plotly.graph_objs
import plotly.offline


def main():
    files = ['moves-kumedinfo$-2018-04-24.zip'.replace('$', format(i, '02d')) for i in
             [1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 13, 14]]
    data = {}
    json_zip = None
    for i in range(len(files)):
        file = files[i]
        with zipfile.ZipFile(file) as zf_root:
            with zf_root.open('json.zip') as zf_json_fp:
                json_zip = io.BytesIO(zf_json_fp.read())
            with zipfile.ZipFile(json_zip) as zf_json:
                activities = {}
                for zi in filter(lambda x: x.filename.startswith('json/daily/activities/activities_'),
                                 zf_json.infolist()):
                    with zf_json.open(zi) as day_activities:
                        for activity in json.load(day_activities):
                            date = activity['date']
                            date = '-'.join([date[:4], date[4:6], date[6:]])
                            by_date = activities.get(date, {})
                            for entry in filter(lambda e: e['activity'] == 'walking',
                                                activity.get('summary', None) or []):
                                by_date['distance'] = by_date.get('distance', 0) + entry['distance']
                                by_date['steps'] = by_date.get('steps', 0) + entry['steps']
                            activities[date] = by_date
                data[file] = activities

    graphs_daily, graphs_weekly = [], []
    dates = set()
    time_range = (datetime.date(2018, 3, 19), datetime.date(2018, 4, 8))
    days = (time_range[1] - time_range[0]).days + 1
    weeks = math.ceil(days / 7.0)
    total_daily, total_weekly = days * [0], weeks * [0]
    # weekly_x = [(time_range[0] + datetime.timedelta(7 * x)).strftime('%Y/%m/%d') + ' - ' + (
    #         time_range[0] + datetime.timedelta(7 * (x + 1) - 1)).strftime('%Y/%m/%d') for x in range(weeks)]
    weekly_x = ['week ' + str(x + 1) for x in range(weeks)]

    total_daily_x = [(time_range[0] + datetime.timedelta(x)).strftime('%Y-%m-%d') for x in range(days)]
    i = 1
    for user, activities in data.items():
        daily_x, daily_y = [], []
        weekly_y = weeks * [0]
        for date_str in sorted(activities):
            date = datetime.datetime.strptime(date_str, '%Y-%m-%d').date()
            if (date >= time_range[0]) and (date <= time_range[1]):
                dates.add(date)
                activity = activities[date_str]
                day = (date - time_range[0]).days
                week = day // 7
                print(date_str + ': ' + str(week))
                if 'steps' in activity:
                    daily_x.append(date)
                    daily_y.append(activity['steps'])
                    weekly_y[week] += activity['steps']
                    total_daily[day] += activity['steps']
                    total_weekly[week] += activity['steps']

        # graphs_daily.append(plotly.graph_objs.Scatter(x=x, y=y, mode='lines+markers',name=user))
        graphs_daily.append(plotly.graph_objs.Bar(x=daily_x, y=daily_y, name=i))
        graphs_weekly.append(plotly.graph_objs.Bar(x=weekly_x, y=weekly_y, name=i))
        i = i + 1

    plotly.offline.plot({
        'data': graphs_daily,
        'layout': {
            'title': 'Daily Steps',
            'xaxis': {'title': 'Date', 'tickvals': [date for date in sorted(dates)]},
            'yaxis': {'title': 'Steps'}
        }
    }, filename='steps_daily.html')
    plotly.offline.plot({
        'data': graphs_weekly,
        'layout': {
            'title': 'Weekly Steps',
            'xaxis': {'title': 'Week'},
            'yaxis': {'title': 'Steps'}
        }
    }, filename='steps_weekly.html')
    graphs_daily.append(plotly.graph_objs.Bar(x=total_daily_x, y=total_daily, name='Total'))
    graphs_weekly.append(plotly.graph_objs.Bar(x=weekly_x, y=total_weekly, name='Total'))
    plotly.offline.plot({
        'data': graphs_daily,
        'layout': {
            'title': 'Daily Steps',
            'xaxis': {'title': 'Date', 'tickvals': [date for date in sorted(dates)]},
            'yaxis': {'title': 'Steps'}
        }
    }, filename='steps_daily_with_total.html')
    plotly.offline.plot({
        'data': graphs_weekly,
        'layout': {
            'title': 'Weekly Steps',
            'xaxis': {'title': 'Week'},
            'yaxis': {'title': 'Steps'}
        }
    }, filename='steps_weekly_with_total.html')
    plotly.offline.plot({
        'data': [plotly.graph_objs.Bar(x=weekly_x, y=total_weekly, width=len(weekly_x) * [0.3], name='Total', )],
        'layout': {
            'title': 'Weekly Steps',
            'xaxis': {'title': 'Week'},
            'yaxis': {'title': 'Steps'}
        }
    }, filename='steps_weekly_total.html')


if __name__ == '__main__':
    main()
