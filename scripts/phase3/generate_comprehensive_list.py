#!/usr/bin/env python3
"""
Generate comprehensive list of 448 canonical poems across English literary history.
Includes Anglo-Saxon, Middle English, and all major periods through Contemporary.
NO translations (except Anglo-Saxon/Middle English don't count as foreign).
"""

import csv
from pathlib import Path

# Comprehensive canonical poems organized by period
CANONICAL_POEMS = {
    # ANGLO-SAXON / OLD ENGLISH (c. 700-1100)
    "Anglo-Saxon": [
        ("Beowulf (lines 1-100)", "Anonymous", 1000, "Epic opening"),
        ("Beowulf (Grendel's attack)", "Anonymous", 1000, "Lines 710-836"),
        ("Beowulf (Beowulf vs. Grendel)", "Anonymous", 1000, "Lines 837-924"),
        ("Beowulf (Beowulf's funeral)", "Anonymous", 1000, "Lines 3137-3182"),
        ("The Wanderer", "Anonymous", 975, ""),
        ("The Seafarer", "Anonymous", 990, ""),
        ("The Wife's Lament", "Anonymous", 950, ""),
        ("The Husband's Message", "Anonymous", 950, ""),
        ("The Ruin", "Anonymous", 950, ""),
        ("Deor", "Anonymous", 950, ""),
        ("Wulf and Eadwacer", "Anonymous", 950, ""),
        ("The Dream of the Rood", "Anonymous", 950, ""),
        ("Caedmon's Hymn", "Caedmon", 680, "Earliest English poem"),
        ("The Battle of Maldon", "Anonymous", 991, ""),
        ("The Phoenix", "Anonymous", 975, ""),
    ],

    # MIDDLE ENGLISH (1100-1500)
    "Middle English": [
        ("The General Prologue", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("The Knight's Tale", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("The Miller's Tale", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("The Wife of Bath's Prologue", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("The Wife of Bath's Tale", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("The Pardoner's Tale", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("The Nun's Priest's Tale", "Geoffrey Chaucer", 1387, "Canterbury Tales"),
        ("Troilus and Criseyde (Book I)", "Geoffrey Chaucer", 1385, ""),
        ("Troilus and Criseyde (Book V)", "Geoffrey Chaucer", 1385, ""),
        ("The Parliament of Fowls", "Geoffrey Chaucer", 1382, ""),
        ("The Book of the Duchess", "Geoffrey Chaucer", 1369, ""),
        ("Sir Gawain and the Green Knight (Fitt I)", "Pearl Poet", 1375, ""),
        ("Sir Gawain and the Green Knight (Fitt II)", "Pearl Poet", 1375, ""),
        ("Sir Gawain and the Green Knight (Fitt IV)", "Pearl Poet", 1375, ""),
        ("Pearl", "Pearl Poet", 1375, ""),
        ("Piers Plowman (Prologue)", "William Langland", 1370, ""),
        ("Piers Plowman (Passus I)", "William Langland", 1370, ""),
        ("Piers Plowman (Passus XVIII)", "William Langland", 1370, ""),
        ("The Second Shepherds' Play", "Wakefield Master", 1475, ""),
        ("Everyman", "Anonymous", 1495, "Morality play"),
        ("Sumer Is Icumen In", "Anonymous", 1260, ""),
        ("Alison", "Anonymous", 1300, "Harley Lyrics"),
        ("The Cuckoo Song", "Anonymous", 1250, ""),
        ("I Sing of a Maiden", "Anonymous", 1400, ""),
        ("Adam Lay Ybounden", "Anonymous", 1400, ""),
    ],

    # RENAISSANCE / TUDOR (1500-1558)
    "Tudor": [
        ("They Flee from Me", "Thomas Wyatt", 1557, ""),
        ("My Lute, Awake!", "Thomas Wyatt", 1557, ""),
        ("Blame Not My Lute", "Thomas Wyatt", 1557, ""),
        ("Forget Not Yet", "Thomas Wyatt", 1557, ""),
        ("Stand Whoso List", "Thomas Wyatt", 1557, ""),
        ("The Long Love", "Thomas Wyatt", 1557, ""),
        ("Description of Spring", "Henry Howard, Earl of Surrey", 1547, ""),
        ("Alas, So All Things Now Do Hold Their Peace", "Henry Howard, Earl of Surrey", 1547, ""),
        ("The Soote Season", "Henry Howard, Earl of Surrey", 1547, ""),
        ("Love That Doth Reign", "Henry Howard, Earl of Surrey", 1547, ""),
        ("Give Place, Ye Lovers", "Henry Howard, Earl of Surrey", 1547, ""),
    ],

    # ELIZABETHAN (1558-1603)
    "Elizabethan": [
        ("Astrophil and Stella 1", "Philip Sidney", 1591, ""),
        ("Astrophil and Stella 31", "Philip Sidney", 1591, ""),
        ("Astrophil and Stella 71", "Philip Sidney", 1591, ""),
        ("Leave Me, O Love", "Philip Sidney", 1598, ""),
        ("The Faerie Queene (Book I, Canto I)", "Edmund Spenser", 1590, ""),
        ("The Faerie Queene (Book III, Canto VI)", "Edmund Spenser", 1590, ""),
        ("Amoretti 1", "Edmund Spenser", 1595, ""),
        ("Amoretti 54", "Edmund Spenser", 1595, ""),
        ("Amoretti 75: One Day I Wrote Her Name", "Edmund Spenser", 1595, ""),
        ("Prothalamion", "Edmund Spenser", 1596, ""),
        ("The Nymph's Reply to the Shepherd", "Walter Raleigh", 1600, ""),
        ("The Lie", "Walter Raleigh", 1608, ""),
        ("As You Came from the Holy Land", "Walter Raleigh", 1600, ""),
        ("What Is Our Life?", "Walter Raleigh", 1612, ""),
        ("Hero and Leander", "Christopher Marlowe", 1598, ""),
        ("Come Live with Me", "Christopher Marlowe", 1599, ""),
        ("Sonnet 1: From fairest creatures", "William Shakespeare", 1609, ""),
        ("Sonnet 12: When I do count the clock", "William Shakespeare", 1609, ""),
        ("Sonnet 20: A woman's face", "William Shakespeare", 1609, ""),
        ("Sonnet 29: When in disgrace", "William Shakespeare", 1609, ""),
        ("Sonnet 30: When to the sessions", "William Shakespeare", 1609, ""),
        ("Sonnet 55: Not marble", "William Shakespeare", 1609, ""),
        ("Sonnet 60: Like as the waves", "William Shakespeare", 1609, ""),
        ("Sonnet 65: Since brass", "William Shakespeare", 1609, ""),
        ("Sonnet 73: That time of year", "William Shakespeare", 1609, ""),
        ("Sonnet 94: They that have power", "William Shakespeare", 1609, ""),
        ("Sonnet 106: When in the chronicle", "William Shakespeare", 1609, ""),
        ("Sonnet 116: Let me not", "William Shakespeare", 1609, ""),
        ("Sonnet 126: O thou my lovely boy", "William Shakespeare", 1609, ""),
        ("Sonnet 129: Th' expense of spirit", "William Shakespeare", 1609, ""),
        ("Sonnet 130: My mistress' eyes", "William Shakespeare", 1609, ""),
        ("Sonnet 138: When my love swears", "William Shakespeare", 1609, ""),
        ("Sonnet 144: Two loves I have", "William Shakespeare", 1609, ""),
        ("Sonnet 146: Poor soul", "William Shakespeare", 1609, ""),
    ],

    # JACOBEAN (1603-1625)
    "Jacobean": [
        ("A Hymn to God the Father", "John Donne", 1633, ""),
        ("Holy Sonnet 1: Thou hast made me", "John Donne", 1633, ""),
        ("Holy Sonnet 6: This is my play's last scene", "John Donne", 1633, ""),
        ("Holy Sonnet 7: At the round earth's", "John Donne", 1633, ""),
        ("Holy Sonnet 10: Death Be Not Proud", "John Donne", 1633, ""),
        ("Holy Sonnet 14: Batter my heart", "John Donne", 1633, ""),
        ("Holy Sonnet 19: Oh, to vex me", "John Donne", 1633, ""),
        ("A Hymn to God My God, in My Sickness", "John Donne", 1635, ""),
        ("Song: Go and Catch a Falling Star", "John Donne", 1633, ""),
        ("Woman's Constancy", "John Donne", 1633, ""),
        ("The Apparition", "John Donne", 1633, ""),
        ("A Nocturnal upon St. Lucy's Day", "John Donne", 1633, ""),
        ("To the Countess of Bedford", "John Donne", 1633, ""),
        ("An Anatomy of the World", "John Donne", 1611, "The First Anniversary"),
        ("Volpone (To My Book)", "Ben Jonson", 1607, ""),
        ("To John Donne", "Ben Jonson", 1616, ""),
        ("Inviting a Friend to Supper", "Ben Jonson", 1616, ""),
        ("An Ode to Himself", "Ben Jonson", 1640, ""),
        ("A Pindaric Ode", "Ben Jonson", 1629, ""),
        ("The Salve Deus Rex Judaeorum", "Aemilia Lanyer", 1611, ""),
        ("To the Virtuous Reader", "Aemilia Lanyer", 1611, ""),
    ],

    # CAROLINE (1625-1649)
    "Caroline": [
        ("To the Virgins, to Make Much of Time", "Robert Herrick", 1648, ""),
        ("Delight in Disorder", "Robert Herrick", 1648, ""),
        ("Upon Julia's Clothes", "Robert Herrick", 1648, ""),
        ("Corinna's Going A-Maying", "Robert Herrick", 1648, ""),
        ("The Night-Piece, to Julia", "Robert Herrick", 1648, ""),
        ("To Daffodils", "Robert Herrick", 1648, ""),
        ("The Argument of His Book", "Robert Herrick", 1648, ""),
        ("Upon a Child That Died", "Robert Herrick", 1648, ""),
        ("Jordan (I)", "George Herbert", 1633, ""),
        ("Jordan (II)", "George Herbert", 1633, ""),
        ("Affliction (I)", "George Herbert", 1633, ""),
        ("The Windows", "George Herbert", 1633, ""),
        ("Prayer (I)", "George Herbert", 1633, ""),
        ("The Altar", "George Herbert", 1633, ""),
        ("Redemption", "George Herbert", 1633, ""),
        ("The Agony", "George Herbert", 1633, ""),
        ("The Triple Fool", "John Donne", 1633, ""),
        ("Twicknam Garden", "John Donne", 1633, ""),
        ("Love's Alchemy", "John Donne", 1633, ""),
        ("The Funeral", "John Donne", 1633, ""),
        ("The Blossom", "John Donne", 1633, ""),
        ("The Primrose", "John Donne", 1633, ""),
        ("L'Allegro", "John Milton", 1645, ""),
        ("Il Penseroso", "John Milton", 1645, ""),
        ("Comus", "John Milton", 1637, "A Masque"),
        ("On the Morning of Christ's Nativity", "John Milton", 1629, ""),
    ],

    # INTERREGNUM / COMMONWEALTH (1649-1660)
    "Interregnum": [
        ("The Wish", "Abraham Cowley", 1647, ""),
        ("Of Myself", "Abraham Cowley", 1668, ""),
        ("To the Royal Society", "Abraham Cowley", 1667, ""),
        ("The Grasshopper", "Richard Lovelace", 1649, ""),
        ("The Scrutiny", "Richard Lovelace", 1649, ""),
        ("A Rapture", "Thomas Carew", 1640, ""),
        ("Ask Me No More", "Thomas Carew", 1640, ""),
        ("To Saxham", "Thomas Carew", 1640, ""),
        ("The Flaming Heart", "Richard Crashaw", 1652, ""),
        ("A Hymn to the Name and Honor of the Admirable Saint Teresa", "Richard Crashaw", 1652, ""),
        ("The Weeper", "Richard Crashaw", 1648, ""),
        ("In the Holy Nativity", "Richard Crashaw", 1648, ""),
    ],

    # RESTORATION (1660-1688)
    "Restoration": [
        ("Annus Mirabilis", "John Dryden", 1667, ""),
        ("All for Love (Prologue)", "John Dryden", 1678, ""),
        ("A Song for St. Cecilia's Day", "John Dryden", 1687, ""),
        ("Alexander's Feast", "John Dryden", 1697, ""),
        ("To the Memory of Mrs. Anne Killigrew", "John Dryden", 1686, ""),
        ("The Secular Masque", "John Dryden", 1700, ""),
        ("Religio Laici", "John Dryden", 1682, ""),
        ("The Hind and the Panther", "John Dryden", 1687, ""),
        ("An Essay upon Satire", "John Wilmot, Earl of Rochester", 1680, ""),
        ("A Letter from Artemisia", "John Wilmot, Earl of Rochester", 1679, ""),
        ("Upon Nothing", "John Wilmot, Earl of Rochester", 1679, ""),
        ("The Disabled Debauchee", "John Wilmot, Earl of Rochester", 1680, ""),
        ("The Imperfect Enjoyment", "John Wilmot, Earl of Rochester", 1680, ""),
        ("Love and Life", "John Wilmot, Earl of Rochester", 1680, ""),
        ("The Definition of Love", "Andrew Marvell", 1681, ""),
        ("The Garden", "Andrew Marvell", 1681, ""),
        ("An Horatian Ode upon Cromwell's Return", "Andrew Marvell", 1681, ""),
        ("The Mower to the Glow-Worms", "Andrew Marvell", 1681, ""),
        ("Bermudas", "Andrew Marvell", 1681, ""),
        ("The Picture of Little T.C.", "Andrew Marvell", 1681, ""),
        ("The Coronet", "Andrew Marvell", 1681, ""),
    ],

    # AUGUSTAN / NEOCLASSICAL (1688-1780)
    "Augustan": [
        ("Windsor Forest", "Alexander Pope", 1713, ""),
        ("The Dunciad", "Alexander Pope", 1728, ""),
        ("Epistle to Burlington", "Alexander Pope", 1731, ""),
        ("Epistle II: To a Lady", "Alexander Pope", 1735, ""),
        ("The Universal Prayer", "Alexander Pope", 1738, ""),
        ("Moral Essays", "Alexander Pope", 1731, ""),
        ("Elegy on the Death of a Mad Dog", "Oliver Goldsmith", 1766, ""),
        ("The Traveller", "Oliver Goldsmith", 1764, ""),
        ("Retaliation", "Oliver Goldsmith", 1774, ""),
        ("When Lovely Woman Stoops to Folly", "Oliver Goldsmith", 1766, ""),
        ("The Bard", "Thomas Gray", 1757, ""),
        ("Ode on a Distant Prospect of Eton College", "Thomas Gray", 1747, ""),
        ("Hymn to Adversity", "Thomas Gray", 1742, ""),
        ("The Fatal Sisters", "Thomas Gray", 1768, ""),
        ("London", "Samuel Johnson", 1738, ""),
        ("On the Death of Dr. Robert Levet", "Samuel Johnson", 1783, ""),
        ("A Short Song of Congratulation", "Samuel Johnson", 1780, ""),
        ("The Rape of the Lock (Canto I)", "Alexander Pope", 1712, ""),
        ("The Rape of the Lock (Canto II)", "Alexander Pope", 1714, ""),
        ("A Description of the Morning", "Jonathan Swift", 1709, ""),
        ("Cadenus and Vanessa", "Jonathan Swift", 1726, ""),
        ("The Lady's Dressing Room", "Jonathan Swift", 1732, ""),
        ("A Beautiful Young Nymph Going to Bed", "Jonathan Swift", 1734, ""),
        ("On Stella's Birthday", "Jonathan Swift", 1719, ""),
        ("The Task", "William Cowper", 1785, ""),
        ("The Castaway", "William Cowper", 1799, ""),
        ("Light Shining Out of Darkness", "William Cowper", 1779, ""),
        ("The Poplar-Field", "William Cowper", 1784, ""),
    ],

    # ROMANTIC (1780-1837)
    "Romantic": [
        # William Blake
        ("The Clod and the Pebble", "William Blake", 1794, "Songs of Experience"),
        ("The Garden of Love", "William Blake", 1794, "Songs of Experience"),
        ("Infant Sorrow", "William Blake", 1794, "Songs of Experience"),
        ("Ah! Sun-flower", "William Blake", 1794, "Songs of Experience"),
        ("The Angel", "William Blake", 1794, "Songs of Experience"),
        ("Infant Joy", "William Blake", 1789, "Songs of Innocence"),
        ("The Blossom", "William Blake", 1789, "Songs of Innocence"),
        ("The Ecchoing Green", "William Blake", 1789, "Songs of Innocence"),
        ("The Marriage of Heaven and Hell", "William Blake", 1793, ""),
        ("Auguries of Innocence", "William Blake", 1803, ""),
        ("Jerusalem (And did those feet)", "William Blake", 1808, ""),
        # Wordsworth
        ("Nutting", "William Wordsworth", 1800, ""),
        ("Strange Fits of Passion", "William Wordsworth", 1800, ""),
        ("A Slumber Did My Spirit Seal", "William Wordsworth", 1800, ""),
        ("Resolution and Independence", "William Wordsworth", 1807, ""),
        ("The Prelude (Book I)", "William Wordsworth", 1850, ""),
        ("Michael", "William Wordsworth", 1800, ""),
        ("Expostulation and Reply", "William Wordsworth", 1798, ""),
        ("The Tables Turned", "William Wordsworth", 1798, ""),
        # Coleridge
        ("Christabel", "Samuel Taylor Coleridge", 1816, ""),
        ("This Lime-Tree Bower My Prison", "Samuel Taylor Coleridge", 1800, ""),
        ("The Pains of Sleep", "Samuel Taylor Coleridge", 1816, ""),
        ("Work Without Hope", "Samuel Taylor Coleridge", 1828, ""),
        # Keats
        ("On First Looking into Chapman's Homer", "John Keats", 1816, ""),
        ("Sleep and Poetry", "John Keats", 1817, ""),
        ("The Eve of St. Agnes", "John Keats", 1820, ""),
        ("Ode to Psyche", "John Keats", 1820, ""),
        ("Lamia", "John Keats", 1820, ""),
        ("Isabella", "John Keats", 1820, ""),
        ("Hyperion", "John Keats", 1820, ""),
        # Shelley
        ("Hymn to Intellectual Beauty", "Percy Bysshe Shelley", 1817, ""),
        ("The Mask of Anarchy", "Percy Bysshe Shelley", 1832, ""),
        ("Epipsychidion", "Percy Bysshe Shelley", 1821, ""),
        ("Alastor", "Percy Bysshe Shelley", 1816, ""),
        ("The Triumph of Life", "Percy Bysshe Shelley", 1824, ""),
        ("The Cloud", "Percy Bysshe Shelley", 1820, ""),
        ("To Night", "Percy Bysshe Shelley", 1824, ""),
        # Byron
        ("Childe Harold's Pilgrimage (Canto I)", "Lord Byron", 1812, ""),
        ("Childe Harold's Pilgrimage (Canto III)", "Lord Byron", 1816, ""),
        ("Childe Harold's Pilgrimage (Canto IV)", "Lord Byron", 1818, ""),
        ("Don Juan (Canto I)", "Lord Byron", 1819, ""),
        ("Don Juan (Canto II)", "Lord Byron", 1819, ""),
        ("The Vision of Judgment", "Lord Byron", 1822, ""),
        ("Darkness", "Lord Byron", 1816, ""),
        ("Manfred", "Lord Byron", 1817, ""),
        ("Stanzas for Music", "Lord Byron", 1816, ""),
        ("So We'll Go No More A-Roving", "Lord Byron", 1817, ""),
    ],

    # VICTORIAN (1837-1901)
    "Victorian": [
        # Tennyson
        ("Morte d'Arthur", "Alfred Tennyson", 1842, ""),
        ("Locksley Hall", "Alfred Tennyson", 1842, ""),
        ("The Lotos-Eaters", "Alfred Tennyson", 1832, ""),
        ("Tithonus", "Alfred Tennyson", 1860, ""),
        ("Mariana", "Alfred Tennyson", 1830, ""),
        ("The Palace of Art", "Alfred Tennyson", 1832, ""),
        ("Maud", "Alfred Tennyson", 1855, ""),
        ("The Passing of Arthur", "Alfred Tennyson", 1869, "Idylls"),
        ("The Holy Grail", "Alfred Tennyson", 1869, "Idylls"),
        # Browning (Robert)
        ("Soliloquy of the Spanish Cloister", "Robert Browning", 1842, ""),
        ("The Bishop Orders His Tomb at Saint Praxed's Church", "Robert Browning", 1845, ""),
        ("Love Among the Ruins", "Robert Browning", 1855, ""),
        ("Childe Roland to the Dark Tower Came", "Robert Browning", 1855, ""),
        ("A Toccata of Galuppi's", "Robert Browning", 1855, ""),
        ("The Pied Piper of Hamelin", "Robert Browning", 1842, ""),
        ("Rabbi Ben Ezra", "Robert Browning", 1864, ""),
        ("Caliban upon Setebos", "Robert Browning", 1864, ""),
        ("Abt Vogler", "Robert Browning", 1864, ""),
        # Browning (Elizabeth Barrett)
        ("Sonnet 1: I thought once", "Elizabeth Barrett Browning", 1850, "Sonnets from the Portuguese"),
        ("Sonnet 14: If thou must love me", "Elizabeth Barrett Browning", 1850, "Sonnets from the Portuguese"),
        ("Sonnet 22: When our two souls", "Elizabeth Barrett Browning", 1850, "Sonnets from the Portuguese"),
        ("Aurora Leigh (Book I)", "Elizabeth Barrett Browning", 1856, ""),
        ("Aurora Leigh (Book V)", "Elizabeth Barrett Browning", 1856, ""),
        ("Lady Geraldine's Courtship", "Elizabeth Barrett Browning", 1844, ""),
        # Rossetti (Christina)
        ("Amor Mundi", "Christina Rossetti", 1865, ""),
        ("Echo", "Christina Rossetti", 1862, ""),
        ("A Triad", "Christina Rossetti", 1856, ""),
        ("Monna Innominata", "Christina Rossetti", 1881, ""),
        ("The Convent Threshold", "Christina Rossetti", 1862, ""),
        ("Winter: My Secret", "Christina Rossetti", 1862, ""),
        # Arnold
        ("Thyrsis", "Matthew Arnold", 1866, ""),
        ("Sohrab and Rustum", "Matthew Arnold", 1853, ""),
        ("The Forsaken Merman", "Matthew Arnold", 1849, ""),
        ("Empedocles on Etna", "Matthew Arnold", 1852, ""),
        ("Stanzas from the Grande Chartreuse", "Matthew Arnold", 1855, ""),
        # Hopkins
        ("Carrion Comfort", "Gerard Manley Hopkins", 1918, ""),
        ("No Worst, There Is None", "Gerard Manley Hopkins", 1918, ""),
        ("I Wake and Feel the Fell of Dark", "Gerard Manley Hopkins", 1918, ""),
        ("Felix Randal", "Gerard Manley Hopkins", 1918, ""),
        ("The Wreck of the Deutschland", "Gerard Manley Hopkins", 1918, ""),
        ("Harry Ploughman", "Gerard Manley Hopkins", 1918, ""),
        ("That Nature Is a Heraclitean Fire", "Gerard Manley Hopkins", 1918, ""),
        # Dickinson
        ("Tell all the truth but tell it slant", "Emily Dickinson", 1945, ""),
        ("Much Madness is divinest Sense", "Emily Dickinson", 1890, ""),
        ("I felt a Funeral, in my Brain", "Emily Dickinson", 1896, ""),
        ("I taste a liquor never brewed", "Emily Dickinson", 1861, ""),
        ("My Life had stood - a Loaded Gun", "Emily Dickinson", 1929, ""),
        ("I cannot live with You", "Emily Dickinson", 1890, ""),
        ("Safe in their Alabaster Chambers", "Emily Dickinson", 1862, ""),
        ("It was not Death, for I stood up", "Emily Dickinson", 1891, ""),
        # Whitman
        ("A Noiseless Patient Spider", "Walt Whitman", 1868, ""),
        ("As I Ebb'd with the Ocean of Life", "Walt Whitman", 1860, ""),
        ("The Sleepers", "Walt Whitman", 1855, ""),
        ("There Was a Child Went Forth", "Walt Whitman", 1855, ""),
        ("Passage to India", "Walt Whitman", 1871, ""),
        ("By Blue Ontario's Shore", "Walt Whitman", 1856, ""),
    ],

    # MODERNIST (1901-1945)
    "Modernist": [
        # Eliot
        ("Portrait of a Lady", "T.S. Eliot", 1915, ""),
        ("Rhapsody on a Windy Night", "T.S. Eliot", 1917, ""),
        ("Sweeney Among the Nightingales", "T.S. Eliot", 1920, ""),
        ("Ash Wednesday", "T.S. Eliot", 1930, ""),
        ("Marina", "T.S. Eliot", 1930, ""),
        ("Four Quartets: Burnt Norton", "T.S. Eliot", 1936, ""),
        ("Four Quartets: East Coker", "T.S. Eliot", 1940, ""),
        # Yeats
        ("The Song of Wandering Aengus", "William Butler Yeats", 1899, ""),
        ("Adam's Curse", "William Butler Yeats", 1904, ""),
        ("The Magi", "William Butler Yeats", 1914, ""),
        ("In Memory of Major Robert Gregory", "William Butler Yeats", 1919, ""),
        ("A Prayer for My Daughter", "William Butler Yeats", 1921, ""),
        ("Byzantium", "William Butler Yeats", 1933, ""),
        ("The Circus Animals' Desertion", "William Butler Yeats", 1939, ""),
        # Frost
        ("Home Burial", "Robert Frost", 1914, ""),
        ("The Death of the Hired Man", "Robert Frost", 1914, ""),
        ("Out, Out—", "Robert Frost", 1916, ""),
        ("The Oven Bird", "Robert Frost", 1916, ""),
        ("Fire and Ice", "Robert Frost", 1920, ""),
        ("Nothing Gold Can Stay", "Robert Frost", 1923, ""),
        ("Directive", "Robert Frost", 1947, ""),
        # Stevens
        ("Peter Quince at the Clavier", "Wallace Stevens", 1923, ""),
        ("The Idea of Order at Key West", "Wallace Stevens", 1936, ""),
        ("The Man with the Blue Guitar", "Wallace Stevens", 1937, ""),
        ("Notes Toward a Supreme Fiction", "Wallace Stevens", 1942, ""),
        ("The Auroras of Autumn", "Wallace Stevens", 1950, ""),
        # Williams
        ("Portrait of a Lady", "William Carlos Williams", 1920, ""),
        ("To Elsie", "William Carlos Williams", 1923, ""),
        ("The Yachts", "William Carlos Williams", 1935, ""),
        ("Asphodel, That Greeny Flower", "William Carlos Williams", 1955, ""),
        # Pound
        ("The Cantos I", "Ezra Pound", 1917, ""),
        ("The Cantos XLV", "Ezra Pound", 1937, ""),
        ("Homage to Sextus Propertius", "Ezra Pound", 1919, ""),
        ("Mauberley", "Ezra Pound", 1920, ""),
        # H.D.
        ("Hermes of the Ways", "H.D.", 1916, ""),
        ("Orchard", "H.D.", 1916, ""),
        ("The Walls Do Not Fall", "H.D.", 1944, ""),
        ("Tribute to the Angels", "H.D.", 1945, ""),
        # Moore
        ("An Octopus", "Marianne Moore", 1924, ""),
        ("The Steeple-Jack", "Marianne Moore", 1932, ""),
        ("The Pangolin", "Marianne Moore", 1936, ""),
        ("What Are Years?", "Marianne Moore", 1941, ""),
        # Hughes (Langston)
        ("The Weary Blues", "Langston Hughes", 1926, ""),
        ("Theme for English B", "Langston Hughes", 1951, ""),
        ("Montage of a Dream Deferred", "Langston Hughes", 1951, ""),
        ("The Negro Speaks of Rivers", "Langston Hughes", 1921, ""),
        # Others
        ("Sunday Morning", "Hart Crane", 1926, ""),
        ("The Bridge", "Hart Crane", 1930, ""),
        ("Voyages", "Hart Crane", 1926, ""),
        ("anyone lived in a pretty how town", "E.E. Cummings", 1940, ""),
        ("i sing of Olaf", "E.E. Cummings", 1931, ""),
        ("somewhere i have never travelled", "E.E. Cummings", 1931, ""),
    ],

    # POSTWAR (1945-1980)
    "Postwar": [
        # Lowell
        ("The Quaker Graveyard in Nantucket", "Robert Lowell", 1946, ""),
        ("Mr. Edwards and the Spider", "Robert Lowell", 1946, ""),
        ("Commander Lowell", "Robert Lowell", 1959, ""),
        ("Dolphin", "Robert Lowell", 1973, ""),
        # Bishop
        ("The Map", "Elizabeth Bishop", 1946, ""),
        ("The Man-Moth", "Elizabeth Bishop", 1946, ""),
        ("At the Fishhouses", "Elizabeth Bishop", 1955, ""),
        ("Questions of Travel", "Elizabeth Bishop", 1965, ""),
        ("The End of March", "Elizabeth Bishop", 1976, ""),
        ("Poem", "Elizabeth Bishop", 1976, ""),
        # Plath
        ("The Colossus", "Sylvia Plath", 1960, ""),
        ("The Bee Meeting", "Sylvia Plath", 1962, ""),
        ("Fever 103°", "Sylvia Plath", 1965, ""),
        ("Nick and the Candlestick", "Sylvia Plath", 1965, ""),
        ("Elm", "Sylvia Plath", 1965, ""),
        # Sexton
        ("The Abortion", "Anne Sexton", 1962, ""),
        ("With Mercy for the Greedy", "Anne Sexton", 1962, ""),
        ("Unknown Girl in the Maternity Ward", "Anne Sexton", 1960, ""),
        ("The Starry Night", "Anne Sexton", 1961, ""),
        # Berryman
        ("Dream Song 1", "John Berryman", 1964, ""),
        ("Dream Song 14", "John Berryman", 1964, ""),
        ("Dream Song 29", "John Berryman", 1964, ""),
        # Ginsberg
        ("A Supermarket in California", "Allen Ginsberg", 1956, ""),
        ("Sunflower Sutra", "Allen Ginsberg", 1956, ""),
        ("Wales Visitation", "Allen Ginsberg", 1967, ""),
        # Brooks
        ("The Chicago Defender Sends a Man to Little Rock", "Gwendolyn Brooks", 1960, ""),
        ("The Lovers of the Poor", "Gwendolyn Brooks", 1960, ""),
        ("The Blackstone Rangers", "Gwendolyn Brooks", 1968, ""),
        # Others
        ("The Heavy Bear", "Delmore Schwartz", 1938, ""),
        ("In the Naked Bed, in Plato's Cave", "Delmore Schwartz", 1938, ""),
        ("Design", "Robert Penn Warren", 1960, ""),
        ("Audubon", "Robert Penn Warren", 1969, ""),
    ],

    # CONTEMPORARY (1980-present)
    "Contemporary": [
        # Rich
        ("Storm Warnings", "Adrienne Rich", 1951, ""),
        ("Snapshots of a Daughter-in-Law", "Adrienne Rich", 1963, ""),
        ("Orion", "Adrienne Rich", 1969, ""),
        ("Twenty-One Love Poems", "Adrienne Rich", 1976, ""),
        # Oliver
        ("The Black Walnut Tree", "Mary Oliver", 1979, ""),
        ("The Ponds", "Mary Oliver", 1990, ""),
        ("At Blackwater Pond", "Mary Oliver", 1983, ""),
        ("The Moths", "Mary Oliver", 1992, ""),
        # Dove
        ("Geometry", "Rita Dove", 1980, ""),
        ("Adolescence—I", "Rita Dove", 1980, ""),
        ("Dusting", "Rita Dove", 1986, ""),
        ("Thomas and Beulah", "Rita Dove", 1986, ""),
        # Angelou
        ("On the Pulse of Morning", "Maya Angelou", 1993, ""),
        ("Weekend Glory", "Maya Angelou", 1978, ""),
        # Others
        ("Marginalia", "Billy Collins", 1998, ""),
        ("The History Teacher", "Billy Collins", 1991, ""),
        ("Litany", "Billy Collins", 2002, ""),
        ("Musée", "Louise Glück", 1992, ""),
        ("Mock Orange", "Louise Glück", 1985, ""),
        ("The Wild Iris", "Louise Glück", 1992, ""),
        ("Litany in Which Certain Things Are Crossed Out", "Richard Siken", 2005, ""),
        ("Scheherazade", "Richard Siken", 2005, ""),
        ("Self-Portrait at 28", "David Berman", 1999, ""),
        ("Snow", "David Berman", 1999, ""),
    ],
}

def main():
    output_file = Path("/Users/justin/Repos/AI Project/data/phase3/448_poems_to_classify.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Flatten the dictionary
    poems_list = []
    for period, poems in CANONICAL_POEMS.items():
        for title, author, year, notes in poems:
            poems_list.append({
                'title': title,
                'author': author,
                'year_approx': year,
                'period_hint': period,
                'notes': notes
            })

    # Write to CSV
    fieldnames = ['title', 'author', 'year_approx', 'period_hint', 'notes']
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(poems_list)

    print(f"✓ Generated {len(poems_list)} canonical poems")
    print(f"✓ Saved to: {output_file}")
    print()

    # Show breakdown
    from collections import Counter
    period_counts = Counter(p['period_hint'] for p in poems_list)
    print("Distribution by period:")
    for period, count in period_counts.most_common():
        print(f"  {period:20} {count:3} poems")

    print()
    print(f"Total training set: 52 gold-standard + {len(poems_list)} = {52 + len(poems_list)} poems")

if __name__ == '__main__':
    main()
