# Définitions des variables
VENV := .venv
PYTHON := python3
PIP := $(VENV)/bin/pip

.PHONY: all venv install clean

# Action par défaut quand tu tapes juste "make"
all: install

# Création de l'environnement virtuel si le dossier n'existe pas
$(VENV):
	@echo "Création de l'environnement virtuel..."
	$(PYTHON) -m venv $(VENV)
	$(PIP) install --upgrade pip

# Installation des dépendances (gère aussi le cas où requirements.txt n'existe pas encore)
install: $(VENV)
	@echo "Installation des dépendances..."
	@if [ -f requirements.txt ]; then \
		$(PIP) install -r requirements.txt; \
	else \
		echo "Aucun fichier requirements.txt trouvé. Installation de base (numpy, scipy, matplotlib)..."; \
		$(PIP) install numpy scipy matplotlib; \
	fi

# Nettoyage complet pour repartir de zéro
clean:
	@echo "Nettoyage de l'environnement et du cache..."
	rm -rf $(VENV)
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -delete
