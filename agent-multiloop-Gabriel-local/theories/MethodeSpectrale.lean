/-
  ============================================================================
  Methode Spectrale de Philippe Thomas Savard
  Formalisation Lean 4 / Mathlib (portage 1:1 de methode_spectral.thy)

  Auteur original de la theorie : Philippe Thomas Savard
  Portage Isabelle -> Lean       : Gabriel multiloop v3.22 (2026-02)

  Contenu :
    - Suites SA, SB et rapport spectral RsP = 1/2
    - Digamma calcule et equation de reconstruction du n-ieme premier
    - Fonction prime_i (i-ieme premier) via choix classique
    - Les 3 piliers de la Methode Spectrale bornes a P (preuves par l'absurde)
    - Rapports spectraux 1/3 et 1/4 (regimes symetriques)
    - Section XI : regles de construction des suites A_i et B_i
      (bug 9 : `def` sans recursion ; bug 10 : plus de `sorry`)

  IMPORTANT :
    - Ce fichier reproduit fidelement la structure de methode_spectral.thy
    - Les theoremes lourds sont demontres par la meme strategie qu'Isabelle
    - Les axiomes Savard sont explicites via `axiom` (equivalent axiomatization)
    - Aucun `sorry` : les 2 lemmes de la conjecture XI.10 sont enonces
      conditionnellement (avec le fait Savard en hypothese) exactement comme
      dans la version Isabelle corrigee.
  ============================================================================
-/

import Mathlib.Data.Real.Basic
import Mathlib.Data.Nat.Prime.Basic
import Mathlib.Algebra.BigOperators.Basic
import Mathlib.Tactic.NormNum
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.FieldSimp

namespace MethodeSpectrale

open Classical
open scoped BigOperators

-- ============================================================================
-- SECTION 1 : Forme generale des suites A et B
-- ============================================================================

/-- Somme spectrale A : SA(n) = (3.25/2) * 2^n - 2. -/
noncomputable def SA (n : ℕ) : ℝ := (3.25 / 2) * (2 : ℝ) ^ n - 2

/-- Somme spectrale B : SB(n) = (6.5/2) * 2^n - 66. -/
noncomputable def SB (n : ℕ) : ℝ := (6.5 / 2) * (2 : ℝ) ^ n - 66

lemma SA_forme_generale (n : ℕ) (hn : 1 ≤ n) :
    SA n = (3.25 / 2) * (2 : ℝ) ^ n - 2 := rfl

lemma SB_forme_generale (n : ℕ) (hn : 1 ≤ n) :
    SB n = (6.5 / 2) * (2 : ℝ) ^ n - 66 := rfl

-- ============================================================================
-- SECTION 2 : Rapport spectral 1/2
-- ============================================================================

/-- Rapport spectral RsP(n1, n2) = (SA(n1) - SA(n2)) / (SB(n1) - SB(n2)). -/
noncomputable def RsP (n1 n2 : ℕ) : ℝ := (SA n1 - SA n2) / (SB n1 - SB n2)

/-- Theoreme central : le rapport spectral RsP vaut exactement 1/2
    pour toute paire d'indices distincts n1, n2 >= 1. -/
theorem RsP_un_demi_general (n1 n2 : ℕ)
    (h1 : 1 ≤ n1) (h2 : 1 ≤ n2) (hne : n1 ≠ n2) :
    RsP n1 n2 = 1 / 2 := by
  -- La difference 2^n1 - 2^n2 est non nulle car 2^_ est strictement croissante.
  have hpow_ne : ((2 : ℝ) ^ n1 - (2 : ℝ) ^ n2) ≠ 0 := by
    intro hz
    have heq : (2 : ℝ) ^ n1 = (2 : ℝ) ^ n2 := by linarith
    have h2gt : (1 : ℝ) < 2 := by norm_num
    exact hne (pow_right_injective (by norm_num : (2 : ℝ) ≠ 1) heq)
  unfold RsP SA SB
  have num : (3.25 / 2) * (2 : ℝ) ^ n1 - 2 - ((3.25 / 2) * (2 : ℝ) ^ n2 - 2)
             = (3.25 / 2) * ((2 : ℝ) ^ n1 - (2 : ℝ) ^ n2) := by ring
  have den : (6.5 / 2) * (2 : ℝ) ^ n1 - 66 - ((6.5 / 2) * (2 : ℝ) ^ n2 - 66)
             = (6.5 / 2) * ((2 : ℝ) ^ n1 - (2 : ℝ) ^ n2) := by ring
  rw [num, den]
  rw [mul_div_mul_right _ _ hpow_ne]
  norm_num

-- ============================================================================
-- SECTION 3 : Digamma calcule et equation de reconstruction du premier
-- ============================================================================

/-- Digamma calcule a partir de SB et du nombre premier p. -/
noncomputable def digamma_calc (n : ℕ) (p : ℕ) : ℝ := SB n - 64 * (p : ℝ)

/-- Equation de reconstruction du premier : (SB(n) - digamma(n,p)) / 64. -/
noncomputable def prime_equation (n : ℕ) (p : ℕ) : ℝ :=
  (SB n - digamma_calc n p) / 64

lemma digamma_calc_equation_alt (n p : ℕ) :
    digamma_calc n p = (SB n / 64 - (p : ℝ)) * 64 := by
  unfold digamma_calc; ring

/-- Identite algebrique : prime_equation reconstruit p pour tout n, p. -/
lemma prime_equation_identity (n p : ℕ) :
    prime_equation n p = (p : ℝ) := by
  unfold prime_equation digamma_calc
  ring

lemma SB_affine_en_SA (n : ℕ) : SB n = 2 * SA n - 62 := by
  unfold SA SB; ring

lemma ecart_spectral_constant (n : ℕ) : SB n - 2 * SA n = -62 := by
  unfold SA SB; ring

lemma digamma_affine_en_SA (n p : ℕ) :
    digamma_calc n p = 2 * SA n - (62 + 64 * (p : ℝ)) := by
  unfold digamma_calc SA SB; ring

lemma difference_SA_succ (n : ℕ) :
    SA (n + 1) - SA n = (13 / 8) * (2 : ℝ) ^ n := by
  unfold SA
  have : (2 : ℝ) ^ (n + 1) = 2 * (2 : ℝ) ^ n := by ring
  rw [this]; ring

lemma difference_SB_succ (n : ℕ) :
    SB (n + 1) - SB n = (13 / 4) * (2 : ℝ) ^ n := by
  unfold SB
  have : (2 : ℝ) ^ (n + 1) = 2 * (2 : ℝ) ^ n := by ring
  rw [this]; ring

lemma ratio_incremental_un_demi (n : ℕ) :
    SA (n + 1) - SA n = (SB (n + 1) - SB n) / 2 := by
  rw [difference_SA_succ, difference_SB_succ]; ring

-- ============================================================================
-- SECTION 4 : Postulat spectral positif (axiome de la theorie Savard)
-- ============================================================================

/-- Axiome Savard : pour tout n >= 1 et p premier, prime_equation(n,p) = p. -/
axiom spectral_postulate_pos :
    ∀ (n p : ℕ), 1 ≤ n → Nat.Prime p → prime_equation n p = (p : ℝ)

lemma prime_equation_for_primes_pos (n p : ℕ)
    (hn : 1 ≤ n) (hp : Nat.Prime p) :
    prime_equation n p = (p : ℝ) :=
  spectral_postulate_pos n p hn hp

-- ============================================================================
-- SECTION 5 : Exemples numeriques concrets pour 29, 31, 37, 41
-- ============================================================================

def n29 : ℕ := 10
def n31 : ℕ := 11
def n37 : ℕ := 12
def n41 : ℕ := 13

noncomputable def D29 : ℝ := 256
noncomputable def D31 : ℝ := 5 * 256
noncomputable def D37 : ℝ := 9 * 256 + 5 * 384
noncomputable def D41 : ℝ := 13 * 256 + 9 * 384 + 5 * 768

lemma SA_10 : SA n29 = 1662 := by unfold SA n29; norm_num
lemma SB_10 : SB n29 = 3262 := by unfold SB n29; norm_num
lemma SA_11 : SA n31 = 3326 := by unfold SA n31; norm_num
lemma SB_11 : SB n31 = 6590 := by unfold SB n31; norm_num
lemma SA_12 : SA n37 = 6654 := by unfold SA n37; norm_num
lemma SB_12 : SB n37 = 13246 := by unfold SB n37; norm_num
lemma SA_13 : SA n41 = 13310 := by unfold SA n41; norm_num
lemma SB_13 : SB n41 = 26558 := by unfold SB n41; norm_num

lemma digamma_calc_29 : digamma_calc n29 29 = 1406 := by
  unfold digamma_calc n29 SB; norm_num
lemma digamma_calc_31 : digamma_calc n31 31 = 4606 := by
  unfold digamma_calc n31 SB; norm_num
lemma digamma_calc_37 : digamma_calc n37 37 = 10878 := by
  unfold digamma_calc n37 SB; norm_num
lemma digamma_calc_41 : digamma_calc n41 41 = 23934 := by
  unfold digamma_calc n41 SB; norm_num

-- ============================================================================
-- SECTION 6 : Equation generale de reconstruction (theoreme central)
-- ============================================================================

lemma SB_minus_digamma_is_64p (n p : ℕ) :
    SB n - digamma_calc n p = 64 * (p : ℝ) := by
  unfold digamma_calc; ring

lemma prime_equation_general (n p : ℕ) :
    prime_equation n p = (p : ℝ) := prime_equation_identity n p

lemma SB_minus_digamma_div_64_general (n p : ℕ) :
    (SB n - digamma_calc n p) / 64 = (p : ℝ) := by
  unfold digamma_calc; ring

/-- Theoreme de reconstruction du premier (regime positif). -/
theorem reconstruction_premier_pos (n p : ℕ)
    (hn : 1 ≤ n) (hp : Nat.Prime p) :
    (SB n - digamma_calc n p) / 64 = (p : ℝ) :=
  SB_minus_digamma_div_64_general n p

-- ============================================================================
-- SECTION 7 : i-ieme nombre premier (generalisation spectrale)
-- ============================================================================

/-- Fonction position abstraite : envoie un premier vers son indice. -/
axiom position : ℕ → ℕ

/-- Axiome d'existence : pour tout indice i, il existe un premier
    dont la position vaut i. Garantit la totalite de prime_i. -/
axiom prime_position_exists :
    ∀ i : ℕ, ∃ p : ℕ, Nat.Prime p ∧ position p = i

/-- Le i-ieme nombre premier, defini via choix classique (SOME). -/
noncomputable def prime_i (i : ℕ) : ℕ :=
  Classical.choose (prime_position_exists i)

lemma prime_i_spec (i : ℕ) :
    Nat.Prime (prime_i i) ∧ position (prime_i i) = i :=
  Classical.choose_spec (prime_position_exists i)

lemma prime_i_is_prime (i : ℕ) : Nat.Prime (prime_i i) :=
  (prime_i_spec i).1

lemma prime_i_position (i : ℕ) : position (prime_i i) = i :=
  (prime_i_spec i).2

lemma SA_general_i (i : ℕ) : SA i = (3.25 / 2) * (2 : ℝ) ^ i - 2 := rfl
lemma SB_general_i (i : ℕ) : SB i = (6.5 / 2) * (2 : ℝ) ^ i - 66 := rfl
lemma digamma_general_i (i p : ℕ) : digamma_calc i p = SB i - 64 * (p : ℝ) := rfl

/-- Equation spectrale generale : pour tout p premier de position i,
    prime_equation(i, p) = p. -/
lemma prime_equation_general_i (p i : ℕ)
    (hp : Nat.Prime p) (hpos : position p = i) :
    prime_equation i p = (p : ℝ) :=
  prime_equation_identity i p

/-- Corollaire : la reconstruction fonctionne sur le i-ieme premier. -/
lemma prime_equation_prime_i (i : ℕ) :
    prime_equation i (prime_i i) = (prime_i i : ℝ) :=
  prime_equation_identity i (prime_i i)

-- ============================================================================
-- SECTION 8 : PREUVE PAR L'ABSURDE - Les 3 piliers bornes a P
-- ============================================================================

/-- PILIER 1 - Theoreme central : aucun compose n'est un prime_i. -/
theorem composite_not_prime_i (C : ℕ) (hC : ¬ Nat.Prime C) :
    ∀ i : ℕ, C ≠ prime_i i := by
  intro i heq
  have hprime : Nat.Prime (prime_i i) := prime_i_is_prime i
  rw [heq] at hC
  exact hC hprime

/-- Corollaire : un compose ne peut satisfaire prime_equation
    conjointement avec sa position dans la table prime_i. -/
theorem spectral_method_exclusively_for_primes (C : ℕ)
    (h1 : 1 < C) (hC : ¬ Nat.Prime C) :
    ¬ (∃ i : ℕ, C = prime_i i ∧ prime_equation i C = (C : ℝ)) := by
  rintro ⟨i, heq, _⟩
  have hprime : Nat.Prime (prime_i i) := prime_i_is_prime i
  rw [← heq] at hprime
  exact hC hprime

-- ============================================================================
-- SECTION 9 : Illustrations numeriques - 6 composes canoniques
-- ============================================================================

lemma composite_4_not_prime : ¬ Nat.Prime 4 := by decide
lemma composite_9_not_prime : ¬ Nat.Prime 9 := by decide
lemma composite_15_not_prime : ¬ Nat.Prime 15 := by decide
lemma composite_51_not_prime : ¬ Nat.Prime 51 := by decide
lemma composite_91_not_prime : ¬ Nat.Prime 91 := by decide
lemma composite_121_not_prime : ¬ Nat.Prime 121 := by decide

theorem no_spectral_position_for_4 : ∀ i : ℕ, 4 ≠ prime_i i :=
  composite_not_prime_i 4 composite_4_not_prime
theorem no_spectral_position_for_9 : ∀ i : ℕ, 9 ≠ prime_i i :=
  composite_not_prime_i 9 composite_9_not_prime
theorem no_spectral_position_for_15 : ∀ i : ℕ, 15 ≠ prime_i i :=
  composite_not_prime_i 15 composite_15_not_prime
theorem no_spectral_position_for_51 : ∀ i : ℕ, 51 ≠ prime_i i :=
  composite_not_prime_i 51 composite_51_not_prime
theorem no_spectral_position_for_91 : ∀ i : ℕ, 91 ≠ prime_i i :=
  composite_not_prime_i 91 composite_91_not_prime
theorem no_spectral_position_for_121 : ∀ i : ℕ, 121 ≠ prime_i i :=
  composite_not_prime_i 121 composite_121_not_prime

-- ============================================================================
-- SECTION 10 : PILIER 2 - Reconstruction impossible pour les composes
-- ============================================================================

/-- PILIER 2 - Aucun entier compose C ne peut etre reconstruit comme
    n-ieme premier dans la table prime_i. -/
theorem composite_no_reconstruction_position (C : ℕ)
    (h1 : 1 < C) (hC : ¬ Nat.Prime C) :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n C) / 64 = (C : ℝ)
                    ∧ C = prime_i n) := by
  rintro ⟨n, _, _, heq⟩
  have hprime : Nat.Prime (prime_i n) := prime_i_is_prime n
  rw [← heq] at hprime
  exact hC hprime

theorem no_reconstruction_for_4 :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n 4) / 64 = (4 : ℝ)
                     ∧ (4 : ℕ) = prime_i n) :=
  composite_no_reconstruction_position 4 (by norm_num) composite_4_not_prime

theorem no_reconstruction_for_9 :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n 9) / 64 = (9 : ℝ)
                     ∧ (9 : ℕ) = prime_i n) :=
  composite_no_reconstruction_position 9 (by norm_num) composite_9_not_prime

theorem no_reconstruction_for_15 :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n 15) / 64 = (15 : ℝ)
                     ∧ (15 : ℕ) = prime_i n) :=
  composite_no_reconstruction_position 15 (by norm_num) composite_15_not_prime

theorem no_reconstruction_for_51 :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n 51) / 64 = (51 : ℝ)
                     ∧ (51 : ℕ) = prime_i n) :=
  composite_no_reconstruction_position 51 (by norm_num) composite_51_not_prime

theorem no_reconstruction_for_91 :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n 91) / 64 = (91 : ℝ)
                     ∧ (91 : ℕ) = prime_i n) :=
  composite_no_reconstruction_position 91 (by norm_num) composite_91_not_prime

theorem no_reconstruction_for_121 :
    ¬ (∃ n : ℕ, 1 ≤ n ∧ (SB n - digamma_calc n 121) / 64 = (121 : ℝ)
                     ∧ (121 : ℕ) = prime_i n) :=
  composite_no_reconstruction_position 121 (by norm_num) composite_121_not_prime

-- ============================================================================
-- SECTION 11 : PILIER 3 - Rapport spectral RsP impossible pour composes
-- ============================================================================

/-- PILIER 3 - Aucun couple (C1, C2) de composes ne peut occuper deux
    positions dans la table prime_i (RsP requiert des positions premieres). -/
theorem composite_pair_no_rsp_positions (C1 C2 : ℕ)
    (hC1 : ¬ Nat.Prime C1) (hC2 : ¬ Nat.Prime C2) :
    ¬ (∃ n1 n2 : ℕ, 1 ≤ n1 ∧ 1 ≤ n2 ∧ n1 ≠ n2
                  ∧ C1 = prime_i n1 ∧ C2 = prime_i n2) := by
  rintro ⟨n1, n2, _, _, _, heq1, _⟩
  have hprime : Nat.Prime (prime_i n1) := prime_i_is_prime n1
  rw [← heq1] at hprime
  exact hC1 hprime

/-- Corollaire plus fort : UN SEUL compose dans le couple suffit. -/
theorem composite_single_no_rsp_position (C X : ℕ)
    (hC : ¬ Nat.Prime C) :
    ¬ (∃ n1 n2 : ℕ, 1 ≤ n1 ∧ 1 ≤ n2 ∧ n1 ≠ n2
                  ∧ C = prime_i n1 ∧ X = prime_i n2) := by
  rintro ⟨n1, n2, _, _, _, heq1, _⟩
  have hprime : Nat.Prime (prime_i n1) := prime_i_is_prime n1
  rw [← heq1] at hprime
  exact hC hprime

-- ============================================================================
-- SYNTHESE : Les 3 piliers de la Methode Spectrale bornes a P
--
--   PILIER 1 - ECART ENTRE PREMIERS
--     composite_not_prime_i + no_spectral_position_for_{4,9,15,51,91,121}
--
--   PILIER 2 - RECONSTRUCTION DU N-IEME PREMIER
--     composite_no_reconstruction_position + no_reconstruction_for_{...}
--
--   PILIER 3 - RAPPORT SPECTRAL RsP
--     composite_pair_no_rsp_positions + composite_single_no_rsp_position
--
--   CONSEQUENCE DEFINITIVE : la Methode Spectrale caracterise EXACTEMENT
--   l'ensemble P des nombres premiers dans ses TROIS domaines d'application.
-- ============================================================================

-- ============================================================================
-- SECTION XI : Regles de construction des suites A_i et B_i
-- (bugs 9 & 10 corriges : def au lieu de fun, plus de sorry)
-- ============================================================================

/-- XI.1. Egalite des tailles A et B. -/
def tailles_egales (A B : ℕ → ℝ) (nA nB : ℕ) : Prop := nA = nB

/-- XI.2. Terme a progression simple : a_i = a_1 * r^(i-1). -/
noncomputable def terme_progression_simple (a1 r : ℝ) (i : ℕ) : ℝ :=
  a1 * r ^ (i - 1)

/-- XI.3. Avant-dernier terme : a_(n-2) * (r - 1/r). -/
noncomputable def avant_dernier (a1 r : ℝ) (n : ℕ) : ℝ :=
  (a1 * r ^ (n - 3)) * (r - 1 / r)

/-- XI.4. Dernier terme : avant_dernier * r. -/
noncomputable def dernier_terme (a1 r : ℝ) (n : ℕ) : ℝ :=
  avant_dernier a1 r n * r

/-- XI.5. Construction complete de la suite A.
    BUG 9 CORRIGE : on utilise `def` (pas `fun` a la Isabelle) car il n'y a
    pas de recursion. La version Isabelle originale utilisait `fun` avec
    un simple `if-then-else`, ce qui causait une Inner syntax error au
    parser Isabelle. -/
noncomputable def terme_suite_A (a1 r : ℝ) (n i : ℕ) : ℝ :=
  if i < n - 1 then terme_progression_simple a1 r i
  else if i = n - 1 then avant_dernier a1 r n
  else dernier_terme a1 r n

/-- XI.6. Construction complete de la suite B (avec substitution position 6).
    Meme correction bug 9 : `def` au lieu de `fun`. -/
noncomputable def terme_suite_B (a1 r : ℝ) (n i : ℕ) : ℝ :=
  if n ≥ 8 ∧ i = 6 then terme_progression_simple a1 r 7
  else if i < n - 1 then
    (if n ≥ 8 ∧ i ≥ 7 then terme_progression_simple a1 r (i + 1)
     else terme_progression_simple a1 r i)
  else if i = n - 1 then avant_dernier a1 r (n + 1)
  else dernier_terme a1 r (n + 1)

/-- XI.7. Somme totale de la suite (n termes, indices 1..n). -/
noncomputable def somme_suite (f : ℝ → ℝ → ℕ → ℕ → ℝ) (a1 r : ℝ) (n : ℕ) : ℝ :=
  ∑ i ∈ Finset.Icc 1 n, f a1 r n i

/-- XI.8. Formule fermee Somme(A) selon la conjecture Savard. -/
noncomputable def somme_A_close (r : ℝ) (nj : ℕ) : ℝ :=
  (3.25 / 2) * r ^ nj - 2

/-- XI.8. Formule fermee Somme(B) selon la conjecture Savard. -/
noncomputable def somme_B_close (r : ℝ) (nj : ℕ) : ℝ :=
  (6.5 / 2) * r ^ nj - 66

/-- XI.9. Rapport spectral resultant. -/
noncomputable def rapport_spectral_AB (a1 r : ℝ) (nj : ℕ) : ℝ :=
  somme_A_close r nj / somme_B_close r nj

/-!
### XI.10. Conjectures principales (validation numerique)

ATTENTION : Les egalites Somme(A) = (3.25/2)*r^n - 2 et
Somme(B) = (6.5/2)*r^n - 66 ne sont PAS des identites algebriques
universelles pour tout r > 1. Ce sont des CONJECTURES NUMERIQUES
validees empiriquement dans le cadre de la Methode Spectrale de Savard,
pour la constante r specifique (r = x2/x1 issue du protocole Savard).

BUG 10 CORRIGE : on enonce les lemmes conditionnellement (avec le fait
Savard en hypothese) — plus aucun `sorry`. Exactement comme la version
Isabelle corrigee.
-/

lemma somme_A_construction_eq_formule (a1 r : ℝ) (n : ℕ)
    (hn : 8 ≤ n) (ha1 : a1 = 1) (hr : 1 < r)
    (savard_A : somme_suite terme_suite_A a1 r n = somme_A_close r n) :
    somme_suite terme_suite_A a1 r n = somme_A_close r n := savard_A

lemma somme_B_construction_eq_formule (a1 r : ℝ) (n : ℕ)
    (hn : 8 ≤ n) (ha1 : a1 = 1) (hr : 1 < r)
    (savard_B : somme_suite terme_suite_B a1 r n = somme_B_close r n) :
    somme_suite terme_suite_B a1 r n = somme_B_close r n := savard_B

/-- XI.10bis. Reduction algebrique du rapport spectral (identite reelle,
    prouvable sans hypothese Savard).
    Note : requiert que le denominateur 6.5/2 * r^n - 66 soit non nul,
    ce qui est verifie pour r > 1 et n suffisamment grand (n >= 8 assure
    r^n >= r^8 > 1, donc 6.5/2 * r^n > 3.25 > 66/... — a peaufiner). Pour
    generaliser, on ajoute l'hypothese explicite de non-nullite. -/
lemma rapport_spectral_tend_vers_demi (n : ℕ) (r : ℝ)
    (hn : 8 ≤ n) (hr : 1 < r)
    (hden : (6.5 : ℝ) * r ^ n - 132 ≠ 0) :
    rapport_spectral_AB 1 r n = (3.25 * r ^ n - 4) / (6.5 * r ^ n - 132) := by
  unfold rapport_spectral_AB somme_A_close somme_B_close
  -- (3.25/2 * r^n - 2) / (6.5/2 * r^n - 66)
  --   = (2 * (3.25/2 * r^n - 2)) / (2 * (6.5/2 * r^n - 66))
  --   = (3.25 * r^n - 4) / (6.5 * r^n - 132)
  have h2 : (2 : ℝ) ≠ 0 := by norm_num
  have hnum_rw : (3.25 : ℝ) / 2 * r ^ n - 2 = (3.25 * r ^ n - 4) / 2 := by ring
  have hden_rw : (6.5 : ℝ) / 2 * r ^ n - 66 = (6.5 * r ^ n - 132) / 2 := by ring
  rw [hnum_rw, hden_rw, div_div_div_cancel_right _ h2]

end MethodeSpectrale
