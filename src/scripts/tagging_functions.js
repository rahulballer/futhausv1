// Helper function to clean text
function cleanText(text, forRegex = false) {
    // Convert text to lowercase
    let normalizedText = text.toLowerCase();

    // Replace special characters with a regex pattern for both forms
    if (forRegex) {
        normalizedText = normalizedText.replace(/ä/g, '(a|ae)').replace(/ö/g, '(o|oe)').replace(/ü/g, '(u|ue)')
                                       .replace(/Ä/g, '(a|ae)').replace(/Ö/g, '(o|oe)').replace(/Ü/g, '(u|ue)')
                                       .replace(/ß/g, '(ss|ß)');
    } else {
        normalizedText = normalizedText.replace(/ä/g, 'ae').replace(/ö/g, 'oe').replace(/ü/g, 'ue')
                                       .replace(/Ä/g, 'ae').replace(/Ö/g, 'oe').replace(/Ü/g, 'ue')
                                       .replace(/ß/g, 'ss');
    }

    // Normalize and remove other diacritics if not already handled
    normalizedText = normalizedText.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

    // Replace hyphens with spaces
    normalizedText = normalizedText.replace(/-/g, " ");

    return normalizedText;
}

// Function to determine if a last name is unique in the dataset
function isLastNameUnique(lastName, playerClubTaggingData) {
    const allLastNames = playerClubTaggingData.map(row => {
        const names = row.person.split(' ');
        return cleanText(names[names.length - 1]);
    });
    return allLastNames.filter(name => name === lastName).length === 1;
}

// Function to check if concatenated short names are valid and return associated clubs and leagues
function checkCombinedShortNames(content, playerClubTaggingData) {
    let combinedTags = new Set();
    const shortNameRegex = /(?:#|\/)([a-zA-Z0-9]+)([a-zA-Z0-9]+)/; // Regex to capture concatenated short names with prefix

    const match = shortNameRegex.exec(content);
    if (match) {
        const combined = match[0].substring(1); // Remove the prefix (# or /) before checking

        let foundClubs = new Map();

        // Check each part of the combined short name against all short names in the dataset
        playerClubTaggingData.forEach(row => {
            if (row.short_name) {
                row.short_name.split(',').forEach(shortName => {
                    shortName = cleanText(shortName.trim());
                    if (combined.startsWith(shortName) || combined.endsWith(shortName)) {
                        foundClubs.set(shortName, { club: row.club, league: row.league });
                    }
                });
            }
        });

        // If two different clubs are found, add their tags
        if (foundClubs.size === 2) {
            foundClubs.forEach(value => {
                combinedTags.add(value.club);
                combinedTags.add(value.league);
            });
        }
    }

    return Array.from(combinedTags);
}

// Function to generate regex for tag matching with exceptions
function generateTagRegex(tag) {
    // Use only the cleaned version of the tag
    const cleanedTag = cleanText(tag);

    // Regular expression for handling prefixes and suffixes
    const prefixExceptions = ['#', '/',"(",">","<",",",".","~","`","-",,"=","+","@","&"];
    const suffixExceptions = ["'",".",",","!","/",")","?",":",";",'"',"-","=","+","@","&"];
    const prefixPattern = prefixExceptions.map(e => `\\${e}`).join('|');
    const suffixPattern = suffixExceptions.map(e => `\\${e}`).join('|');

    return new RegExp(`(?:${prefixPattern})?\\b${cleanedTag}\\b(?:${suffixPattern})?`, 'i');
}




// Function to simulate tagging logic
function tagTweet(content, playerClubTaggingData) {
    const cleanedContent = cleanText(content);
    let tags = new Set();

    for (const row of playerClubTaggingData) {
        const totalTags = row.total_tags.split(',').map(tag => cleanText(tag.trim()));
        let clubTagged = false;
        totalTags.forEach(tag => {
            const tagRegex = generateTagRegex(tag);
            if (tagRegex.test(cleanedContent)) {
                tags.add(row.club);  
                tags.add(row.league); 
                clubTagged = true;
            }
        });

        if (row.person) {
            const cleanedFullName = cleanText(row.person);
            const personNames = row.person.split(' ');
            let lastName = cleanText(personNames[personNames.length - 1]);
            if (personNames.length > 2 && personNames[personNames.length - 2].includes('-')) {
                lastName = cleanText(personNames.slice(-2).join(' '));
            }
            const isUniqueLastName = isLastNameUnique(lastName, playerClubTaggingData);
            const fullNameRegex = generateTagRegex(cleanedFullName);
            const lastNameRegex = generateTagRegex(lastName);
            if ((fullNameRegex.test(cleanedContent) && (isUniqueLastName || clubTagged)) ||
                (lastNameRegex.test(cleanedContent) && (isUniqueLastName || clubTagged))) {
                tags.add(row.person);
                tags.add(row.club);
                tags.add(row.league);
            }
        }

        // Additional logic for short names
        if (row.short_name) {
            row.short_name.split(',').forEach(shortName => {
                const tagRegex = generateTagRegex(shortName.trim());
                if (tagRegex.test(cleanedContent)) {
                    tags.add(row.club);
                    tags.add(row.league);
                }
            });
        }
    }

    // Check for concatenated short names
    const combinedTags = checkCombinedShortNames(cleanedContent, playerClubTaggingData);
    combinedTags.forEach(tag => tags.add(tag));

    return Array.from(tags);
}


// Test function for tagTweet
function testTagTweet() {
    // Example test data
    const testPlayerClubTaggingData = [
        {
            club: 'Bayer 04 Leverkusen',
            short_name: 'b04',
            league: 'Bundesliga',
            person: 'Florian Wirtz',
            total_tags: 'Bayer 04, Leverkusen, Werkself, Bayer'
        },
        {
            club: 'Bayer 04 Leverkusen',
            short_name: 'b04',
            league: 'Bundesliga',
            person: 'Victor Okoh Boniface',
            total_tags: 'Bayer 04, Leverkusen, Werkself, Bayer'
        },
        {
            club: 'Bayern München',
            short_name: 'fcb',
            league: 'Bundesliga',
            person: 'Eric Maxim Choupo-Moting',
            total_tags: 'Bayern München, Bayern Münich, miasanmia, Bayern'
        },
        {
            club: 'Bayern München',
            short_name: 'fcb',
            league: 'Bundesliga',
            person: 'Mattijs de-Ligt',
            total_tags: 'Bayern München, Bayern Münich, miasanmia, Bayern'
        },
        {
            club: 'Bayern München',
            short_name: 'fcb',
            league: 'Bundesliga',
            person: 'Thomas Müller',
            total_tags: 'Bayern München, Bayern Münich, miasanmia, Bayern'
        },
        {
            club: 'Arsenal',
            short_name: 'afc, ars',
            league: 'English Premier League',
            person: 'Gabriel Jesus',
            total_tags: 'Arsenal, Gunners, coyg'
        },
        {
            club: 'Chelsea',
            short_name: 'cfc, che',
            league: 'English Premier League',
            person: 'Gabriel Jesus',
            total_tags: 'Chelsea, the blues'
        },
        {
            club: 'FC Basel',
            short_name: 'fcb',
            league: 'Swiss League',
            person: 'Mo Salah',
            total_tags: 'basel, fcbasel'
        },
        // Add more test cases as needed
    ];

    // Example content scenarios
    const testContents = [
        'Exciting match coming up between bayer and bayern',
        'wirtz, is showing great potential this season',
        'leverkusen secures a spot in the European league',
        'wirtz getting interest from bayern and arsenal',
        'wirtz!!!',
        'choupo möting is really good',
        'choupo is on fire, so is moting',
        'choupo moting is on fire',
        'wirtz is fantastic',
        'de ligt is not leaving to arsenal',
        'ligt is on fire',
        'jesus take the wheel',
        'gabriel jesus take the wheel',
        'jesus doing well for chelsea',
        "bayern's gonna struggle without lewandowski",
        "#wirtz is amazing, so is /jesus for arsenal",
        'b04 is on fire this season', // Testing short name
        'go /fcb and #afc', // Testing combined short names
        'go #fcbafc what a game', // Testing combined short names with valid prefix
        'go #fcbafc, what a game', // Testing combined short names with valid prefix and comma
        'fcbafc is a great match', // Invalid without prefix
        '#fcbhell is not a real team', // Invalid short name combination
        '#fcbfcb is not the same team as the other team is bayern', // same short_name but 2 teams share it
        '#afcgunners is the same team', // Invalid short name combination since its coming from the same team
        'chevara', // Chelsea short name is Che, but if it's joined by another letter and without wildcard exception, it's not valid
        'Muller is amazing', // without ü
        'Mueller is amazing', // converting ü to ue
        'Müller is amazing',




        '',
        // Add more test content scenarios as needed
    ];

// Running test scenarios
testContents.forEach(content => {
    // Clean and normalize the test content without regex patterns
    const cleanedTestContent = cleanText(content, false);

    console.log(`\nTesting content: "${content}" (Cleaned: "${cleanedTestContent}")`);
    const tags = tagTweet(cleanedTestContent, testPlayerClubTaggingData);
    console.log('Generated Tags:', tags.join(', '));
});
}

// Run the test
testTagTweet();
