;; ======================================================================
;; Problem.pddl -- base scenario (Rock1..Rock5)
;; ======================================================================

(define (problem rover-sample-collection)
  (:domain mars-rover)

  (:objects
    Base SiteA SiteB SiteC SiteD SiteE SiteF - location
    Curiosity - rover
    Drill1 - drill
    Rock1 Rock2 Rock3 Rock4 Rock5 - rock
    Bay1 Bay2 - bay
  )

  (:init
    ;; --- rover and equipment ---
    (at Curiosity Base)
    (drill-at Drill1 SiteE)

    ;; --- rock locations ---
    (rock-at Rock1 SiteA)
    (rock-at Rock2 SiteB)
    (rock-at Rock3 SiteC)
    (rock-at Rock4 SiteD)
    (rock-at Rock5 SiteF)

    ;; --- rock hardness ---
    (soft Rock1)
    (soft Rock2)
    (hard Rock3)
    (soft Rock4)
    (hard Rock5)

    ;; --- storage bays start empty ---
    (bay-empty Bay1)
    (bay-empty Bay2)

    ;; --- connectivity: two-way routes (both directions asserted) ---
    (connected Base SiteA) (connected SiteA Base)
    (connected Base SiteB) (connected SiteB Base)
    (connected SiteA SiteC) (connected SiteC SiteA)
    (connected SiteB SiteD) (connected SiteD SiteB)
    (connected SiteC SiteE) (connected SiteE SiteC)
    (connected SiteD SiteE) (connected SiteE SiteD)
    (connected SiteE SiteF) (connected SiteF SiteE)

    ;; --- connectivity: one-way route (steep downhill slope) ---
    (connected SiteC SiteD)
    ;; NOTE: no (connected SiteD SiteC) -- rover cannot go SiteD -> SiteC directly
  )

  (:goal (and
    (rock-at Rock1 Base)
    (rock-at Rock2 Base)
    (rock-at Rock3 Base)
    (rock-at Rock4 Base)
    (rock-at Rock5 Base)
    (bay-empty Bay1)
    (bay-empty Bay2)
    (at Curiosity Base)
  ))
)
