from django.urls import path
from data_analytics.views import (
                                    file_analyze,
                                    file_upload,
                                    file_gpt,
                                    trend_analysis,
                                    anomaly_detection,
                                )


urlpatterns = [
    path('upload', file_upload.FileUploadView.as_view(), name='s3-upload'),
    path('analyze', file_analyze.AnalyzeFileView.as_view(), name='analyze-file'),
    path('analyze_website', file_analyze.AnalyzeWebsiteView.as_view(), name='analyze-website'),

    path('file_view', anomaly_detection.WorkbookUploadView.as_view(), name='file-view'),
    path('get_anomaly', anomaly_detection.AnomalyDetectionView.as_view(), name='get_anomaly'),

    path('trend_analysis', trend_analysis.TAFileUploadView.as_view(), name='trend-analysis-upload'),
    path('trend_analysis_files', trend_analysis.TAFileView.as_view(), name='trend-analysis-files'),
    path('trend_analysis_data', trend_analysis.TAPlotDataView.as_view(), name='trend-analysis'),
    path('trend_analysis_commentary', trend_analysis.TACommentaryView.as_view(), name='trend-analysis-commentary'),
    path('trend_analysis_summary', trend_analysis.TASummaryView.as_view(), name='trend-analysis-summary'),

    path('file_gpt', file_gpt.FileGPTView.as_view(), name='file-gpt'),
    path('file_gpt_query', file_gpt.FileGPTQueryView.as_view(), name='file-gpt-query'),
]
