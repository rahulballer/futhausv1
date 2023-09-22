import express from 'express';
import cors from 'cors';
import { spawn } from 'child_process';

const app = express();
app.use(cors());

app.get('/tweets', (req, res) => {
  const python = spawn('python', ['scrape_tweets.py']);

  python.stdout.on('data', data => {
    const tweets = JSON.parse(data.toString());
    res.json(tweets);
  });

  python.stderr.on('data', data => {
    console.error(data.toString());
  });
});

app.listen(3000, () => {
  console.log('Server listening on port 3000');
});