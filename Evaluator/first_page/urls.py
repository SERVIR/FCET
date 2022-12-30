'''
This module routes urls to specific files used by ExtJS 
including the main page. The structure is specific to an ExtJS app, 
but it's possible to interchange some components with little hassle.
'''

from django.urls import re_path as url
from first_page import views

urlpatterns  = [
    url(r'^$', views.index),
    url(r'^app/app.js$', views.app),
    url(r'^app/view/Viewport.js$', views.viewport),
    url(r'^app/view/Overview.js$', views.overview),
    url(r'^app/view/DefineStudyYears.js$', views.define_study_years),
    url(r'^app/view/DefineStudyArea.js$', views.define_study_area),
    url(r'^app/view/LimitPlotTypes.js$', views.limit_plot_types),
    url(r'^app/view/SelectPolicyAreas.js$', views.select_policy_areas),
    url(r'^app/view/SelectControlAreas.js$', views.select_control_areas),
    url(r'^app/view/MatchSimilarPlots.js$', views.match_similar_plots),
    url(r'^app/view/CheckBalanceStatistics.js$', 
        views.check_balance_statistics),
    url(r'^app/view/MeasureTreatmentEffects.js$', 
        views.measure_treatment_effects),
    url(r'^app/view/Report.js$', views.report),
    url(r'^app/view/CheckSensitivity.js$', views.check_sensitivity),
    url(r'^app/view/MainMap.js$', views.main_map),
    url(r'^app/view/CS.js$', views.cs),
    url(r'^app/view/MSP.js$', views.msp),
    url(r'^app/view/MTE.js$', views.mte),
    url(r'^app/model/Station.js$', views.station_model),
    url(r'^app/model/Song.js$', views.song),
    url(r'^app/store/RecentSongs.js$', views.recent_songs_store),
    url(r'^app/store/Stations.js$', views.stations_store),
    url(r'^app/store/SearchResults.js$', views.search_results_store),
    url(r'^app/controller/Station.js$', views.station_controller),
    url(r'^app/controller/Song.js$', views.song_controller),
    url(r'^geoserver/evaluator/wms$', views.geoserver_wms),
    url(r'^geoserver/evaluator/wfs$', views.geoserver_wfs),
]
