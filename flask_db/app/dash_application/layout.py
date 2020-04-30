html_layout = """
<!DOCTYPE html>
<html lang="en">
    <head>
        {%metas%}
        <title>Dashboard</title>
        {%css%}
    </head>
    <body>
        <div class="navbar">
          <a href="/index">HOME</a>
          <a href="/inverters">INVERTERS</a>
          <a href="/meters">METERS</a>
          <a href="/graphs">GRAPHS</a>
       </div>
        {%app_entry%}
        <footer>
            {%config%}
            {%scripts%}
            {%renderer%}
        </footer>
    </body>
</html>
"""
