const express = require('express');
const cors = require('cors');
const Twint = require('twint');

const app = express();
app.use(cors());

app.get('/tweets', (req, res) => {
  const twint = new Twint();
  twint.config = {
    username: ['fabrizioromano', 'imiasanmia'],
    tweet_mode: 'extended',
  };
  twint.run();
  const tweets = twint.storage.tweets;
  res.json(tweets);
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});