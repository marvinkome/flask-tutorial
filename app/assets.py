from flask_assets import Bundle

app_assets = {
    'main_css': Bundle(
        'lib/bootstrap/css/bootstrap.css',
        output='gen/main.css'),
    'main_js': Bundle(
        'lib/jquery/jquery.js',
        'lib/bootstrap/js/bootstrap.js',
        output='gen/main.js')
}
