;; ======================================================================
;; Domain.pddl -- Mars Rover Sample Collection
;; Requirements: :strips and :typing only (no numeric fluents, no
;; :negative-preconditions). Because negative preconditions are not
;; allowed, "soft rock needs no drill" cannot be written as
;; (not (hard ?rk)). Instead we use TWO separate positive predicates,
;; (soft ?rk) and (hard ?rk), each rock has exactly one of them asserted
;; in the problem file, and there are two separate collect actions:
;; collect-soft (no drill needed) and collect-hard (drill needed).
;; ======================================================================

(define (domain mars-rover)
  (:requirements :strips :typing)

  (:types
    location
    rover
    drill
    rock
    bay
  )

  (:predicates
    (at ?r - rover ?l - location)                 ; rover r is at location l
    (rock-at ?rk - rock ?l - location)             ; rock rk is lying at location l
    (drill-at ?d - drill ?l - location)            ; drill d is lying at location l
    (connected ?l1 - location ?l2 - location)      ; rover can move l1 -> l2
    (soft ?rk - rock)                              ; rock rk is a soft rock
    (hard ?rk - rock)                              ; rock rk is a hard rock
    (has-drill ?r - rover ?d - drill)              ; rover r is carrying drill d
    (bay-empty ?b - bay)                           ; storage bay b is empty
    (in-bay ?rk - rock ?b - bay)                   ; rock rk is stored in bay b
  )

  ;; ---- Move between two connected locations ----
  (:action move
    :parameters (?r - rover ?from - location ?to - location)
    :precondition (and
      (at ?r ?from)
      (connected ?from ?to)
    )
    :effect (and
      (not (at ?r ?from))
      (at ?r ?to)
    )
  )

  ;; ---- Pick up the drill at the rover's current location ----
  ;; Once picked up the rover keeps the drill for the rest of the mission
  ;; (no action ever removes has-drill), matching the assignment text.
  (:action pick-drill
    :parameters (?r - rover ?d - drill ?l - location)
    :precondition (and
      (at ?r ?l)
      (drill-at ?d ?l)
    )
    :effect (and
      (not (drill-at ?d ?l))
      (has-drill ?r ?d)
    )
  )

  ;; ---- Collect a SOFT rock: no drill required ----
  (:action collect-soft
    :parameters (?r - rover ?rk - rock ?l - location ?b - bay)
    :precondition (and
      (at ?r ?l)
      (rock-at ?rk ?l)
      (soft ?rk)
      (bay-empty ?b)
    )
    :effect (and
      (not (rock-at ?rk ?l))
      (not (bay-empty ?b))
      (in-bay ?rk ?b)
    )
  )

  ;; ---- Collect a HARD rock: rover must be carrying a drill ----
  (:action collect-hard
    :parameters (?r - rover ?rk - rock ?l - location ?b - bay ?d - drill)
    :precondition (and
      (at ?r ?l)
      (rock-at ?rk ?l)
      (hard ?rk)
      (bay-empty ?b)
      (has-drill ?r ?d)
    )
    :effect (and
      (not (rock-at ?rk ?l))
      (not (bay-empty ?b))
      (in-bay ?rk ?b)
    )
  )

  ;; ---- Deposit a rock from a storage bay at the rover's current location ----
  (:action deposit
    :parameters (?r - rover ?rk - rock ?l - location ?b - bay)
    :precondition (and
      (at ?r ?l)
      (in-bay ?rk ?b)
    )
    :effect (and
      (not (in-bay ?rk ?b))
      (bay-empty ?b)
      (rock-at ?rk ?l)
    )
  )
)
