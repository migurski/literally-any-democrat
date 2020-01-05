LiterallyAnyDemocrat/build:
	python -c 'import LiterallyAnyDemocrat as lad, flask_frozen as ff; ff.Freezer(lad.app).freeze()'

live: LiterallyAnyDemocrat/build
	aws s3 sync --acl public-read --cache-control 'public, max-age=300' --delete \
		$^/ s3://literallyanydemocrat.com-live/

clean:
	rm -rf LiterallyAnyDemocrat/build
