import sys
from flask import Flask, render_template, render_template_string, make_response
from flask_flatpages import FlatPages, pygments_style_defs, pygmented_markdown
from flask_frozen import Freezer
import babel


def html_renderer(text):
    prerendered_body = render_template_string(text)
    return pygmented_markdown(prerendered_body)


DEBUG = True
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.html'
FLATPAGES_ROOT = 'content'
FLATPAGES_MARKDOWN_EXTENSIONS = []
POST_DIR = 'posts'

app = Flask(__name__)
app.config['FLATPAGES_HTML_RENDERER'] = html_renderer
flatpages = FlatPages(app)
freezer = Freezer(app)
app.config.from_object(__name__)


def datetimeformat(value, format="%Y-%m-%d %H:%M:%S"):
    return value.strftime(format)


app.jinja_env.filters['datetime'] = datetimeformat


@app.route("/", methods=['GET'])
def posts():
    all_posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    all_posts.sort(key=lambda item: item['published_date'], reverse=True)
    return render_template('posts.html', posts=all_posts)


@app.route('/<category>/<name>/', methods=['GET'])
def post(category, name):
    path = '{}/{}'.format(POST_DIR, name)
    post = flatpages.get_or_404(path)
    return render_template('post.html', post=post)


@app.route('/<cat_name>/', methods=['GET'])
def get_category(cat_name):
    all_posts = [p for p in flatpages if p.path.startswith(POST_DIR) and p["category"] == cat_name]
    return render_template('category.html', posts=all_posts)


@app.route('/sitemap.xml', methods=['GET'])
def sitemap():
    posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    posts.sort(key=lambda item: item['published_date'], reverse=True)
    sitemap_xml = render_template('sitemap.xml', posts=posts)
    response = make_response(sitemap_xml)
    response.headers["Content-Type"] = "application/xml"
    return response


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(host='0.0.0.0', debug=True)
