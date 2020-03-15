LiterallyAnyDemocrat/build:
	python -c 'import LiterallyAnyDemocrat as lad, flask_frozen as ff; ff.Freezer(lad.app).freeze()'

live: LiterallyAnyDemocrat/build
	aws s3 sync --acl public-read --cache-control 'public, max-age=300' --delete \
		--exclude 'candidates.json' --exclude 'candidates.json.gz' \
		$^/ s3://literallyanydemocrat.com-live/
	gzip -v9 $^/candidates.json
	aws s3 cp --acl public-read --cache-control 'public, max-age=300' --content-encoding gzip \
		$^/candidates.json.gz s3://literallyanydemocrat.com-live/candidates.json

clean:
	rm -rf LiterallyAnyDemocrat/build
