# Learning guide: templates, HTML, Jinja, and CSS

Read [the Python and Flask guide](learning-guide.md) for the backend and [the tests and project files guide](testing-and-project-files.md) for the rest of the project. This document explains the four files in `templates/` and every rule in `static/style.css`. Line numbers refer to the current source files. Some source lines contain several HTML elements; each is explained below.

## 1. Which computer runs which part?

Suppose the browser asks for `/login`:

1. Flask receives that HTTP request in Python.
2. The login function calls `render_template('auth.html', registering=False)`.
3. Jinja, Flask's template engine, evaluates the template on the server. It combines the page with `base.html`, chooses the login wording, and inserts the form token.
4. Flask sends the finished HTML to the browser. The browser does not receive the Python source or the Jinja instructions.
5. The browser sees the stylesheet link in that HTML and requests `/static/style.css`.
6. The browser uses HTML for the page's structure and CSS for its appearance.
7. Submitting the form sends another HTTP request. Flask processes it and responds with HTML or a redirect.

A template is an HTML file with instructions for generating HTML. A static file is served as a file without running Jinja on its contents. This project's stylesheet is static.

There is no JavaScript in this project. Ordinary links, forms, page navigation, password inputs, and browser form validation already work through HTML and HTTP. JavaScript would become useful for extra behaviour such as updating part of a page without navigation.

### Basic HTML syntax

```html
<label for="email">Email address</label>
<input id="email" name="email" type="email" required>
```

- `<label>` opens an element; `</label>` closes it. The text between them is its content.
- `for="email"` is an attribute: extra information about the element.
- HTML uses straight quotes around attribute values.
- `<input>` is a void element: it has no closing `</input>` tag.
- `required` is a Boolean attribute. Its presence makes the field required. Writing `required="false"` would still make it required because the attribute would still be present.
- Elements can contain other elements. That containment creates the document tree used by CSS and accessibility tools.
- `class` assigns reusable styling names. `class="card dashboard"` assigns two classes to one element.
- `id` identifies one particular element on the page. A label's `for` refers to an input's `id`.
- `name` identifies a field in the submitted form. Flask reads that name through `request.form`.

The distinction between `id` and `name` matters: changing `id="email"` affects label association and CSS/JavaScript selection; changing `name="email"` changes the key the backend receives.

### Basic Jinja syntax

| Syntax | Meaning | Example in this project |
|---|---|---|
| `{{ expression }}` | Evaluate an expression and insert its result into HTML | `{{ g.user['name'] }}` |
| `{% instruction %}` | Run template logic rather than insert its literal text | `{% if registering %}` |
| `{% if ... %}` / `{% endif %}` | Include content only when a condition is true | Registration-only fields |
| `{% for ... %}` / `{% endfor %}` | Repeat content for each item | Notification messages |
| `{% extends 'base.html' %}` | Use a parent template | All three page templates |
| `{% block title %}` / `{% endblock %}` | Define a region that a child template can replace | Browser tab title |
| `'A' if condition else 'B'` | Choose between two values | Login versus registration labels |

Jinja resembles Python, but it is a separate template language. In particular, Boolean `true` in `with_categories=true` is Jinja syntax; Python's equivalent is `True`.

### HTML escaping

For these HTML templates, Flask enables Jinja's normal HTML autoescaping. If a stored name is `<script>alert(1)</script>`, inserting it through `{{ g.user['name'] }}` produces escaped text such as `&lt;script&gt;`, so it displays as text in this location instead of becoming a script element. The test suite checks this example.

Escaping concerns output. It does not prevent SQL injection; bound SQL parameters do that separately. Do not add Jinja's `|safe` filter to untrusted user text: that would tell Jinja to skip this escaping.

## 2. `templates/base.html`: the shared page frame

This file has 19 lines. It supplies the document structure, logo, navigation, notifications, and footer. Reusing it keeps those things consistent across every page.

**Line 1 — `<!doctype html>`**

Declares a modern HTML document so the browser uses standards mode.

**Line 2 — `<html lang="en">`**

Opens the document's root element. `lang="en"` identifies English, which helps screen readers and other language-aware browser features.

**Line 3 — `<head>`**

Opens the metadata area. This contains information about the page rather than its main visible content.

**Line 4 — `<meta charset="utf-8">`**

Tells the browser how to interpret the text encoding. UTF-8 supports punctuation such as the arrow, apostrophe, and middle dot used in the templates.

**Line 5 — `<meta name="viewport" content="width=device-width, initial-scale=1">`**

Makes the layout viewport match the device width and starts at the normal scale. This lets the CSS mobile rules work as intended on narrow screens.

**Line 6 — the `<title>` element**

```html
<title>{% block title %}Miserly{% endblock %} · Business tracker</title>
```

The browser uses this text for the tab title. The default block content is `Miserly`. A child page can replace that part, while ` · Business tracker` stays shared. For example, the dashboard title becomes `Dashboard · Business tracker`.

**Line 7 — the stylesheet link**

```html
<link rel="stylesheet" href="{{ url_for('static', filename='style.css') }}">
```

`<link>` connects an external resource. `rel="stylesheet"` identifies it as CSS. `href` gives its address. `url_for` generates the address for Flask's built-in `static` endpoint, with `filename='style.css'`; here the result is normally `/static/style.css`. This uses Flask's routing rather than manually writing the URL.

**Lines 8–9 — `</head>` and `<body>`**

Close the metadata and open the visible document body.

**Line 10 — header, logo link, and tagline**

- `<header>` groups the top area of the page.
- `<a class="brand" href="{{ url_for('index') }}">` creates a styled link to the `index` endpoint, whose URL is `/`.
- `<b>m.</b>` creates the little logo text. CSS gives it a green rounded background.
- `Miserly` is the visible brand name next to that logo.
- `</a>` ends the link.
- `<span class="tagline">Small steps. Smarter business.</span>` adds a short inline slogan.

`<span>` is a generic inline container. It is useful when you need a styling hook around a small piece of text.

**Line 11 — conditional logout form**

```html
{% if g.user %}
  <form method="post" action="{{ url_for('logout') }}">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button class="secondary" type="submit">Log out</button>
  </form>
{% endif %}
```

This is one source line, expanded here to make its parts visible.

- `g.user` is the current user row loaded by the backend. A real row makes the condition true; `None` makes it false.
- The template includes the form only when someone is logged in. Backend protection is still necessary: hiding a button alone does not protect a route.
- `<form>` groups fields and specifies how to submit them.
- `method="post"` submits using HTTP POST because logout changes authentication state.
- `action` specifies the URL to submit to; `url_for('logout')` generates `/logout`.
- The hidden input sends the CSRF token with the form. Hidden means it is not shown as a normal control, not that it is secret from the person using the browser.
- `csrf_token()` is a Python helper made available to Jinja. It obtains or creates a random token for the session.
- The backend compares the submitted token against the one in the session before accepting POST requests.
- `type="submit"` makes the button submit the form; `secondary` chooses its CSS styling.

CSRF means cross-site request forgery: a different site tries to make a user's browser submit an unwanted request. Requiring the matching token makes this harder because another origin normally cannot read the legitimate page's token. Tokens do not encrypt the form or replace HTTPS.

**Lines 12–13 — `</header>` and `<main>`**

Close the top area and open the page's main content area. Semantic elements such as `header`, `main`, and `footer` describe the roles of document regions.

**Line 14 — notification loop**

```html
{% for category, message in get_flashed_messages(with_categories=true) %}
  <div class="notice {{ category }}"
       role="{{ 'alert' if category == 'error' else 'status' }}">
    {{ message }}
  </div>
{% endfor %}
```

- `flash(...)` in Python stores a short message for a following rendered response.
- `get_flashed_messages(...)` retrieves those messages for display.
- `with_categories=true` includes the category along with each message.
- `for category, message in ...` unpacks each pair into two template names.
- `<div>` is a generic block container.
- `class="notice {{ category }}"` becomes, for example, `class="notice error"` or `class="notice success"`.
- CSS applies `.notice` to both; `.notice.error` adds the error colours.
- `role="alert"` tells assistive technology that an error is an urgent message; `status` identifies a less urgent status update. Actual announcement behaviour depends on the assistive technology and page navigation.
- `{{ message }}` inserts escaped message text.
- `{% endfor %}` ends the loop. With no messages, nothing is inserted.

**Line 15 — `{% block content %}{% endblock %}`**

The replaceable main-content region. Each child template supplies its own content here.

**Line 16 — `</main>`**

Closes the main region.

**Line 17 — footer**

`<footer>Miserly · Your business, in balance.</footer>` supplies the same closing text on every page.

**Lines 18–19 — `</body>` and `</html>`**

Close the visible body and the document.

## 3. `templates/auth.html`: one template for two forms

This file has 21 lines. `registering=True` gives the registration version; `registering=False` gives the login version. Sharing a template avoids maintaining two almost identical forms.

**Line 1 — `{% extends 'base.html' %}`**

Selects the parent template. The blocks below fill regions in that parent.

**Line 2 — title block**

```jinja
{% block title %}{{ 'Create account' if registering else 'Log in' }}{% endblock %}
```

Chooses the tab title according to `registering`. This variable is supplied by `render_template(...)` in Python.

**Line 3 — `{% block content %}`**

Begins the main content supplied to the parent.

**Line 4 — `<div class="auth-layout">`**

Wraps the introduction and form. CSS makes these two columns on wide screens and one column on narrow screens.

**Line 5 — introduction and decorative chart**

The long line contains:

- `<section class="intro">`: a meaningful grouping for the introduction.
- `<span class="eyebrow">`: the small uppercase label above the main heading.
- `<h1>`: the principal heading, “A little clarity. A lot of possibility.”
- `<br>`: an explicit line break between the two phrases; it has no closing tag.
- `<p>`: a paragraph describing the app.
- `<div class="illustration" aria-hidden="true">`: a decorative illustration. `aria-hidden="true"` excludes it and its descendants from the accessibility tree, so screen readers do not need to announce decorative bars.
- `Keep growing.`: decorative text inside the illustration.
- `<div class="bars">`: the flex container for the chart-like shapes.
- Five empty `<i></i>` elements: CSS gives each a width, colour, and height. They contain no data and are only decorative. Although `<i>` commonly marks alternate-voice text, these empty elements are being used as styling hooks here.
- The closing `</div>` tags and `</section>` finish the nested containers in reverse order.

The bars are not real business statistics. Their heights are fixed CSS values.

**Line 6 — `<section class="card">`**

Opens the white rounded panel containing the form.

**Line 7 — eyebrow text**

Displays “LET’S GET STARTED” with the same small-label styling used elsewhere.

**Line 8 — conditional `<h2>`**

Shows `Create your account` for registration or `Welcome back` for login.

**Line 9 — conditional paragraph**

Shows the registration introduction or the login introduction. The conditional expression chooses text; it does not run any authentication.

**Line 10 — `<form method="post">`**

Uses POST. No `action` is specified, so the browser submits to the current page URL: `/register` on the registration page and `/login` on the login page.

GET requests show the form. POST requests submit its values. GET and POST are HTTP methods, not Python keywords. Passwords belong in a POST body rather than a URL query string, but POST still needs HTTPS for network confidentiality outside local development.

**Line 11 — hidden CSRF input**

Works like the logout token in the base template. The field's name is `csrf_token`; that is the key read by `request.form.get('csrf_token', '')` in Python.

**Line 12 — registration-only name field**

```html
{% if registering %}
  <label for="name">Full name</label>
  <input id="name" name="name" autocomplete="name" maxlength="80"
         value="{{ request.form.get('name', '') }}" required>
{% endif %}
```

- The `if` excludes this entire field from the login page.
- `for="name"` and `id="name"` connect the label and field. Clicking the label focuses the input.
- `name="name"` makes the submitted field available as `request.form['name']`.
- With no explicit `type`, this input defaults to a text field.
- `autocomplete="name"` tells the browser what kind of saved information it may offer.
- `maxlength="80"` limits ordinary browser editing to 80 characters. Python separately checks the name length because HTTP requests can bypass browser controls.
- `value` sets the displayed input value.
- `request.form.get('name', '')` retrieves the submitted name, or the empty string if absent. This preserves the name after a validation error, so the user does not need to retype it.
- `required` enables browser-side required-field checking.

**Line 13 — email field**

`<label for="email">` connects to `id="email"`. `name="email"` is the form key the backend reads.

- `type="email"` asks the browser to use its email-field behaviour, such as a suitable mobile keyboard and basic format validation.
- `autocomplete="email"` describes the expected saved value.
- `maxlength="254"` limits browser entry length.
- `placeholder="you@example.com"` is a hint displayed when empty; it is not a submitted default and does not replace the label.
- `value="{{ request.form.get('email', '') }}"` preserves the submitted address after errors. Jinja escapes it before placing it in the quoted HTML attribute.
- `required` disallows an empty field in normal browser submission.

The browser's email validation and the backend's simple email checks are not identical. Neither confirms that the mailbox exists or belongs to the user.

**Line 14 — password field**

```html
<label for="password">Password</label>
<input id="password" name="password" type="password"
       autocomplete="{{ 'new-password' if registering else 'current-password' }}"
       {% if registering %}minlength="8" aria-describedby="password-help"{% endif %}
       maxlength="128" required>
```

- The label and input identifiers follow the same pattern as the other fields.
- `type="password"` masks the visible characters. It does not hash or encrypt the password.
- `autocomplete="new-password"` tells password managers that registration creates a password. `current-password` marks an existing login password.
- On registration only, `minlength="8"` sets the browser's minimum length and `aria-describedby="password-help"` connects the field to its explanatory text.
- `maxlength="128"` sets the browser maximum; Python also checks its limit.
- `required` means it must be filled in for normal browser submission.
- There is deliberately no `value` attribute containing a previously entered password. After a failed submission the password fields are blank.

**Line 15 — registration-only help and confirmation**

- `{% if registering %}` includes these elements only on registration.
- `<small id="password-help">` displays the length guidance. Its `id` is the target of the previous input's `aria-describedby`.
- `<label for="confirm_password">Confirm password</label>` labels the confirmation control.
- `<input id="confirm_password" name="confirm_password" type="password">` creates the masked confirmation field and its backend form key.
- `autocomplete="new-password"`, `minlength="8"`, `maxlength="128"`, and `required` have the meanings above.
- `{% endif %}` ends the conditional.

HTML does not compare the two password fields here. The Python registration function checks equality. The confirmation password is not stored in the database.

**Line 16 — submit button**

- `class="primary"` selects the large green button styling.
- `type="submit"` submits the enclosing form.
- The Jinja expression chooses `Create account` or `Log in`.
- `<span aria-hidden="true">→</span>` adds a decorative arrow without adding it to the accessible button text.

**Line 17 — `</form>`**

Closes the form. The account-switch link below is outside the submitted form.

**Line 18 — switch between registration and login**

The `<p class="switch">` displays either `Already have an account?` or `New to Miserly?`. The anchor's `href` uses:

```jinja
{{ url_for('login' if registering else 'register') }}
```

On registration it links to login; on login it links to registration. The link text uses a second conditional to match the destination. Clicking this link sends a normal GET request; it does not submit the form.

**Lines 19–21 — closing elements and block**

- Line 19 closes the card's section.
- Line 20 closes the two-column layout wrapper.
- Line 21 ends the child template's content block.

## 4. `templates/dashboard.html`: the protected page

This file has five lines.

| Line | Explanation |
|---|---|
| 1 | Extends `base.html` so the dashboard gets the shared header, stylesheet, notices, and footer. |
| 2 | Replaces the title block with `Dashboard`. |
| 3 | Begins the content block. |
| 4 | Supplies the visible dashboard, explained below. |
| 5 | Ends the content block. |

Line 4 contains:

- `<section class="card dashboard">`: applies both the general card style and dashboard sizing.
- `<span class="eyebrow">YOUR WORKSPACE</span>`: a small label.
- `<h1>Hello, {{ g.user['name'] }}.</h1>`: reads the `name` column from the user row loaded in Python and inserts it as escaped text.
- `<p>You’re logged in as ...</p>`: a descriptive paragraph.
- `<strong>{{ g.user['email'] }}</strong>`: gives the email semantic emphasis, normally rendered bold.
- `<div class="empty-state">`: a styled placeholder for future team work.
- `<h2>`: the placeholder heading.
- The following `<p>` explains where spending entries, purchase history, and reports can be added.
- `</div></section>` close the nested elements.

The template displays information; it does not enforce authentication. The Python `@login_required` decorator is what prevents an unauthenticated request from reaching it. The dashboard currently has no real business-tracking data or calculations.

## 5. `templates/error.html`: rejected form submissions

This file has three lines.

- **Line 1:** extends the shared base.
- **Line 2:** sets the title block to `Form expired`.
- **Line 3:** opens the content block, displays a section with both `card` and `dashboard` styles, adds the heading `Please try again`, explains that the form could not be verified, and provides a link generated by `url_for('index')` to return to `/`. It then closes the section and the block.

The backend returns this page with HTTP status `400` when a POST's CSRF token is missing or fails to match. The heading `Form expired` is user-facing wording: the application does not implement a separate timestamp or per-form expiry timer. A token can become invalid after the session changes or is cleared.

## 6. Understanding CSS syntax before reading the rules

The stylesheet is stored on one long physical line. Its rules are expanded below for explanation; the actual stylesheet has not been changed.

```css
.card {
  background: #fff;
  padding: 38px;
}
```

- `.card` is the selector: which elements to style.
- `{ ... }` contains the declarations for that selector.
- Each declaration has `property: value;` syntax.
- The leading dot selects a class, not a filename extension.
- CSS whitespace is usually not significant between these declarations. It can be formatted onto several lines without changing the result.
- `header` selects elements by tag name.
- `.brand b` selects any `b` descendant inside an element with class `brand`; the space means descendant, not necessarily direct child.
- `.notice.error` selects an element with both classes. It has no space.
- `button,input` is a selector list: apply to both.
- `:hover`, `:focus`, `:focus-visible`, and `:nth-child(...)` are pseudo-classes, selecting elements by state or position.
- `:root` selects the root element, normally `<html>`.
- `*` matches all elements.

Most size values here use CSS pixels (`px`). These are browser layout units; they do not necessarily equal one physical screen pixel. `%` is relative to a relevant parent dimension. `vw` is viewport width: `4vw` equals 4% of that width. `fr` is a share of available space in CSS Grid.

Colours use hexadecimal red/green/blue values: `#203d32`, for example, is a dark green. `#fff` is shorthand for `#ffffff`. Eight-digit hex, such as `#203d3206`, adds an alpha channel: the final `06` makes the colour very transparent.

Properties such as `color`, `font-family`, and `line-height` commonly inherit to children. Properties such as padding and borders generally do not. The cascade decides between competing rules using factors including importance, specificity, and source order. Media-query rules below apply only when their condition is true.

## 7. Every CSS rule and declaration

### Document defaults

```css
:root {
  font-family: system-ui, -apple-system, "Segoe UI", sans-serif;
  color: #203d32;
  background: #f5f7f2;
  line-height: 1.6;
}
* { box-sizing: border-box; }
body { margin: 0; }
a { color: #286547; text-underline-offset: 4px; }
button,input { font: inherit; }
```

- `font-family` is an ordered fallback list. The browser uses an available system font, with a generic sans-serif fallback. Quotes group the multiword font name `Segoe UI`.
- Root `color` makes the default text dark green.
- Root `background` supplies the pale page background.
- Unitless `line-height:1.6` sets a line box about 1.6 times the element's font size, improving readability.
- Universal `box-sizing:border-box` includes padding and border within declared element widths and heights. This helps `width:100%` inputs fit their parent.
- `body{margin:0}` removes the browser's default body margin.
- `a` changes link colour and places its underline 4px below the text.
- `font:inherit` makes buttons and inputs use the surrounding font rather than their browser default form-control font.

### Header and brand

```css
header {
  max-width: 1180px;
  margin: auto;
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px 36px;
}
.brand {
  display: flex;
  align-items: center;
  gap: 10px;
  text-decoration: none;
  font-size: 24px;
  font-weight: 750;
  color: #203d32;
}
.brand b {
  display: grid;
  place-items: center;
  background: #286547;
  color: white;
  border-radius: 12px;
  width: 42px;
  height: 42px;
}
.tagline { margin-left: auto; font-size: 13px; color: #637469; }
```

- Header `max-width` caps its total border-box width at 1180px while allowing a smaller width on narrow screens.
- `margin:auto` automatically distributes available outer space; for this block's horizontal margins it centres the header.
- `display:flex` lays out its direct children in a row by default.
- `align-items:center` centres those children vertically within the row.
- `gap:24px` separates adjacent flex items.
- Two-value `padding:28px 36px` means 28px top/bottom and 36px left/right. Padding is space inside the element.
- `.brand` is itself a flex container so its little logo and text line up; it uses 10px between them.
- `text-decoration:none` removes the normal link underline for the brand.
- `font-size:24px` sets its text size; `font-weight:750` requests a heavy weight, with actual appearance depending on the available font.
- Brand `color` sets the dark text.
- `.brand b` uses Grid for a simple centring task. `place-items:center` centres its content on both axes.
- Its green `background` and white `color` create the logo tile.
- `border-radius:12px` rounds the tile's corners.
- Its `width` and `height` make it 42px square.
- `.tagline` uses `margin-left:auto` to consume available flex space before it, pushing it toward the right.
- Tagline `font-size:13px` and muted `color` keep it visually secondary.

### Main layout and introduction

```css
main { max-width: 1100px; margin: 35px auto; padding: 0 28px; }
.auth-layout {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 80px;
  align-items: center;
}
.intro h1 {
  font-size: clamp(36px,4vw,52px);
  line-height: 1.14;
  letter-spacing: -2px;
  margin: 20px 0;
}
.intro p { max-width: 370px; color: #637469; font-size: 17px; }
.eyebrow { font-size: 11px; font-weight: 750; letter-spacing: 2px; color: #54795c; }
```

- `main` has a maximum width of 1100px.
- `margin:35px auto` gives it 35px outer space above/below and automatic centring horizontally.
- `padding:0 28px` adds no top/bottom inner space and 28px at the sides.
- `.auth-layout` uses a grid. `grid-template-columns:1fr 1fr` divides available column space equally between the introduction and card.
- `gap:80px` separates those columns; `align-items:center` centres grid items along the vertical axis within their grid areas.
- `clamp(36px,4vw,52px)` chooses a responsive heading size: normally 4% of viewport width, but no smaller than 36px and no larger than 52px.
- Heading `line-height:1.14` packs heading lines more tightly than body text.
- `letter-spacing:-2px` reduces the space between characters.
- Heading `margin:20px 0` means 20px above/below, zero at the sides.
- `.intro p` limits paragraph width to 370px, uses muted green-grey text, and sets 17px type.
- `.eyebrow` uses 11px heavy text, 2px extra letter spacing, and a muted green colour. The uppercase letters themselves are written in the HTML, not generated by CSS.

### Card, headings, and paragraph text

```css
.card {
  background: #fff;
  border: 1px solid #e0e6dc;
  border-radius: 22px;
  padding: 38px;
  box-shadow: 0 12px 40px #203d3206;
}
.card h2 { font-size: 28px; letter-spacing: -.8px; margin: 12px 0 4px; }
.card p { color: #637469; margin-top: 0; }
```

- The card gets a white background.
- `border:1px solid #e0e6dc` is shorthand for border width, line style, and colour.
- `border-radius:22px` rounds all corners.
- `padding:38px` adds the same inner space on all four sides.
- `box-shadow:0 12px 40px #203d3206` describes zero horizontal offset, 12px downward offset, 40px blur, and a very transparent green shadow. No spread value is supplied, so the default is used.
- `.card h2` selects level-two headings anywhere inside a card, sets 28px text and slightly tighter letter spacing.
- Three-value `margin:12px 0 4px` means top 12px, left/right 0, bottom 4px.
- `.card p` uses muted text and removes the paragraph's top margin.

### Labels, inputs, focus, and helper text

```css
label { display: block; font-size: 13px; font-weight: 650; margin: 18px 0 6px; }
input {
  display: block;
  width: 100%;
  padding: 11px 13px;
  border: 1px solid #cdd7ce;
  border-radius: 8px;
  background: #fcfdfb;
  color: #203d32;
}
input:focus { outline: 3px solid #b9d9b8; outline-offset: 2px; }
small { color: #637469; font-size: 12px; }
```

- `display:block` makes labels start on their own line.
- Labels use 13px text with weight 650, and margins of 18px above, zero at the sides, 6px below.
- Visible inputs are block controls with `width:100%` of the available containing width. A hidden input remains hidden because of its HTML hidden-input behaviour.
- Input padding is 11px vertically and 13px horizontally.
- Input borders are 1px solid muted green-grey; corners are rounded by 8px.
- A near-white background and dark-green text set field colours.
- `input:focus` matches a field receiving keyboard input. Its 3px pale-green outline is offset 2px outside the border.
- An outline does not take up layout space in the way a border does.
- `small` helper text uses the muted text colour and 12px size.

### Buttons and account-switch text

```css
button { cursor: pointer; border-radius: 8px; font-weight: 650; }
.primary {
  width: 100%;
  background: #286547;
  color: white;
  border: 0;
  padding: 12px 16px;
  margin-top: 24px;
  display: flex;
  justify-content: space-between;
}
.primary:hover { background: #1d5036; }
.secondary { background: white; border: 1px solid #cdd7ce; padding: 8px 16px; color: #286547; }
.switch { font-size: 13px; text-align: center; margin: 24px 0 0!important; }
.switch a { font-weight: 650; }
```

- All buttons use a pointing-hand cursor, 8px corners, and weight 650.
- The primary button fills the available width, has a green background and white text, removes its border, and adds 12px vertical/16px horizontal padding.
- `margin-top:24px` separates it from the fields.
- It is a flex container. Its text and arrow are laid out along the row; `justify-content:space-between` puts available space between them.
- `.primary:hover` darkens the button when a pointer hovers over it. Hover is visual feedback, not form submission logic.
- `.secondary` makes the logout button white with a thin border, 8px vertical/16px horizontal padding, and green text.
- `.switch` sets 13px centred text.
- Its margin is 24px top and 0 on the remaining sides. `!important` gives this declaration priority over ordinary competing margin declarations, including the general `.card p` rule. There is no need to copy this technique into every rule; it is just how this stylesheet handles that one override.
- `.switch a` gives only the links inside switch paragraphs weight 650.

### Notification messages

```css
.notice {
  padding: 12px 18px;
  margin-bottom: 22px;
  border-radius: 10px;
  border: 1px solid #bdd7be;
  background: #e7f2e5;
}
.notice.error { border-color: #e9c5be; background: #fff0eb; color: #873f31; }
```

- Every notice gets 12px vertical/18px horizontal padding, a 22px gap below it, 10px rounded corners, a thin green border, and a pale-green background.
- `.notice.error` matches elements that have both `notice` and `error` classes. It changes the border colour, background, and text to warm error colours.
- There is no separate `.success` CSS rule. A `notice success` uses the basic `.notice` styling.

### Decorative illustration and bars

```css
.illustration {
  margin-top: 35px;
  background: #e5eddd;
  border-radius: 20px;
  padding: 25px 30px;
  max-width: 350px;
  transform: rotate(-2deg);
  font-weight: 650;
}
.bars { display: flex; gap: 14px; height: 110px; align-items: end; margin-top: 18px; }
.bars i { flex: 1; background: #85a883; border-radius: 7px 7px 0 0; height: 30%; }
.bars i:nth-child(2) { height: 45%; }
.bars i:nth-child(3) { height: 60%; }
.bars i:nth-child(4) { height: 78%; }
.bars i:nth-child(5) { height: 100%; background: #286547; }
```

- The illustration has 35px of outer space above, a pale-green background, 20px rounded corners, 25px vertical/30px horizontal padding, and at most 350px width.
- `transform:rotate(-2deg)` visually rotates it by negative two degrees, giving a slight tilt. The surrounding layout is calculated before this visual transform.
- Its text weight is 650.
- `.bars` lays its children out as a flex row, separated by 14px, in a 110px-high container.
- `align-items:end` aligns the bars at the end of the cross axis—at the bottom for this row.
- `margin-top:18px` separates the bars from “Keep growing.”
- `.bars i` selects the `i` elements inside that container.
- `flex:1` lets the bars share available horizontal space evenly. It is flex shorthand for growing and shrinking with a zero basis in this normal browser use.
- Bars start with a muted-green background.
- `border-radius:7px 7px 0 0` rounds top-left and top-right corners but leaves the bottom-right and bottom-left corners square. Four-value corner order starts at the top-left and travels clockwise.
- Default `height:30%` makes the first bar 30% of the 110px container height.
- `:nth-child(2)`, `(3)`, and `(4)` target the second, third, and fourth child elements, increasing height to 45%, 60%, and 78%.
- `:nth-child(5)` makes the last bar full height and dark green.
- These percentages are presentation values, not queries into the database.

### Dashboard and placeholder

```css
.dashboard { max-width: 800px; margin: 60px auto; }
.dashboard h1 { font-size: 36px; margin: 14px 0; }
.empty-state {
  padding: 28px;
  background: #f5f7f2;
  border: 1px dashed #cdd7ce;
  border-radius: 12px;
  margin-top: 32px;
}
.empty-state h2 { font-size: 22px; }
.empty-state p { margin-bottom: 0; }
```

- `.dashboard` limits the card to 800px, centres it horizontally, and gives it 60px outer space above/below.
- Its main heading is 36px with 14px above/below and zero side margins.
- `.empty-state` adds 28px inner space, the page's pale background, a 1px dashed border, 12px corners, and 32px separation above.
- `.empty-state h2` uses 22px instead of the general card heading's 28px. This later rule has the same selector specificity, so its font size wins by source order.
- `.empty-state p` removes bottom paragraph margin to keep the inner spacing balanced.

### Footer and keyboard focus

```css
footer { text-align: center; color: #748171; font-size: 12px; padding: 30px; }
button:focus-visible,a:focus-visible { outline: 3px solid #85a883; outline-offset: 4px; }
```

- The footer centres its text, uses muted 12px type, and adds 30px inner space on all sides.
- `:focus-visible` applies when the browser considers a visible focus indicator useful, typically during keyboard navigation.
- Buttons and links then get a 3px green outline, positioned 4px outside their edges. This helps users see which control will activate when they press Enter or Space as appropriate.

### Every mobile override

```css
@media(max-width:760px) {
  header { padding: 20px; }
  .tagline { display: none; }
  header form { margin-left: auto; }
  main { margin: 15px auto; padding: 0 20px; }
  .auth-layout { grid-template-columns: 1fr; gap: 26px; }
  .intro h1 { font-size: 36px; }
  .intro p { font-size: 15px; }
  .illustration { display: none; }
  .card { padding: 26px; }
  .dashboard { margin: 20px auto; }
}
```

`@media(max-width:760px)` means the enclosed rules apply when the viewport is 760 CSS pixels wide or narrower. These are overrides of the earlier defaults, not a separate mobile webpage.

- Header padding becomes 20px on every side.
- `.tagline{display:none}` removes the slogan from layout and display to save horizontal space.
- `header form{margin-left:auto}` pushes the logout form to the right when the slogan is absent.
- Main margins become 15px vertically with horizontal centring; side padding becomes 20px.
- Authentication layout becomes one grid column (`1fr`), placing the form below the introduction; its gap shrinks to 26px.
- The introduction heading uses a fixed 36px mobile size.
- The introduction paragraph shrinks to 15px.
- The decorative illustration is hidden and takes up no layout space.
- Card padding decreases to 26px.
- Dashboard outer vertical spacing shrinks to 20px while keeping horizontal centring.

All CSS declarations in the current stylesheet are covered above. Resize your browser window to see these last rules take effect; the backend and database do not need to change for a responsive layout.

## 8. What you should be able to demonstrate

1. Open `auth.html` beside the running app and identify the email input. Explain why `name="email"` must agree with the Python code.
2. Compare `/login` and `/register`. Point to `registering` and explain how one template produces the two forms.
3. Show the shared logo and footer on both pages and explain template inheritance.
4. Submit mismatching registration passwords. Explain that the server checks them; HTML does not perform that comparison here.
5. Log in and show that the logout form appears because `g.user` now contains a user.
6. Use the browser's View Page Source or developer tools to see generated HTML. Explain why the Jinja `{% ... %}` instructions are absent from the response.
7. Resize the browser below 760px and explain the media query.
8. Identify the decorative chart and state honestly that its bars are CSS shapes rather than business data.

Practice answering: “HTML defines the document and form fields; Jinja generates that document on the server using Python-provided values; CSS controls its presentation in the browser; Flask receives the form submission and implements the behaviour.”
