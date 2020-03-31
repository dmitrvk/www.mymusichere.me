STATIC = scores/static/scores
SCSS = scores/scss

compile-scss:
	pysassc $(SCSS)/style.scss $(STATIC)/style.css -s compressed
