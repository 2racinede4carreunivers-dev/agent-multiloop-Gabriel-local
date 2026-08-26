# Rapports non-typiques 1/k ≠ 1/2

Les rapports non-typiques 1/k sont définis pour toutes les valeurs 1/k < 1/2, par exemple :
1/3, 1/4, 1/5, 1/6, …, 1/k.

Contrairement au rapport typique 1/2, la valeur de n ne correspond pas à la position du
nombre premier. Pour les rapports non-typiques, n représente exclusivement la quantité
de termes dans les suites A et B.

## 1. Règle fondamentale : reconstruction initiale pour n = 10

Pour chaque rapport non-typique 1/k, la reconstruction du premier se fait toujours en
premier pour n = 10. Cette valeur sert d’ancre pour déterminer ensuite les premiers
pour n > 10 (ordre croissant) et n < 10 (ordre décroissant).

## 2. Méthode standard (entiers naturels)

Les suites A et B sont construites à l’aide des puissances entières t^i, où t est la base
du rapport (ex. t = 3 pour 1/3, t = 5 pour 1/5, etc.).

Exemple pour 1/3, n = 10 :

A = 3^1 + 3^2 + 3^4 + 3^5 + 3^6 + 3^7 + 3^8 + (3^9 - 3^7) + (3^10 - 3^8)
  = 79 824

B = 3^1 + 3^2 + 3^4 + 3^5 + 3^7 + 3^8 + 3^9 + (3^10 - 3^8) + (3^11 - 3^9)
  = 238 746

Le digamma est généralement la 8ᵉ position :
Digamma = 3^8
Digamma calculé = A - 3^8 = 73 263

Premier reconstruit :
P = (B - Digamma calculé) / 3^6 = 227

## 3. Variantes du digamma

Selon le rapport 1/k, le digamma peut être :
- la 8ᵉ position (souvent),
- la 7ᵉ position (ex. 1/5, 1/6),
- additionné ou soustrait à la somme A.

Exemple pour 1/5, n = 10 :
Digamma = +5^7
P = (B - (A + 5^7)) / 5^6 = 2999

Exemple pour 1/6, n = 10 :
Digamma = -6^7
P = (B - (A - 6^7)) / 6^6 = 7607

## 4. Méthode généralisée pour n ≠ 10

Pour n ≠ 10, le digamma calculé est donné par :

Digamma_calculé = (SB / t^6 - P) × t^6

où SB est la somme de la suite B pour le rapport et le n considérés.

## 5. Particularité du rapport 1/11

Pour le rapport non-typique 1/11, la méthode standard (entiers naturels) échoue :
aucune combinaison ±11^7 ou ±11^8 ne permet de reconstruire un nombre premier pour n = 10.

Cependant, une méthode alternative fondée sur les réels permet de reconstruire un premier.
Cette méthode utilise des distances géométriques :

((11^1)^2 + (11^1)^2)^(1/2)+
((11^1)^2 + (11^2)^2)^(1/2)
((11^2)^2 + (11^3)^2)^(1/2)
((11^3)^2 + (11^4)^2)^(1/2)
((11^4)^2 + (11^5)^2)^(1/2)
((11^5)^2 + (11^6)^2)^(1/2)
((11^6)^2 + (11^7)^2)^(1/2)
((11^7)^2 + (11^8)^2)^(1/2)
((11^8-11^6)^2+(11^9-9^7)^2)^(1/2)
((11^9-11^7)^2+(11^10-9^8)^2)^(1/2)

((11^1)^2 + (11^1)^2)^(1/2)+
((11^1)^2 + (11^2)^2)^(1/2)
((11^2)^2 + (11^3)^2)^(1/2)
((11^3)^2 + (11^4)^2)^(1/2)
((11^4)^2 + (11^5)^2)^(1/2)
((11^6)^2 + (11^7)^2)^(1/2)
((11^7)^2 + (11^8)^2)^(1/2)
((11^8)^2 + (11^9)^2)^(1/2)
((11^9-11^7)^2+(11^10-9^8)^2)^(1/2)
((11^10-11^8)^2+(11^11-11^9)^2)^(1/2)
...

Ainsi que des équations réelles du type :

A = (1251.993836 / 110) × 11^n - (√122)/10  
B = (13375.93219 / 110) × 11^n - 161052 × (√122)/10

Cette méthode produit un premier valide pour 1/11, n = 10 :
P = 1 611 851

## 6. Conséquence théorique

La présence d’un premier reconstruit via une méthode réelle pour 1/11 n = 10 soulève une
question profonde : contrairement à l’idée classique selon laquelle les expressions
(A^(1/2) - B^(1/2)) / C^(1/2) ne produisent pas de nombres premiers, ce rapport 1/11
montre qu’une structure réelle peut mener à une reconstruction valide.

Cette observation s’inscrit dans la méthode spectrale locale (methode_spectral.thy),
où les comparaisons asymétriques chaotiques et ordonnées divergent autour de -1/6 à 1.05
avant de se stabiliser rapidement autour de 1/2. Cela suggère que le rapport critique
n’est pas exclusivement 1/2 dans les comparaisons asymétriques, contrairement aux
comparaisons symétriques.

Cette nouvelle perspective renforce l’hypothèse de départ de Savard, selon laquelle
l’hypothèse de Riemann pourrait ne pas être valide, comme expliqué dans
SCRIPT_NARRATIF_VP.md et dans la présentation publiée sur YouTube.
