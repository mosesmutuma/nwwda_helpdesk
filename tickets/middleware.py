from django.utils.deprecation import MiddlewareMixin

class InjectCustomCSSMiddleware(MiddlewareMixin):
    def process_response(self, request, response):
        # Only inject into admin pages
        if request.path.startswith('/admin/'):
            css_link = '<link rel="stylesheet" type="text/css" href="/static/css/admin_dashboard.css">'
            content = response.content.decode('utf-8')
            if '</head>' in content:
                content = content.replace('</head>', f'{css_link}</head>')
                response.content = content.encode('utf-8')
        return response