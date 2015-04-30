help:
	@echo "make targets:"
	@echo "  setup"
	@echo "  serve"
	@echo "  release"
	@echo "  clean"
	
app/distlib.zip:
	virtualenv .
	bin/pip install Pillow
	bin/python2.7 bootstrap.py
	bin/buildout

setup: app/distlib.zip

serve: app/distlib.zip
	bin/dev_appserver --host 0.0.0.0 app

release: app/distlib.zip
	bin/appcfg update --oauth2 app

clean:
	rm -rf bin/ include/ lib/ app/distlib.zip develop-eggs/ parts/
