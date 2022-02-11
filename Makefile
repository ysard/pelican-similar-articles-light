 
# development & release cycle
fullrelease:
	fullrelease

check_setups:
	pyroma .

check_code:
	prospector pelican/plugins/similar_articles_light/
	check-manifest

sdist:
	python setup.py sdist
