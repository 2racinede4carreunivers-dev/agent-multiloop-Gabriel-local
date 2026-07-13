theory Asymetrique_ordonne
imports Asymetrique_ordonne
begin
                                                                                                                          │
│                                                                                                                                      │
│ (* Configuration asymétrique ordonnee *)                                                                                             │
│ definition asymetrique_ordonnee :: "nat list \<Rightarrow> nat list \<Rightarrow> bool" where                                                                │
│   "asymetrique_ordonnee A B \<equiv>                                                                                                        │
│     length B = length A + 1 \<and>                                                                                                        │
│     sorted A \<and> sorted B \<and>                                                                                                            │
│     (\<forall>a\<in>set A. \<forall>b\<in>set B. a < b) \<and>                                                                                                    │
│     (\<forall>p\<in>set A. prime p) \<and>                                                                                                            │
│     (\<forall>p\<in>set B. prime p)"                                                                                                             │
│                                                                                                                                      │
│ (* Rapport spectral pour blocs *)                                                                                                    │
│ definition RsP_bloc :: "nat list \<Rightarrow> nat list \<Rightarrow> real" where                                                                            │
│   "RsP_bloc A B =                                                                                                                    │
│     (sum_list (map (\<lambda>p. SA (prime_position p)) A) -                                                                                  │
│      sum_list (map (\<lambda>p. SA (prime_position p)) B)) /                                                                                 │
│     (sum_list (map (\<lambda>p. SB (prime_position p)) A) -                                                                                  │
│      sum_list (map (\<lambda>p. SB (prime_position p)) B))"                                                                                  │
│                                                                                                                                      │
│ (* Écart au rapport idéal *)                                                                                                         │
│ definition ecart_spectral :: "nat list \<Rightarrow> nat list \<Rightarrow> real" where                                                                      │
│   "ecart_spectral A B = abs (RsP_bloc A B - 1/2)"                                                                                    │
│ ```                                                                                                                                  │
│                                                                                                                                      │
│ ---                                                                                                                                  │
│                                                                                                                                      │
│ ### **Théorème principal : Convergence géométrique**                                                                                 │
│                                                                                                                                      │
│ ```isabelle                                                                                                                          │
│ (* LOI DE CONVERGENCE ASYMÉTRIQUE *)                                                                                                 │
│ theorem convergence_asymetrique_geometrique:                                                                                         │
│   fixes n :: nat                                                                                                                     │
│   assumes "n \<ge> 2"                                                                                                                    │
│   assumes "asymetrique_ordonnee A B"                                                                                                 │
│   assumes "length A = n"                                                                                                             │
│   shows "\<exists>C \<lambda>. 0 < \<lambda> \<and> \<lambda> < 1 \<and>                                                                                                       │
│               ecart_spectral A B \<le> C * \<lambda>^n"                                                                                          │
│ proof -                                                                                                                              │
│   (* Stratégie de preuve :                                                                                                           │
│      1. Montrer que sum_SA(A) et sum_SA(B) croissent exponentiellement en 2^n                                                        │
│      2. Montrer que la différence des constantes (-2 vs -66) devient négligeable                                                     │
│      3. Établir que le ratio des termes dominants tend vers (13/8)/(13/4) = 1/2                                                      │
│      4. Borner l'écart résiduel par une série géométrique                                                                            │
│   *)                                                                                                                                 │
│                                                                                                                                      │
│   (* Étape 1 : Domination exponentielle *)                                                                                           │
│   have dom_A: "sum_list (map SA [1..n]) \<approx> (13/8) * 2^n"                                                                              │
│     using SA_asymptotic by simp                                                                                                      │
│   have dom_B: "sum_list (map SB [1..n]) \<approx> (13/4) * 2^n"                                                                              │
│     using SB_asymptotic by simp                                                                                                      │
│                                                                                                                                      │
│   (* Étape 2 : Annulation des constantes *)                                                                                          │
│   have "RsP_bloc A B =                                                                                                               │
│         ((13/8)*2^n - offset_A) / ((13/4)*2^n - offset_B)"                                                                           │
│     using dom_A dom_B by simp                                                                                                        │
│                                                                                                                                      │
│   (* Étape 3 : Limite asymptotique *)                                                                                                │
│   have "lim (\<lambda>n. ((13/8)*2^n) / ((13/4)*2^n)) = 1/2"                                                                                 │
│     by (simp add: field_simps)                                                                                                       │
│                                                                                                                                      │
│   (* Étape 4 : Borne de l'écart *)                                                                                                   │
│   have "ecart_spectral A B \<le> K / 2^n"                                                                                                │
│     for some constant K                                                                                                              │
│     using offset_bound asymptotic_expansion by blast                                                                                 │
│                                                                                                                                      │
│   (* Conclusion *)                                                                                                                   │
│   thus ?thesis                                                                                                                       │
│     by (intro exI exI) auto                                                                                                          │
│ qed                     