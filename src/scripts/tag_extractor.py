# tag_extractor.py

def keyword_matching(content, club_names, player_names):
    # Initialize tags list
    tags = []

    # Check for club name matches
    for club in club_names:
        if club.lower() in content.lower():
            tags.append(club)

    # Check for player name matches
    for player in player_names:
        if player.lower() in content.lower():
            tags.append(player)

    return ','.join(tags)  # Returns a comma-separated string of tags