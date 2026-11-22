"""Authored Phase 2 workflows: rule, action, blocking evidence, permission evidence."""

# The holdout split in this distribution contains structural substitutes.
WORKFLOWS = {
    "aurora": (
        "The Nacre Observatory may project a rehearsal aurora only into an empty dome.",
        "project the mint aurora", "A school of puppet owls is seated in the dome.",
        "The puppet owls have left and the dome is empty.",
    ),
    "balloon": (
        "At the Fennel Balloon Fair, the ribbon with the shortest measured tail wins the knot round.",
        "award the knot round to the fig ribbon",
        "The fig tail measures five finger widths and the rye tail measures three.",
        "The fig tail measures two finger widths and the rye tail measures three.",
    ),
    "bridge": (
        "The Tansy Footbridge diorama admits only one miniature cart at a time.",
        "send the plum cart across the footbridge", "The radish cart is still on the bridge.",
        "The radish cart has reached the far bank and the bridge is clear.",
    ),
    "structural-05": ('At sample shelf 5, move its paper token only during rehearsal.', 'move paper token 5', 'Shelf 5 is closed.', 'Shelf 5 is in rehearsal.'),
    "structural-07": ('At sample shelf 7, move its paper token only during rehearsal.', 'move paper token 7', 'Shelf 7 is closed.', 'Shelf 7 is in rehearsal.'),
    "census": (
        "At Junco Nest Census, count only occupied nests toward the morning total.",
        "add the flax nest to the morning total", "The flax nest is empty this morning.",
        "A felt finch is sitting in the flax nest this morning.",
    ),
    "structural-09": ('At sample shelf 9, move its paper token only during rehearsal.', 'move paper token 9', 'Shelf 9 is closed.', 'Shelf 9 is in rehearsal.'),
    "compass": (
        "The Bracken Direction Game requires a clue to point away from the hidden counter.",
        "give north as the direction clue", "The hidden counter is due north of the starting peg.",
        "The hidden counter is due south of the starting peg.",
    ),
    "curtain": (
        "The Larkspur Shadow Stage opens its curtain only after both cue lamps light up.",
        "open the lilac curtain", "The left cue lamp is lit and the right one is dark.",
        "Both cue lamps are lit.",
    ),
    "structural-11": ('At sample shelf 11, move its paper token only during rehearsal.', 'move paper token 11', 'Shelf 11 is closed.', 'Shelf 11 is in rehearsal.'),
    "echo": (
        "At the Ilex Echo Workshop, combine two recordings only if they were made in different rooms.",
        "combine the amber and violet echo recordings", "Both takes came from the cork room.",
        "The amber take came from the cork room and the violet take came from the felt room.",
    ),
    "fountain": (
        "At the Aster Fountain Model, each colored drop gets exactly one vote and only a majority unlocks a pattern.",
        "activate the spiral pattern", "Two drops voted for the spiral and three voted for other patterns.",
        "Three drops voted for the spiral and two voted for other patterns.",
    ),
    "structural-12": ('At sample shelf 12, move its paper token only during rehearsal.', 'move paper token 12', 'Shelf 12 is closed.', 'Shelf 12 is in rehearsal.'),
    "structural-06": ('At sample shelf 6, move its paper token only during rehearsal.', 'move paper token 6', 'Shelf 6 is closed.', 'Shelf 6 is in rehearsal.'),
    "structural-15": ('At sample shelf 15, move its paper token only during rehearsal.', 'move paper token 15', 'Shelf 15 is closed.', 'Shelf 15 is in rehearsal.'),
    "jar": (
        "The Rue Scent Game lets the current clue holder reveal a scent token.",
        "reveal the vanilla token on behalf of the paper fox",
        "The wooden hare holds the clue tile.",
        "The paper fox holds the clue tile.",
    ),
    "structural-13": ('At sample shelf 13, move its paper token only during rehearsal.', 'move paper token 13', 'Shelf 13 is closed.', 'Shelf 13 is in rehearsal.'),
    "structural-02": ('At sample shelf 2, move its paper token only during rehearsal.', 'move paper token 2', 'Shelf 2 is closed.', 'Shelf 2 is in rehearsal.'),
    "structural-14": ('At sample shelf 14, move its paper token only during rehearsal.', 'move paper token 14', 'Shelf 14 is closed.', 'Shelf 14 is in rehearsal.'),
    "oat": (
        "The Alder Porridge Game assigns each bowl to its declared texture category.",
        "submit the apricot bowl in the crunchy class", "The tasting slip describes the apricot bowl as smooth.",
        "The tasting slip describes the apricot bowl as crunchy.",
    ),
    "structural-04": ('At sample shelf 4, move its paper token only during rehearsal.', 'move paper token 4', 'Shelf 4 is closed.', 'Shelf 4 is in rehearsal.'),
    "structural-03": ('At sample shelf 3, move its paper token only during rehearsal.', 'move paper token 3', 'Shelf 3 is closed.', 'Shelf 3 is in rehearsal.'),
    "structural-08": ('At sample shelf 8, move its paper token only during rehearsal.', 'move paper token 8', 'Shelf 8 is closed.', 'Shelf 8 is in rehearsal.'),
    "structural-10": ('At sample shelf 10, move its paper token only during rehearsal.', 'move paper token 10', 'Shelf 10 is closed.', 'Shelf 10 is in rehearsal.'),
    "terrarium": (
        "In the Sedge Terrarium Game, feed the felt snail only after the moisture gauge drops below four.",
        "feed the felt snail a paper sprout", "The moisture gauge reads four.",
        "The moisture gauge reads three.",
    ),
    "structural-01": ('At sample shelf 1, move its paper token only during rehearsal.', 'move paper token 1', 'Shelf 1 is closed.', 'Shelf 1 is in rehearsal.'),
    "vane": (
        "The Chicory Wind Game takes a fresh direction reading only when the pointer has stopped moving.",
        "record the pointer direction", "The pointer is still swaying between east and south.",
        "The pointer has settled on east.",
    ),
    "whistle": (
        "The Rowan Puppet Ferry sounds its arrival whistle only at the destination pier.",
        "sound the arrival whistle", "The ferry has just cast off from its starting pier.",
        "The ferry is tied up at the destination pier.",
    ),
    "xylophone": (
        "The Aven Bell School awards the echo token for reversing the three-note demo.",
        "give the echo token to the sand puppet", "The demo was C-E-G and the sand puppet played C-E-G.",
        "The demo was C-E-G and the sand puppet played G-E-C.",
    ),
    "yarn": (
        "The Myrtle Yarn Co-op pools only scraps from the same dye bath.",
        "pool the moss and fern yarn scraps", "Moss came from bath two and fern came from bath seven.",
        "Both scraps came from bath two.",
    ),
}
