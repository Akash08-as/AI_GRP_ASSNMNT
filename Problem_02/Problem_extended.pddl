;; ======================================================================
;; Problem_extended.pddl -- Task 5: extended scenario
;; Adds Rock6 (Soft, at SiteE) and Rock7 (Hard, at SiteF).
;; Dust storm closes the Base <-> SiteB route in both directions.
;; Goal: Rock1-Rock7 all at Base, both bays empty, rover at Base.
;; ======================================================================

(define (problem rover-sample-collection-extended)
  (:domain mars-rover)

  (:objects
    Base SiteA SiteB SiteC SiteD SiteE SiteF - location
    Curiosity - rover
    Drill1 - drill
    Rock1 Rock2 Rock3 Rock4 Rock5 Rock6 Rock7 - rock
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
    (rock-at Rock6 SiteE)   ; new
    (rock-at Rock7 SiteF)   ; new

    ;; --- rock hardness ---
    (soft Rock1)
    (soft Rock2)
    (hard Rock3)
    (soft Rock4)
    (hard Rock5)
    (soft Rock6)   ; new
    (hard Rock7)   ; new

    ;; --- storage bays start empty ---
    (bay-empty Bay1)
    (bay-empty Bay2)

    ;; --- connectivity: two-way routes ---
    ;; NOTE: Base <-> SiteB is REMOVED (dust storm closes it both directions)
    (connected Base SiteA) (connected SiteA Base)
    (connected SiteA SiteC) (connected SiteC SiteA)
    (connected SiteB SiteD) (connected SiteD SiteB)
    (connected SiteC SiteE) (connected SiteE SiteC)
    (connected SiteD SiteE) (connected SiteE SiteD)
    (connected SiteE SiteF) (connected SiteF SiteE)

    ;; --- connectivity: one-way route (steep downhill slope), unaffected ---
    (connected SiteC SiteD)
    ;; still no (connected SiteD SiteC)
  )

  (:goal (and
    (rock-at Rock1 Base)
    (rock-at Rock2 Base)
    (rock-at Rock3 Base)
    (rock-at Rock4 Base)
    (rock-at Rock5 Base)
    (rock-at Rock6 Base)
    (rock-at Rock7 Base)
    (bay-empty Bay1)
    (bay-empty Bay2)
    (at Curiosity Base)
  ))
)
