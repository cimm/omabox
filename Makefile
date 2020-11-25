NAME = "imv-kiosk"
APPLICATION_KEY_ID = ""
APPLICATION_KEY = ""
BUCKET = ""
FILENAME = $(join $(NAME), *.snap)

build:
	snapcraft

rebuild:
	snapcraft clean
	snapcraft

install:
	sudo snap install $(FILENAME) --dangerous

uninstall:
	sudo snap remove $(NAME) --purge

full: uninstall rebuild install
	spd-say "Beep, beep. Full rebuild done."

config:
	sudo snap set $(NAME) b2-application-key-id=$(APPLICATION_KEY_ID) b2-application-key=$(APPLICATION_KEY) b2-bucket=$(BUCKET)
	sudo snap get $(NAME)
