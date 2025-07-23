PROJECT_PLUGIN=card_deck_builder
install_local:
	@echo "Sourcing local_env.sh and installing plugin..."
	@source ./env/local_env.sh && mkdir -p "$${GIMP_PLUGIN_FOLDER}"  && \
	tar cvf - $(PROJECT_PLUGIN) | tar xv -C "$${GIMP_PLUGIN_FOLDER}" -f -