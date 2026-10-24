def afficher_resultat(produits, chemin_csv):
    print("{} produit(s) Asus V16 enregistré(s).".format(len(produits)))
    for produit in produits:
        print("- {} | {} | {}".format(produit.titre, produit.prix or "Prix indisponible", produit.asin))
    print("Export CSV : {}".format(chemin_csv))
