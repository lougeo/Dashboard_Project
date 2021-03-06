import os
from django.conf import settings
from django.template import Context
import base64
from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa
from matplotlib.figure import Figure


def is_employee(user):
    if user.groups.filter(name="Manager").exists() | user.groups.filter(name="Technician").exists():
        return True
    else:
        return False

def is_manager(user):
    return user.groups.filter(name="Manager").exists()

def link_callback(uri, rel):

    sUrl = settings.STATIC_URL
    sRoot = settings.STATIC_ROOT
    mUrl = settings.MEDIA_URL
    mRoot = settings.MEDIA_ROOT

    # Convert URIs to absolute system paths
    if uri.startswith(mUrl):
        path = os.path.join(mRoot, uri.replace(mUrl, ""))
    elif uri.startswith(sUrl):
        path = os.path.join(sRoot, uri.replace(sUrl, ""))
    else:
        return uri  # handle absolute uri (ie: http://some.tld/foo.png)

    # make sure that file exists
    if not os.path.isfile(path):
            raise Exception(
                'media URI must start with %s or %s' % (sUrl, mUrl)
            )
    return path

def render_to_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    result = BytesIO()
    pdf = pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result, link_callback=link_callback)
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    return None

def plot_sieve_report(test_data, min_bounds, max_bounds):
    # Generate plot
    fig = Figure()
    ax = fig.subplots()
    ax.plot(test_data, color='blue', label='Test Data')
    ax.plot(min_bounds, color='red', label='Bounds')
    ax.plot(max_bounds, color='red')
    ax.legend()
    ax.set_title("Sieve Analysis")
    ax.set_ylabel("Percent Passing")
    ax.set_xlabel("Sieve Number")
    # Save it to a temporary buffer
    buf = BytesIO()
    fig.savefig(buf, format='png')
    # Embed the result in the html output
    plot_data = base64.b64encode(buf.getbuffer()).decode("ascii")
    return plot_data