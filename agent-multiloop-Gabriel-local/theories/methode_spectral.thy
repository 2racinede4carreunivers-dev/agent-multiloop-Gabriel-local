theory methode_spectral
  imports Complex_Main
begin
(****************************************************************)
(* TABLE DES MATIERES - SCRIPT HOL : GEOMETRIE DU SPECTRE       *)
(*                                                              *)
(* I.   RAPPORT SPECTRAL 1/2 - FONDATIONS                       *)
(* II.  MODELE SPECTRAL 1/4                                     *)
(* III. MODELE SPECTRAL 1/3                                     *)
(* IV.  RAPPORT SPECTRAL 1/4 - PREUVE GENERALE                  *)
(* V.   SUITES MIXTES A ET B (-,+)                              *)
(* VI.  SUITES NEGATIVES - EQUATIONS SPECTRALES                 *)
(* VII. GEOMETRIE SPECTRALE - ASYMETRIE ORDONNEE / CHAOTIQUE    *)
(* VIII. METHODE DE COMPARAISON ASYMETRIQUE                     *)
(* IX.  AXIOMATISATIONS SPECTRALES - SECTIONS OFFICIELLES       *)
(* X.   VALIDATION EPIPOLAIRE DU PLAN TRIFOCAL                  *)
(****************************************************************)

section "Forme generale des suites A et B"

definition SA :: "nat => real" where
  "SA n = (3.25 / 2) * (2 ^ n) - 2"

definition SB :: "nat => real" where
  "SB n = (6.5 / 2) * (2 ^ n) - 66"

lemma SA_forme_generale:
  assumes "n >= 1"
  shows "SA n = (3.25 / 2) * (2 ^ n) - 2"
  using assms by (simp add: SA_def)

lemma SB_forme_generale:
  assumes "n >= 1"
  shows "SB n = (6.5 / 2) * (2 ^ n) - 66"
  using assms by (simp add: SB_def)

section "Rapport spectral 1/2"

definition RsP :: "nat => nat => real" where
  "RsP n1 n2 = (SA n1 - SA n2) / (SB n1 - SB n2)"

lemma RsP_un_demi_general:
  assumes "n1 >= 1" "n2 >= 1" "n1 ~= n2"
  shows "RsP n1 n2 = 1/2"
  sorry

section "Section du Digamma calcule."

definition digamma_calc :: "nat => nat => real" where
  "digamma_calc n p = SB n - 64 * real p"

definition prime_equation :: "nat => nat => real" where
  "prime_equation n p = (SB n - digamma_calc n p) / 64"

lemma prime_equation_identity:
  "prime_equation n p = real p"
  unfolding prime_equation_def digamma_calc_def
  by simp

section "Axiomatisation positive"

axiomatization where
  spectral_postulate_pos:
    "!!n p. n >= 1 ==> prime p ==> prime_equation n p = real p"

(* NOTE: Fichier complet de Philippe Thomas Savard - Methode Spectrale
   Contient les modeles 1/2, 1/3, 1/4 (positifs et negatifs),
   suites mixtes, geometrie spectrale, plan trifocal, lien avec Riemann.
   Voir le document complet dans le fichier original. *)

(* === MODELE 1/4 === *)

definition A_1_4 :: "nat => real" where
  "A_1_4 n = ((241 / 16) / 12) * (4 ^ n) - (4 / 3)"

definition B_1_4 :: "nat => real" where
  "B_1_4 n = ((964 / 16) / 12) * (4 ^ n) - (3073 * (4 / 3))"

axiomatization where
  spectral_postulate_1_4:
    "!!n p. n > 0 ==> prime p ==>
       (B_1_4 n - (B_1_4 n - 4096 * real p)) / 4096 = real p"

(* === MODELE 1/3 === *)

definition A_1_3 :: "nat => real" where
  "A_1_3 n = ((73 / 9) / 12) * (3 ^ n) - 1.5"

definition B_1_3 :: "nat => real" where
  "B_1_3 n = ((219 / 9) / 12) * (3 ^ n) - (487 * 1.5)"

axiomatization where
  spectral_postulate_1_3:
    "!!n p. n > 0 ==> prime p ==>
       (B_1_3 n - (B_1_3 n - 729 * real p)) / 729 = real p"

end
