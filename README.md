# Algorand-Greenhouse-Hack-3

Pour utiliser un account avec la Sandbox (blockchain simulée):

- goal account list (liste les account de la sandbox : 3 par défaut)
- goal account export -a <adresse de l'account que vous voulez utiliser> (affiche le mnemonic qui permet de reconstruire la paire clé publique/privée avec le sdk)
- export MNEMONIC_ACCOUNT1 = <mnemonic affiché par cmd précédente> (permet d'avoir une variable d'environnement : pratique)
