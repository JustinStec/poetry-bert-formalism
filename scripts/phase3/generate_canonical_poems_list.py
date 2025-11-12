#!/usr/bin/env python3
"""
Generate list of ~300 canonical poems for Phase 3 training dataset.
Based on the 52 gold-standard examples, expand to cover more canonical works.
"""

import csv
from pathlib import Path

# Canonical poems organized by period
# Format: (title, author, year_approx, notes)
CANONICAL_POEMS = {
    # RENAISSANCE/EARLY MODERN (1500-1660)
    "Renaissance": [
        ("Sonnet 29: When in disgrace with fortune and men's eyes", "William Shakespeare", 1609, ""),
        ("Sonnet 73: That time of year thou mayst in me behold", "William Shakespeare", 1609, ""),
        ("Sonnet 116: Let me not to the marriage of true minds", "William Shakespeare", 1609, ""),
        ("Sonnet 130: My mistress' eyes are nothing like the sun", "William Shakespeare", 1609, ""),
        ("The Flea", "John Donne", 1633, ""),
        ("A Valediction: Forbidding Mourning", "John Donne", 1633, ""),
        ("Death Be Not Proud", "John Donne", 1633, ""),
        ("Batter My Heart", "John Donne", 1633, ""),
        ("The Sun Rising", "John Donne", 1633, ""),
        ("The Canonization", "John Donne", 1633, ""),
        ("To Althea, From Prison", "Richard Lovelace", 1649, ""),
        ("To Lucasta, Going to the Wars", "Richard Lovelace", 1649, ""),
        ("When I Consider How My Light Is Spent", "John Milton", 1673, "On His Blindness"),
        ("Methought I Saw My Late Espoused Saint", "John Milton", 1673, ""),
        ("How Soon Hath Time", "John Milton", 1645, ""),
        ("On Shakespeare", "John Milton", 1632, ""),
        ("The Collar", "George Herbert", 1633, ""),
        ("The Pulley", "George Herbert", 1633, ""),
        ("Easter Wings", "George Herbert", 1633, ""),
        ("Virtue", "George Herbert", 1633, ""),
        ("Love (III)", "George Herbert", 1633, ""),
        ("The Retreat", "Henry Vaughan", 1650, ""),
        ("They Are All Gone into the World of Light", "Henry Vaughan", 1655, ""),
        ("The World", "Henry Vaughan", 1650, ""),
        ("Song: To Celia", "Ben Jonson", 1616, "Drink to Me Only"),
        ("On My First Son", "Ben Jonson", 1616, ""),
        ("Still to Be Neat", "Ben Jonson", 1609, ""),
        ("To Penshurst", "Ben Jonson", 1616, ""),
    ],

    # RESTORATION/AUGUSTAN (1660-1780)
    "Augustan": [
        ("A Satire Against Reason and Mankind", "John Wilmot, Earl of Rochester", 1679, ""),
        ("Absalom and Achitophel", "John Dryden", 1681, ""),
        ("To the Memory of Mr. Oldham", "John Dryden", 1684, ""),
        ("A Song for St. Cecilia's Day", "John Dryden", 1687, ""),
        ("The Rape of the Lock", "Alexander Pope", 1714, ""),
        ("An Essay on Criticism", "Alexander Pope", 1711, ""),
        ("An Essay on Man", "Alexander Pope", 1734, ""),
        ("Epistle to Dr. Arbuthnot", "Alexander Pope", 1735, ""),
        ("A Modest Proposal", "Jonathan Swift", 1729, ""),
        ("A Description of a City Shower", "Jonathan Swift", 1710, ""),
        ("Verses on the Death of Dr. Swift", "Jonathan Swift", 1739, ""),
        ("The Deserted Village", "Oliver Goldsmith", 1770, ""),
        ("The Vanity of Human Wishes", "Samuel Johnson", 1749, ""),
        ("Ode on the Death of a Favourite Cat", "Thomas Gray", 1748, ""),
        ("The Progress of Poesy", "Thomas Gray", 1757, ""),
        ("Elegy to the Memory of an Unfortunate Lady", "Alexander Pope", 1717, ""),
    ],

    # ROMANTIC (1780-1837)
    "Romantic": [
        ("The Tyger", "William Blake", 1794, ""),
        ("The Lamb", "William Blake", 1789, ""),
        ("London", "William Blake", 1794, ""),
        ("The Chimney Sweeper", "William Blake", 1789, ""),
        ("A Poison Tree", "William Blake", 1794, ""),
        ("The Divine Image", "William Blake", 1789, ""),
        ("I Wandered Lonely as a Cloud", "William Wordsworth", 1807, "Daffodils"),
        ("My Heart Leaps Up", "William Wordsworth", 1807, ""),
        ("Ode: Intimations of Immortality", "William Wordsworth", 1807, ""),
        ("The Solitary Reaper", "William Wordsworth", 1807, ""),
        ("The World Is Too Much With Us", "William Wordsworth", 1807, ""),
        ("Composed upon Westminster Bridge", "William Wordsworth", 1807, ""),
        ("She Dwelt Among the Untrodden Ways", "William Wordsworth", 1800, ""),
        ("Kubla Khan", "Samuel Taylor Coleridge", 1816, ""),
        ("Frost at Midnight", "Samuel Taylor Coleridge", 1798, ""),
        ("Dejection: An Ode", "Samuel Taylor Coleridge", 1802, ""),
        ("The Eolian Harp", "Samuel Taylor Coleridge", 1796, ""),
        ("Ode to a Nightingale", "John Keats", 1819, ""),
        ("To Autumn", "John Keats", 1820, ""),
        ("La Belle Dame sans Merci", "John Keats", 1820, ""),
        ("When I Have Fears That I May Cease to Be", "John Keats", 1818, ""),
        ("Ode on Melancholy", "John Keats", 1819, ""),
        ("Bright Star", "John Keats", 1838, ""),
        ("She Walks in Beauty", "Lord Byron", 1815, ""),
        ("When We Two Parted", "Lord Byron", 1816, ""),
        ("The Destruction of Sennacherib", "Lord Byron", 1815, ""),
        ("Prometheus", "Lord Byron", 1816, ""),
        ("Ode to the West Wind", "Percy Bysshe Shelley", 1820, ""),
        ("To a Skylark", "Percy Bysshe Shelley", 1820, ""),
        ("Mont Blanc", "Percy Bysshe Shelley", 1817, ""),
        ("Adonais", "Percy Bysshe Shelley", 1821, ""),
        ("England in 1819", "Percy Bysshe Shelley", 1839, ""),
    ],

    # VICTORIAN (1837-1901)
    "Victorian": [
        ("The Lady of Shalott", "Alfred Tennyson", 1832, ""),
        ("The Charge of the Light Brigade", "Alfred Tennyson", 1854, ""),
        ("Break, Break, Break", "Alfred Tennyson", 1842, ""),
        ("Tears, Idle Tears", "Alfred Tennyson", 1847, ""),
        ("Crossing the Bar", "Alfred Tennyson", 1889, ""),
        ("In Memoriam A.H.H.", "Alfred Tennyson", 1850, ""),
        ("Porphyria's Lover", "Robert Browning", 1836, ""),
        ("Fra Lippo Lippi", "Robert Browning", 1855, ""),
        ("Andrea del Sarto", "Robert Browning", 1855, ""),
        ("The Bishop Orders His Tomb", "Robert Browning", 1845, ""),
        ("Meeting at Night", "Robert Browning", 1845, ""),
        ("How Do I Love Thee?", "Elizabeth Barrett Browning", 1850, "Sonnet 43"),
        ("A Musical Instrument", "Elizabeth Barrett Browning", 1862, ""),
        ("The Runaway Slave at Pilgrim's Point", "Elizabeth Barrett Browning", 1848, ""),
        ("Remember", "Christina Rossetti", 1862, ""),
        ("When I Am Dead, My Dearest", "Christina Rossetti", 1862, ""),
        ("In an Artist's Studio", "Christina Rossetti", 1856, ""),
        ("Up-Hill", "Christina Rossetti", 1862, ""),
        ("A Birthday", "Christina Rossetti", 1862, ""),
        ("Dover Beach", "Matthew Arnold", 1867, ""),
        ("The Scholar-Gypsy", "Matthew Arnold", 1853, ""),
        ("To Marguerite—Continued", "Matthew Arnold", 1852, ""),
        ("The Buried Life", "Matthew Arnold", 1852, ""),
        ("Pied Beauty", "Gerard Manley Hopkins", 1918, ""),
        ("The Windhover", "Gerard Manley Hopkins", 1918, ""),
        ("God's Grandeur", "Gerard Manley Hopkins", 1918, ""),
        ("Spring and Fall", "Gerard Manley Hopkins", 1918, ""),
        ("As Kingfishers Catch Fire", "Gerard Manley Hopkins", 1918, ""),
        ("Because I could not stop for Death", "Emily Dickinson", 1890, ""),
        ("I heard a Fly buzz - when I died", "Emily Dickinson", 1896, ""),
        ("Wild Nights - Wild Nights!", "Emily Dickinson", 1891, ""),
        ("Hope is the thing with feathers", "Emily Dickinson", 1891, ""),
        ("There's a certain Slant of light", "Emily Dickinson", 1890, ""),
        ("The Soul selects her own Society", "Emily Dickinson", 1890, ""),
        ("A narrow Fellow in the Grass", "Emily Dickinson", 1866, ""),
        ("After great pain, a formal feeling comes", "Emily Dickinson", 1929, ""),
        ("Song of Myself", "Walt Whitman", 1855, ""),
        ("O Captain! My Captain!", "Walt Whitman", 1865, ""),
        ("I Sing the Body Electric", "Walt Whitman", 1855, ""),
        ("Crossing Brooklyn Ferry", "Walt Whitman", 1856, ""),
        ("Out of the Cradle Endlessly Rocking", "Walt Whitman", 1859, ""),
    ],

    # MODERNIST (1901-1945)
    "Modernist": [
        ("The Love Song of J. Alfred Prufrock", "T.S. Eliot", 1915, ""),
        ("The Waste Land", "T.S. Eliot", 1922, ""),
        ("The Hollow Men", "T.S. Eliot", 1925, ""),
        ("Preludes", "T.S. Eliot", 1917, ""),
        ("Journey of the Magi", "T.S. Eliot", 1927, ""),
        ("The Second Coming", "William Butler Yeats", 1920, ""),
        ("Sailing to Byzantium", "William Butler Yeats", 1928, ""),
        ("Leda and the Swan", "William Butler Yeats", 1928, ""),
        ("Among School Children", "William Butler Yeats", 1928, ""),
        ("The Wild Swans at Coole", "William Butler Yeats", 1919, ""),
        ("When You Are Old", "William Butler Yeats", 1893, ""),
        ("The Lake Isle of Innisfree", "William Butler Yeats", 1893, ""),
        ("The Road Not Taken", "Robert Frost", 1916, ""),
        ("Stopping by Woods on a Snowy Evening", "Robert Frost", 1923, ""),
        ("Mending Wall", "Robert Frost", 1914, ""),
        ("Birches", "Robert Frost", 1916, ""),
        ("After Apple-Picking", "Robert Frost", 1914, ""),
        ("Design", "Robert Frost", 1936, ""),
        ("Acquainted with the Night", "Robert Frost", 1928, ""),
        ("The Red Wheelbarrow", "William Carlos Williams", 1923, ""),
        ("This Is Just To Say", "William Carlos Williams", 1934, ""),
        ("Spring and All", "William Carlos Williams", 1923, ""),
        ("The Dance", "William Carlos Williams", 1944, ""),
        ("Sea Rose", "H.D.", 1916, ""),
        ("Helen", "H.D.", 1924, ""),
        ("The Garden", "Ezra Pound", 1916, ""),
        ("Hugh Selwyn Mauberley", "Ezra Pound", 1920, ""),
        ("The River-Merchant's Wife: A Letter", "Ezra Pound", 1915, ""),
        ("Poetry", "Marianne Moore", 1919, ""),
        ("The Fish", "Marianne Moore", 1918, ""),
        ("A Grave", "Marianne Moore", 1935, ""),
        ("Sunday Morning", "Wallace Stevens", 1923, ""),
        ("Thirteen Ways of Looking at a Blackbird", "Wallace Stevens", 1917, ""),
        ("The Emperor of Ice-Cream", "Wallace Stevens", 1923, ""),
        ("Anecdote of the Jar", "Wallace Stevens", 1919, ""),
        ("The Snow Man", "Wallace Stevens", 1921, ""),
        ("Musée des Beaux Arts", "W. H. Auden", 1940, ""),
        ("In Memory of W. B. Yeats", "W. H. Auden", 1939, ""),
        ("September 1, 1939", "W. H. Auden", 1939, ""),
        ("The Unknown Citizen", "W. H. Auden", 1940, ""),
        ("The Weary Blues", "Langston Hughes", 1926, ""),
        ("I, Too", "Langston Hughes", 1926, ""),
        ("Dream Deferred", "Langston Hughes", 1951, "Harlem"),
        ("The Dream Keeper", "Langston Hughes", 1932, ""),
        ("Mother to Son", "Langston Hughes", 1922, ""),
        ("Heritage", "Countee Cullen", 1925, ""),
        ("Incident", "Countee Cullen", 1925, ""),
    ],

    # POSTWAR (1945-1980)
    "Postwar": [
        ("The Death of the Ball Turret Gunner", "Randall Jarrell", 1945, ""),
        ("Lady Lazarus", "Sylvia Plath", 1965, ""),
        ("Ariel", "Sylvia Plath", 1965, ""),
        ("Morning Song", "Sylvia Plath", 1965, ""),
        ("Edge", "Sylvia Plath", 1965, ""),
        ("Tulips", "Sylvia Plath", 1965, ""),
        ("Mad Girl's Love Song", "Sylvia Plath", 1953, ""),
        ("Skunk Hour", "Robert Lowell", 1959, ""),
        ("For the Union Dead", "Robert Lowell", 1964, ""),
        ("Memories of West Street and Lepke", "Robert Lowell", 1959, ""),
        ("Waking in the Blue", "Robert Lowell", 1959, ""),
        ("Her Kind", "Anne Sexton", 1960, ""),
        ("The Truth the Dead Know", "Anne Sexton", 1962, ""),
        ("All My Pretty Ones", "Anne Sexton", 1962, ""),
        ("Wanting to Die", "Anne Sexton", 1966, ""),
        ("The Fish", "Elizabeth Bishop", 1946, ""),
        ("One Art", "Elizabeth Bishop", 1976, ""),
        ("In the Waiting Room", "Elizabeth Bishop", 1976, ""),
        ("The Armadillo", "Elizabeth Bishop", 1965, ""),
        ("Sestina", "Elizabeth Bishop", 1965, ""),
        ("Filling Station", "Elizabeth Bishop", 1965, ""),
        ("The Moose", "Elizabeth Bishop", 1976, ""),
        ("A Supermarket in California", "Allen Ginsberg", 1956, ""),
        ("Kaddish", "Allen Ginsberg", 1961, ""),
        ("America", "Allen Ginsberg", 1956, ""),
        ("Ego Tripping", "Nikki Giovanni", 1972, ""),
        ("The Bean Eaters", "Gwendolyn Brooks", 1960, ""),
        ("We Real Cool", "Gwendolyn Brooks", 1960, ""),
        ("The Mother", "Gwendolyn Brooks", 1945, ""),
        ("Kitchenette Building", "Gwendolyn Brooks", 1945, ""),
        ("For Malcolm X", "Margaret Walker", 1970, ""),
        ("An American Childhood", "Annie Dillard", 1987, ""),
    ],

    # CONTEMPORARY (1980-present)
    "Contemporary": [
        ("Diving into the Wreck", "Adrienne Rich", 1973, ""),
        ("Aunt Jennifer's Tigers", "Adrienne Rich", 1951, ""),
        ("Power", "Adrienne Rich", 1978, ""),
        ("The School Among the Ruins", "Adrienne Rich", 2004, ""),
        ("Wild Geese", "Mary Oliver", 1986, ""),
        ("The Summer Day", "Mary Oliver", 1990, ""),
        ("Sleeping in the Forest", "Mary Oliver", 1978, ""),
        ("The Journey", "Mary Oliver", 1986, ""),
        ("When Death Comes", "Mary Oliver", 1992, ""),
        ("In Blackwater Woods", "Mary Oliver", 1983, ""),
        ("Morning Poem", "Mary Oliver", 1994, ""),
        ("Parsley", "Rita Dove", 1983, ""),
        ("Daystar", "Rita Dove", 1986, ""),
        ("The House Slave", "Rita Dove", 1980, ""),
        ("Still I Rise", "Maya Angelou", 1978, ""),
        ("Caged Bird", "Maya Angelou", 1983, ""),
        ("A Brave and Startling Truth", "Maya Angelou", 1995, ""),
        ("The Hill We Climb", "Amanda Gorman", 2021, ""),
        ("Famous", "Naomi Shihab Nye", 1995, ""),
        ("Kindness", "Naomi Shihab Nye", 1995, ""),
        ("Gate A-4", "Naomi Shihab Nye", 2008, ""),
        ("The Writer", "Richard Wilbur", 1976, ""),
        ("Love Calls Us to the Things of This World", "Richard Wilbur", 1956, ""),
        ("Complaint", "William Carlos Williams", 1938, ""),
        ("Ode to My Socks", "Pablo Neruda", 1956, "Translation"),
        ("Tonight I Can Write", "Pablo Neruda", 1924, "Translation"),
        ("The Names", "Billy Collins", 2002, ""),
        ("Introduction to Poetry", "Billy Collins", 1988, ""),
        ("Forgetfulness", "Billy Collins", 1991, ""),
        ("The Lanyard", "Billy Collins", 2005, ""),
    ]
}

def main():
    output_file = Path("/Users/justin/Repos/AI Project/data/phase3/canonical_poems_to_classify.csv")
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Flatten the dictionary into a list
    poems_list = []
    for period, poems in CANONICAL_POEMS.items():
        for title, author, year, notes in poems:
            poems_list.append({
                'title': title,
                'author': author,
                'year_approx': year,
                'period_hint': period,
                'notes': notes,
                'classified': 'no'
            })

    # Write to CSV
    fieldnames = ['title', 'author', 'year_approx', 'period_hint', 'notes', 'classified']
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(poems_list)

    print(f"Generated {len(poems_list)} canonical poems")
    print(f"Saved to: {output_file}")
    print()

    # Show breakdown by period
    from collections import Counter
    period_counts = Counter(p['period_hint'] for p in poems_list)
    print("Breakdown by period:")
    for period, count in period_counts.most_common():
        print(f"  {period}: {count}")

    print()
    print("Next steps:")
    print("1. I'll fetch the full text for each poem")
    print("2. I'll classify each using your 52 examples as reference")
    print("3. You review and correct my classifications")

if __name__ == '__main__':
    main()
